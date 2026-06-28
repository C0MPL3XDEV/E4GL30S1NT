"""Tests for eagleosint.providers.mailfinder."""
from __future__ import annotations

from unittest.mock import MagicMock

import pytest
import requests

from eagleosint.providers.mailfinder import (
    MailFinderProvider, _generate_variations, EMAIL_PROVIDERS,
)
from eagleosint.models import EmailStatus


class TestGenerateVariations:

    def test_single_name_produces_variations(self):
        results = _generate_variations("john")
        assert "john" in results
        assert "john123" in results
        assert "john1234" in results

    def test_full_name_has_no_spaces(self):
        results = _generate_variations("John Doe")
        assert all(" " not in v for v in results)
        assert "johndoe" in results

    def test_leet_replacements(self):
        results = _generate_variations("alice")
        assert "al1ce" in results   # i->1
        assert "4lice" in results   # a->4
        assert "alic3" in results   # e->3


class TestMailFinderProvider:

    def _mock_response(self, category: str, status_code: int = 200):
        mock_resp = MagicMock()
        mock_resp.status_code = status_code
        mock_resp.json.return_value = {"category": category}
        return mock_resp

    def test_single_valid_email(self, monkeypatch):
        monkeypatch.setattr(
            "eagleosint.providers.mailfinder._session.post",
            lambda *a, **kw: self._mock_response("valid"),
        )
        provider = MailFinderProvider()
        result = provider._check_single("test@gmail.com", api_key="key")
        assert result.status == EmailStatus.VALID
        assert result.email == "test@gmail.com"

    def test_single_disposable_email(self, monkeypatch):
        monkeypatch.setattr(
            "eagleosint.providers.mailfinder._session.post",
            lambda *a, **kw: self._mock_response("disposable"),
        )
        provider = MailFinderProvider()
        result = provider._check_single("x@temp.com", api_key="key")
        assert result.status == EmailStatus.INVALID

    def test_single_unknown_category(self, monkeypatch):
        monkeypatch.setattr(
            "eagleosint.providers.mailfinder._session.post",
            lambda *a, **kw: self._mock_response("unknown"),
        )
        provider = MailFinderProvider()
        result = provider._check_single("x@test.com", api_key="key")
        assert result.status == EmailStatus.UNKNOWN

    def test_http_error_returns_unknown(self, monkeypatch):
        monkeypatch.setattr(
            "eagleosint.providers.mailfinder._session.post",
            lambda *a, **kw: self._mock_response("valid", status_code=429),
        )
        provider = MailFinderProvider()
        result = provider._check_single("x@test.com", api_key="key")
        assert result.status == EmailStatus.UNKNOWN

    def test_network_error_returns_unknown(self, monkeypatch):
        monkeypatch.setattr(
            "eagleosint.providers.mailfinder._session.post",
            MagicMock(side_effect=requests.exceptions.ConnectionError),
        )
        provider = MailFinderProvider()
        result = provider._check_single("x@test.com", api_key="key")
        assert result.status == EmailStatus.UNKNOWN

    def test_empty_query_returns_empty(self):
        provider = MailFinderProvider()
        assert provider.execute("") == []

    def test_execute_calls_check_for_each_email(self, monkeypatch):
        monkeypatch.setattr(
            "eagleosint.providers.mailfinder._session.post",
            lambda *a, **kw: self._mock_response("valid"),
        )
        provider = MailFinderProvider()
        results = provider.execute(
            "test", api_key="key", max_workers=2, delay=0
        )
        expected_count = len(_generate_variations("test")) * len(EMAIL_PROVIDERS)
        assert len(results) == expected_count
        assert all(r.status == EmailStatus.VALID for r in results)

    def test_on_result_callback_called(self, monkeypatch):
        monkeypatch.setattr(
            "eagleosint.providers.mailfinder._session.post",
            lambda *a, **kw: self._mock_response("valid"),
        )
        called = []
        provider = MailFinderProvider()
        provider.execute(
            "ab",
            api_key="key",
            max_workers=2,
            delay=0,
            on_result=lambda r, c, t: called.append(c),
        )
        assert len(called) > 0