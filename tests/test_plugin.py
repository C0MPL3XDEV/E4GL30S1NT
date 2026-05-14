"""Tests for BaseProvider ABC and ProviderCategory."""
import pytest
from eagleosint.plugin import BaseProvider, ProviderCategory
from eagleosint.models import ProviderResult

# --- Minimal concrete implementation for testing ---

class _DummyProvider(BaseProvider):
    name = "dummy"
    version = "0.1.0"
    description = "Dummy provider for testing purposes"
    category = ProviderCategory.UTILITY
    required_keys = ["pingutil-api-key"]

    async def execute(self, query: str) -> list[ProviderResult]:
        return []

class  _NoKeyProvider(BaseProvider):
    name = "no-key"
    category = ProviderCategory.UTILITY

    async def execute(self, query: str) -> list[ProviderResult]:
        return []

# --- Tests ---

class TestBaseProviderABC:
    def test_cannot_instantiate_abstract_class(self):
        with pytest.raises(TypeError):
            BaseProvider()  # type: ignore

    def test_concrete_subclass_instantiates(self):
        p = _DummyProvider()
        assert p.name == "dummy"

    def test_repr_contains_name_version_category(self):
        p = _DummyProvider()
        r = repr(p)
        assert "dummy" in r
        assert "0.1.0" in r
        assert "utility" in r


class TestValidateQuery:
    def test_empty_string_returns_error(self):
        p = _DummyProvider()
        assert p.validate_query("") is not None

    def test_whitespace_only_returns_error(self):
        p = _DummyProvider()
        assert p.validate_query("   ") is not None

    def test_valid_query_returns_none(self):
        p = _DummyProvider()
        assert p.validate_query("john_doe") is None

class TestIsAvailable:
    def test_no_required_keys_always_available(self):
        p = _NoKeyProvider()
        assert p.is_available() is True

    def test_missing_key_returns_false(self, monkeypatch):
        import eagleosint.config as cfg
        monkeypatch.setitem(cfg.CONFIGS, "pingutil-api-key", "")
        p = _DummyProvider()
        assert p.is_available() is False

    def test_present_key_returns_true(self, monkeypatch):
        import eagleosint.config as cfg
        monkeypatch.setitem(cfg.CONFIGS, "pingutil-api-key", "test-key-123")
        p = _DummyProvider()
        assert p.is_available() is True

class TestProviderCategory:
    def test_all_expected_categories_exist(self):
        expected = {
            "username", "email", "phone", "domain", "ip",
            "social", "breach", "image", "document",
            "dark_web", "infrastructure", "utility",
        }
        actual = {c.value for c in ProviderCategory}
        assert expected == actual