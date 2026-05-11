"""Tests for eagleosint.providers.bitly."""
from unittest.mock import MagicMock

import pytest
import requests

from eagleosint.providers.bitly import bypass_bitly


class TestBypassBitly:
    def test_invalid_url_prints_error(self, capsys, monkeypatch):
        monkeypatch.setattr("builtins.input", lambda _: "not-a-url")
        monkeypatch.setattr("eagleosint.providers.bitly.getpass", lambda _: "")
        bypass_bitly()
        captured = capsys.readouterr()
        assert "Invalid" in captured.out

    def test_valid_url_resolves(self, capsys, monkeypatch):
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

    def test_request_error_prints_message(self, capsys, monkeypatch):
        monkeypatch.setattr("builtins.input", lambda _: "https://bit.ly/abc123")
        monkeypatch.setattr(
            "eagleosint.providers.bitly._session.get",
            MagicMock(side_effect=requests.exceptions.ConnectionError),
        )
        monkeypatch.setattr("eagleosint.providers.bitly.getpass", lambda _: "")
        bypass_bitly()
        captured = capsys.readouterr()
        assert "Error" in captured.out