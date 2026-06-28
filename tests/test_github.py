"""Tests for eagleosint.providers.github."""
import json
from unittest.mock import MagicMock, patch

import pytest

from eagleosint.providers.github import GITHUB_API_URL, GithubProvider, github_lookup


class TestGithubProvider:
    """Tests for the provider class (no UI, no input)."""

    def _mock_response(self, data: dict, status: int = 200):
        mock_resp = MagicMock()
        mock_resp.status_code = status
        mock_resp.json.return_value = data
        mock_resp.raise_for_status.return_value = None
        return mock_resp

    def test_valid_username_prints_table(self, capsys, monkeypatch):
        fake_data = {"login": "octocat", "name": "The Octocat", "public_repos": 8}
        monkeypatch.setattr(
            "eagleosint.providers.github._session.get",
            lambda *a, **kw: self._mock_response(fake_data),
        )
        provider = GithubProvider()
        results = provider.execute("octocat")
        assert len(results) == 1
        assert results[0].username == "octocat"
        assert results[0].name == "The Octocat"
        assert results[0].source == "github"

    def test_invalid_username_returns_empty(self):
        provider = GithubProvider()
        results = provider.execute("!!!invalid!!!")
        assert results == []

    def test_empty_query_returns_empty(self):
        provider = GithubProvider()
        assert provider.execute("") == []
        assert provider.execute("   ") == []

    def test_network_error_returns_empty(self, monkeypatch):
        import requests
        monkeypatch.setattr(
            "eagleosint.providers.github._session.get",
            MagicMock(side_effect=requests.exceptions.ConnectionError),
        )
        provider = GithubProvider()
        results = provider.execute("octocat")
        assert results == []

    def test_api_url_template(self):
        assert GITHUB_API_URL.format("octocat") == "https://api.github.com/users/octocat"


class TestGithubLookup:
    """Tests for the interactive CLI wrapper."""

    def _mock_response(self, data: dict, status: int = 200):
        mock_resp = MagicMock()
        mock_resp.status_code = status
        mock_resp.json.return_value = data
        mock_resp.raise_for_status.return_value = None
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

    def test_invalid_username_shows_no_results(self, capsys, monkeypatch):
        monkeypatch.setattr("builtins.input", lambda _: "!!!invalid!!!")
        monkeypatch.setattr("eagleosint.providers.github.getpass", lambda _: "")
        result = github_lookup()
        captured = capsys.readouterr()
        assert "No results" in captured.out
        assert result is None