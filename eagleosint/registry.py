"""Platform registry — loads platform definitions from YAML."""
from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

_REGISTRY_PATH = Path(__file__).parent / "platforms.yaml"
_cache: list[dict[str, str]] | None = None

def load_platforms(path: Path | None = None) -> list[dict[str, str]]:
    global _cache
    if _cache is not None and path is None:
        return _cache

    target = path or _REGISTRY_PATH
    with open(target, encoding="utf-8") as f:
        data: dict[str, Any] = yaml.safe_load(f)

    platforms = data.get("platforms", [])
    if path is None:
        _cache = platforms
    return platforms

def get_url_templates(category: str | None = None) -> list[str]:
    platforms = load_platforms()
    if category:
        return [p["url_template"] for p in platforms if p.get("category") == category]
    return [p["url_template"] for p in platforms]

def get_platforms_names(category: str | None = None) -> list[str]:
    platforms = load_platforms()
    if category:
        return [p["name"] for p in platforms if p.get("category") == category]
    return [p["name"] for p in platforms]

def get_categories() -> list[str]:
    platforms = load_platforms()
    return sorted(set(p.get("category", "other") for p in platforms))