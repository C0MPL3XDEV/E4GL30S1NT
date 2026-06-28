"""Tests for eagleosint.providers.userrecon."""
from __future__ import annotations

from unittest.mock import MagicMock

import pytest
import requests

from eagleosint.providers.userrecon import (
    UserReconProvider, PLATFORM_URLS,
)
from eagleosint.models import AccountStatus


class TestUserReconProvider:

    def _mock_response(self, status_code: int = 200):
        mock_resp = MagicMock()
        mock_resp.status_code = status_code
        mock_resp.raise_for_status.return_value = None
        return mock_resp

    def test_found_platform_returns_found(self, monkeypatch):
        monkeypatch.setattr(
            "eagleosint.providers.userrecon._session.get",
            lambda *a, **kw: self._mock_response(200),
        )
        provider = UserReconProvider()
        hit = provider._check_platform("https://github.com/{}", "testuser")
        assert hit.status == AccountStatus.FOUND
        assert hit.url == "https://github.com/testuser"
        assert hit.platform == "github.com"

    def test_http_error_returns_not_found(self, monkeypatch):
        mock_resp = self._mock_response(404)
        mock_resp.raise_for_status.side_effect = requests.exceptions.HTTPError
        monkeypatch.setattr(
            "eagleosint.providers.userrecon._session.get",
            lambda *a, **kw: mock_resp,
        )
        provider = UserReconProvider()
        hit = provider._check_platform("https://github.com/{}", "nouser")
        assert hit.status == AccountStatus.NOT_FOUND

    def test_connection_error_returns_unknown(self, monkeypatch):
        monkeypatch.setattr(
            "eagleosint.providers.userrecon._session.get",
            MagicMock(side_effect=requests.exceptions.ConnectionError),
        )
        provider = UserReconProvider()
        hit = provider._check_platform("https://github.com/{}", "testuser")
        assert hit.status == AccountStatus.UNKNOWN
        assert hit.http_status_code == 0

    def test_empty_query_returns_empty(self):
        provider = UserReconProvider()
        assert provider.execute("") == []

    def test_execute_returns_results_for_all_platforms(self, monkeypatch):
        monkeypatch.setattr(
            "eagleosint.providers.userrecon._session.get",
            lambda *a, **kw: self._mock_response(200),
        )
        provider = UserReconProvider()
        results = provider.execute("testuser", max_workers=5, delay=0)
        assert len(results) == len(PLATFORM_URLS)

    def test_on_result_callback_called(self, monkeypatch):
        monkeypatch.setattr(
            "eagleosint.providers.userrecon._session.get",
            lambda *a, **kw: self._mock_response(200),
        )
        called = []
        provider = UserReconProvider()
        provider.execute(
            "testuser", max_workers=5, delay=0,
            on_result=lambda hit, c, t: called.append(hit),
        )
        assert len(called) == len(PLATFORM_URLS)

    def test_platform_urls_list_not_empty(self):
        assert len(PLATFORM_URLS) == 71