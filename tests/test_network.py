"""Tests for eagleosint.providers.network."""
from unittest.mock import MagicMock

import requests

from eagleosint.providers.network import API_HACKERTARGET, IPINFO_API_URL, infoga, iplocation


class TestIplocation:
    def test_invalid_ip_prints_error(self, capsys, monkeypatch):
        monkeypatch.setattr(
            "subprocess.run", MagicMock(side_effect=FileNotFoundError)
        )
        monkeypatch.setattr("builtins.input", lambda _: "not-an-ip")
        iplocation()
        captured = capsys.readouterr()
        assert "Invalid" in captured.out

    def test_valid_ip_calls_api(self, capsys, monkeypatch):
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


class TestApiUrlTemplates:
    def test_hackertarget_url(self):
        url = API_HACKERTARGET.format("dnslookup", "example.com")
        assert url == "https://api.hackertarget.com/dnslookup/?q=example.com"

    def test_ipinfo_url(self):
        url = IPINFO_API_URL.format("1.1.1.1")
        assert url == "https://ipinfo.io/1.1.1.1/json"