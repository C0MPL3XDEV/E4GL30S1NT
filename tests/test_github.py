"""Tests for eagleosint.providers.github."""
import json
from unittest.mock import MagicMock, patch

import pytest

from eagleosint.providers.github import GITHUB_API_URL, github_lookup


class TestGithubLookup:
    def _mock_response(self, data: dict, status: int = 200):
        mock_resp = MagicMock()
        mock_resp.status_code = status
        mock_resp.json.return_value = data
        return mock_resp

    def test_valid_username_prints_table(self, capsys, monkeypatch):
        fake_data = {"login": "octocat", "name": "The Octocat", "public_repos": 8}
        monkeypatch.setattr(
            "eagleosint.providers.github._session.get",
            lambda *a, **kw: self._mock_response(fake_data),
        )
        monkeypatch.setattr("builtins.input", lambda _: "octocat")
        monkeypatch.setattr("eagleosint.providers.github.getpass", lambda _: "")
        github_lookup()
        captured = capsys.readouterr()
        assert "octocat" in captured.out

    def test_invalid_username_prints_error(self, capsys, monkeypatch):
        monkeypatch.setattr("builtins.input", lambda _: "!!!invalid!!!")
        github_lookup()
        captured = capsys.readouterr()
        assert "Invalid" in captured.out

    def test_api_url_template(self):
        assert GITHUB_API_URL.format("octocat") == "https://api.github.com/users/octocat"

    def test_network_error_prints_message(self, capsys, monkeypatch):
        import requests
        monkeypatch.setattr("builtins.input", lambda _: "octocat")
        monkeypatch.setattr(
            "eagleosint.providers.github._session.get",
            MagicMock(side_effect=requests.exceptions.ConnectionError),
        )
        monkeypatch.setattr("eagleosint.providers.github.getpass", lambda _: "")
        github_lookup()
        captured = capsys.readouterr()
        assert "Error" in captured.out