"""Tests for eagleosint.providers.bitly."""
from unittest.mock import MagicMock

import pytest
import requests

from eagleosint.providers.bitly import BitlyProvider, bypass_bitly


class TestBitlyProvider:
    """Tests for the provider class (no UI)."""

    def test_valid_url_returns_expansion(self, monkeypatch):
        mock_resp = MagicMock()
        mock_resp.text = '<a href="https://example.com">click</a>'
        monkeypatch.setattr(
            "eagleosint.providers.bitly._session.get",
            lambda *a, **kw: mock_resp,
        )
        provider = BitlyProvider()
        results = provider.execute("https://bit.ly/abc123")
        assert len(results) == 1
        assert results[0].original_url == "https://example.com"
        assert results[0].short_url == "https://bit.ly/abc123"
        assert results[0].source == "bitly"

    def test_invalid_url_returns_empty(self):
        provider = BitlyProvider()
        assert provider.execute("not-a-url") == []

    def test_empty_query_returns_empty(self):
        provider = BitlyProvider()
        assert provider.execute("") == []

    def test_network_error_returns_empty(self, monkeypatch):
        monkeypatch.setattr(
            "eagleosint.providers.bitly._session.get",
            MagicMock(side_effect=requests.exceptions.ConnectionError),
        )
        provider = BitlyProvider()
        assert provider.execute("https://bit.ly/abc123") == []

    def test_parse_error_returns_empty(self, monkeypatch):
        mock_resp = MagicMock()
        mock_resp.text = "<html><body>no links here</body></html>"
        monkeypatch.setattr(
            "eagleosint.providers.bitly._session.get",
            lambda *a, **kw: mock_resp,
        )
        provider = BitlyProvider()
        assert provider.execute("https://bit.ly/abc123") == []

    def test_validate_query_rejects_bad_scheme(self):
        provider = BitlyProvider()
        assert provider.validate_query("ftp://bit.ly/abc") is not None
        assert provider.validate_query("https://bit.ly/abc") is None


class TestBypassBitly:
    """Tests for the interactive CLI wrapper."""

    def test_valid_url_prints_result(self, capsys, monkeypatch):
        mock_resp = MagicMock()
        mock_resp.text = '<a href="https://example.com">click</a>'
        monkeypatch.setattr(
            "eagleosint.providers.bitly._session.get",
            lambda *a, **kw: mock_resp,
        )
        monkeypatch.setattr("builtins.input", lambda _: "https://bit.ly/abc123")
        monkeypatch.setattr("eagleosint.providers.bitly.getpass", lambda _: "")
        bypass_bitly()
        captured = capsys.readouterr()
        assert "example.com" in captured.out

    def test_invalid_url_shows_no_results(self, capsys, monkeypatch):
        monkeypatch.setattr("builtins.input", lambda _: "not-a-url")
        monkeypatch.setattr("eagleosint.providers.bitly.getpass", lambda _: "")
        result = bypass_bitly()
        captured = capsys.readouterr()
        assert "No results" in captured.out
        assert result is None