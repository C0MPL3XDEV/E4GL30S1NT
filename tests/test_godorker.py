"""Tests for eagleosint.providers.godorker."""
from __future__ import annotations

from unittest.mock import MagicMock

import pytest
import requests

from eagleosint.providers.godorker import GoDorkerProvider
from eagleosint.models import DorkResult


class TestGoDorkerProvider:

    def test_empty_query_returns_empty(self):
        provider = GoDorkerProvider()
        assert provider.execute("") == []

    def test_execute_returns_dork_results(self, monkeypatch):
        monkeypatch.setattr(
            "eagleosint.providers.godorker.search",
            lambda q, **kw: ["https://example.com", "https://test.com"],
        )
        mock_resp = MagicMock()
        mock_resp.content = b"<html><head><title>Example</title></head></html>"
        mock_resp.raise_for_status.return_value = None
        monkeypatch.setattr(
            "eagleosint.providers.godorker._session.get",
            lambda *a, **kw: mock_resp,
        )
        provider = GoDorkerProvider()
        results = provider.execute("inurl:test")
        assert len(results) == 2
        assert results[0].url == "https://example.com"
        assert results[0].title == "Example"
        assert results[0].source == "godorker"

    def test_search_error_returns_empty(self, monkeypatch):
        monkeypatch.setattr(
            "eagleosint.providers.godorker.search",
            MagicMock(side_effect=Exception("blocked")),
        )
        provider = GoDorkerProvider()
        results = provider.execute("inurl:test")
        assert results == []

    def test_fetch_title_failure_returns_none_title(self, monkeypatch):
        monkeypatch.setattr(
            "eagleosint.providers.godorker.search",
            lambda q, **kw: ["https://down.com"],
        )
        monkeypatch.setattr(
            "eagleosint.providers.godorker._session.get",
            MagicMock(side_effect=requests.exceptions.ConnectionError),
        )
        provider = GoDorkerProvider()
        results = provider.execute("inurl:test")
        assert len(results) == 1
        assert results[0].title is None

    def test_on_result_callback_called(self, monkeypatch):
        monkeypatch.setattr(
            "eagleosint.providers.godorker.search",
            lambda q, **kw: ["https://example.com"],
        )
        mock_resp = MagicMock()
        mock_resp.content = b"<html><head><title>T</title></head></html>"
        mock_resp.raise_for_status.return_value = None
        monkeypatch.setattr(
            "eagleosint.providers.godorker._session.get",
            lambda *a, **kw: mock_resp,
        )
        called = []
        provider = GoDorkerProvider()
        provider.execute("test", on_result=lambda r: called.append(r))
        assert len(called) == 1