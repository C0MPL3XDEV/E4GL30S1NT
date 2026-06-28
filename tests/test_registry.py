"""Tests for platform registry."""
import pytest
from pathlib import Path

from eagleosint.registry import (
    get_categories,
    get_platforms_names,
    get_url_templates,
    load_platforms,
)


class TestLoadPlatforms:
    def test_loads_default_yaml(self):
        platforms = load_platforms()
        assert len(platforms) > 0

    def test_each_platform_has_required_fields(self):
        for p in load_platforms():
            assert "name" in p, f"missing name: {p}"
            assert "url_template" in p, f"missing url_template: {p}"
            assert "category" in p, f"missing category: {p}"

    def test_url_templates_have_placeholder(self):
        for p in load_platforms():
            assert "{}" in p["url_template"], (
                f"{p['name']}: url_template must contain {{}}"
            )

    def test_no_duplicate_names(self):
        names = [p["name"] for p in load_platforms()]
        assert len(names) == len(set(names)), f"duplicate names: {[n for n in names if names.count(n) > 1]}"

    def test_custom_path(self, tmp_path):
        custom = tmp_path / "custom.yaml"
        custom.write_text(
            "platforms:\n"
            "  - name: test\n"
            "    url_template: 'https://test.com/{}'\n"
            "    category: testing\n",
            encoding="utf-8",
        )
        result = load_platforms(path=custom)
        assert len(result) == 1
        assert result[0]["name"] == "test"

    def test_invalid_path_raises(self):
        with pytest.raises(FileNotFoundError):
            load_platforms(path=Path("/nonexistent/file.yaml"))


class TestGetUrlTemplates:
    def test_returns_all(self):
        urls = get_url_templates()
        assert len(urls) == len(load_platforms())

    def test_filter_by_category(self):
        social = get_url_templates(category="social")
        assert len(social) > 0
        assert len(social) < len(get_url_templates())

    def test_nonexistent_category(self):
        assert get_url_templates(category="nonexistent") == []


class TestGetPlatformNames:
    def test_returns_all(self):
        names = get_platforms_names()
        assert "github" in names
        assert "twitter" in names

    def test_filter_by_category(self):
        dev = get_platforms_names(category="development")
        assert "github" in dev
        assert "twitter" not in dev


class TestGetCategories:
    def test_returns_sorted(self):
        cats = get_categories()
        assert cats == sorted(cats)

    def test_includes_known_categories(self):
        cats = get_categories()
        assert "social" in cats
        assert "development" in cats
        assert "music" in cats