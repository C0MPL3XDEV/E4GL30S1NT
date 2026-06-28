"""Bitly URL shortener bypass."""
from __future__ import annotations
import logging
import urllib.parse
from typing import ClassVar
from getpass import getpass

import requests
from bs4 import BeautifulSoup

from eagleosint.display import (
    RED, BLUE, WHITE, LIGHT_RED,
    BG_BLUE,
    SPACE_PREFIX, LINES_SEPARATOR,
)
from eagleosint.plugin import BaseProvider, ProviderCategory
from eagleosint.session import session as _session
from eagleosint.models import URLExpansion

logger = logging.getLogger(__name__)

class BitlyProvider(BaseProvider):
    name = "bitly"
    version = "1.0.0"
    description = "Resolve shortened Bitly URLs to their original destination"
    category = ProviderCategory.UTILITY
    required_keys: ClassVar[list[str]] = []

    def validate_query(self, query: str) -> str | None:
        base = super().validate_query(query)
        if base:
            return base
        parsed = urllib.parse.urlparse(query)
        if parsed.scheme not in ("http", "https") or not parsed.netloc:
            return "Invalid URL. Must start with http:// or https://"
        return None

    def execute(self, query: str) -> list[URLExpansion]:
        error = self.validate_query(query)
        if error:
            logger.warning("Invalid query: %s", error)
            return []

        try:
            response = _session.get(query, allow_redirects=False, timeout=10)
            soup = BeautifulSoup(response.text, "lxml")
            original_url = str(soup.find_all("a", href=True)[0]["href"])
        except requests.exceptions.RequestException as e:
            logger.error("Bitly fetch error: %s", e)
            return []
        except (IndexError, KeyError) as e:
            logger.error("Bitly parse error: %s", e)
            return []

        return [URLExpansion(
            query=query,
            short_url=query,
            original_url=original_url,
        )]

def bypass_bitly() -> URLExpansion | None:
    """Interactive CLI wrapper — prompts for URL, prints result."""
    print(WHITE + LINES_SEPARATOR)
    bitly_url = input(
        f"{SPACE_PREFIX}{WHITE}{BLUE}>{WHITE} Bitly URL: {BLUE}"
    ).strip()

    provider = BitlyProvider()
    results = provider.run(bitly_url)

    if not results:
        print(f"{RED}No results for '{bitly_url}'.{WHITE}")
        print(WHITE + LINES_SEPARATOR)
        getpass(SPACE_PREFIX + "press enter for back to previous menu ")
        return None

    result: URLExpansion = results[0]  # type: ignore[assignment]
    print(
        f"{SPACE_PREFIX}{BG_BLUE} DONE {WHITE} Original URL: "
        f"\u001b[38;5;32m{result.original_url}"
    )
    print(WHITE + LINES_SEPARATOR)
    getpass(SPACE_PREFIX + "press enter for back to previous menu ")
    return result