"""Tests for eagleosint.providers.network."""
from unittest.mock import MagicMock

import pytest
import requests

from eagleosint.providers.network import (
    API_HACKERTARGET, IPINFO_API_URL,
    IPLocationProvider, DomainInfoProvider,
    iplocation, infoga,
)


class TestIPLocationProvider:

    def _mock_response(self, data: dict):
        mock_resp = MagicMock()
        mock_resp.json.return_value = data
        return mock_resp

    def test_valid_ip_returns_result(self, monkeypatch):
        fake_data = {
            "ip": "8.8.8.8", "city": "Mountain View",
            "country": "US", "loc": "37,-122",
            "org": "Google", "timezone": "America/Los_Angeles",
        }
        monkeypatch.setattr(
            "eagleosint.providers.network._session.get",
            lambda *a, **kw: self._mock_response(fake_data),
        )
        provider = IPLocationProvider()
        results = provider.execute("8.8.8.8")
        assert len(results) == 1
        assert results[0].ip == "8.8.8.8"
        assert results[0].city == "Mountain View"
        assert results[0].source == "network"

    def test_invalid_ip_returns_empty(self):
        provider = IPLocationProvider()
        assert provider.execute("not-an-ip") == []

    def test_empty_query_returns_empty(self):
        provider = IPLocationProvider()
        assert provider.execute("") == []

    def test_network_error_returns_empty(self, monkeypatch):
        monkeypatch.setattr(
            "eagleosint.providers.network._session.get",
            MagicMock(side_effect=requests.exceptions.ConnectionError),
        )
        provider = IPLocationProvider()
        assert provider.execute("8.8.8.8") == []


class TestDomainInfoProvider:

    def _mock_response(self, lines: list[bytes]):
        mock_resp = MagicMock()
        mock_resp.iter_lines.return_value = lines
        return mock_resp

    def test_valid_domain_returns_records(self, monkeypatch):
        monkeypatch.setattr(
            "eagleosint.providers.network._session.get",
            lambda *a, **kw: self._mock_response(
                [b"A 93.184.216.34", b"MX mail.example.com"]
            ),
        )
        provider = DomainInfoProvider()
        results = provider.execute("example.com", query_type="dnslookup")
        assert len(results) == 1
        assert results[0].query_type == "dnslookup"
        assert "A 93.184.216.34" in results[0].records

    def test_empty_query_returns_empty(self):
        provider = DomainInfoProvider()
        assert provider.execute("") == []

    def test_network_error_returns_empty(self, monkeypatch):
        monkeypatch.setattr(
            "eagleosint.providers.network._session.get",
            MagicMock(side_effect=requests.exceptions.ConnectionError),
        )
        provider = DomainInfoProvider()
        assert provider.execute("example.com") == []


class TestIplocationCLI:

    def test_valid_ip_prints_info(self, capsys, monkeypatch):
        mock_resp = MagicMock()
        mock_resp.json.return_value = {
            "ip": "8.8.8.8", "city": "Mountain View",
            "country": "US", "loc": "37,-122",
            "org": "Google", "timezone": "America/Los_Angeles",
        }
        monkeypatch.setattr(
            "subprocess.run", MagicMock(side_effect=FileNotFoundError)
        )
        monkeypatch.setattr("builtins.input", lambda _: "8.8.8.8")
        monkeypatch.setattr(
            "eagleosint.providers.network._session.get",
            lambda *a, **kw: mock_resp,
        )
        monkeypatch.setattr("eagleosint.providers.network.getpass", lambda _: "")
        iplocation()
        captured = capsys.readouterr()
        assert "8.8.8.8" in captured.out

    def test_invalid_ip_shows_no_results(self, capsys, monkeypatch):
        monkeypatch.setattr(
            "subprocess.run", MagicMock(side_effect=FileNotFoundError)
        )
        monkeypatch.setattr("builtins.input", lambda _: "not-an-ip")
        monkeypatch.setattr("eagleosint.providers.network.getpass", lambda _: "")
        result = iplocation()
        captured = capsys.readouterr()
        assert "No results" in captured.out
        assert result is None


class TestApiUrlTemplates:
    def test_hackertarget_url(self):
        url = API_HACKERTARGET.format("dnslookup", "example.com")
        assert url == "https://api.hackertarget.com/dnslookup/?q=example.com"

    def test_ipinfo_url(self):
        url = IPINFO_API_URL.format("1.1.1.1")
        assert url == "https://ipinfo.io/1.1.1.1/json"