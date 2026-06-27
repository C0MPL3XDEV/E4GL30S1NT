"""Tests for eagleosint.providers.phoneinfo."""
from __future__ import annotations

from unittest.mock import MagicMock

import pytest
import requests

from eagleosint.providers.phoneinfo import PhoneInfoProvider


class TestPhoneInfoProvider:

    def _mock_response(self, data: dict):
        mock_resp = MagicMock()
        mock_resp.json.return_value = data
        mock_resp.raise_for_status.return_value = None
        return mock_resp

    def test_valid_phone_returns_result(self, monkeypatch):
        fake_data = {
            "phone": "+391234567890",
            "phone_valid": True,
            "country": "Italy",
            "country_code": "IT",
            "carrier": "Vodafone",
            "line_type": "mobile",
            "international_number": "+391234567890",
        }
        monkeypatch.setattr(
            "eagleosint.providers.phoneinfo._session.get",
            lambda *a, **kw: self._mock_response(fake_data),
        )
        provider = PhoneInfoProvider()
        results = provider.execute("+391234567890", api_key="test-key")
        assert len(results) == 1
        assert results[0].phone == "+391234567890"
        assert results[0].country == "Italy"
        assert results[0].source == "phoneinfo"

    def test_empty_query_returns_empty(self):
        provider = PhoneInfoProvider()
        assert provider.execute("", api_key="test-key") == []

    def test_missing_api_key_returns_empty(self, monkeypatch):
        from unittest.mock import MagicMock
        mock_settings = MagicMock()
        mock_settings.get_key.return_value = None
        monkeypatch.setattr(
            "eagleosint.providers.phoneinfo.settings",
            mock_settings,
        )
        provider = PhoneInfoProvider()
        assert provider.execute("+391234567890") == []

    def test_network_error_returns_empty(self, monkeypatch):
        monkeypatch.setattr(
            "eagleosint.providers.phoneinfo._session.get",
            MagicMock(side_effect=requests.exceptions.ConnectionError),
        )
        provider = PhoneInfoProvider()
        assert provider.execute("+391234567890", api_key="test-key") == []

    def test_json_error_returns_empty(self, monkeypatch):
        import json as _json
        mock_resp = MagicMock()
        mock_resp.raise_for_status.return_value = None
        mock_resp.json.side_effect = _json.JSONDecodeError("bad", "", 0)
        monkeypatch.setattr(
            "eagleosint.providers.phoneinfo._session.get",
            lambda *a, **kw: mock_resp,
        )
        provider = PhoneInfoProvider()
        assert provider.execute("+391234567890", api_key="test-key") == []