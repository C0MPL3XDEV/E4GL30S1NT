"""Google dorking search and result scraper."""
from __future__ import annotations
import logging
import textwrap
from getpass import getpass
from typing import Callable, ClassVar

import requests
from googlesearch import search  # type: ignore
from lxml.html import fromstring

from eagleosint.display import (
    RED, YELLOW, BLUE, WHITE, DARK_GRAY,
    BG_BLUE,
    SPACE_PREFIX, LINES_SEPARATOR,
)
from eagleosint.models import DorkResult
from eagleosint.plugin import BaseProvider, ProviderCategory
from eagleosint.session import HEADERS, session as _session

logger = logging.getLogger(__name__)

RESULTS_GODORKER_TXT = "result_godorker.txt"

class GoDorkerProvider(BaseProvider):
    name = "godorker"
    version = "1.0.0"
    description = "Google dorking search with result scraping"
    category = ProviderCategory.UTILITY

    def execute(
            self,
            query: str,
            num_results: int = 30,
            on_result: Callable | None = None,
    ) -> list[DorkResult]:
        error = self.validate_query(query)
        if error:
            logger.warning("invalid query: %s", error)
            return []

        urls: list[str] = []
        try:
            for url in search(query, num_results=num_results, timeout=5):
                urls.append(url)
        except Exception as e:
            logger.error("Google search error: %s", e)

        results: list[DorkResult] = []
        for url in urls:
            title = self._fetch_title(url)
            result = DorkResult(query=query, url=url, title=title)
            results.append(result)
            if on_result:
                on_result(result)

        return results

    def _fetch_title(self, url: str) -> str | None:
        """Fetch the page title for a URL."""
        try:
            resp = _session.get(url, headers=HEADERS, timeout=10)
            resp.raise_for_status()
            doc = fromstring(resp.content)
            return doc.findtext(".//title")
        except (requests.exceptions.RequestException, TypeError):
            logger.debug("could not fetch title for %s", url)
            return None


# ------------------------------------------------------------------
# Interactive CLI wrapper
# ------------------------------------------------------------------

def godorker() -> list[DorkResult]:
    """Interactive CLI wrapper — prompts for dork query, prints results."""
    dork_query = input(
        f"{SPACE_PREFIX}{BLUE}>{WHITE} enter dork (inurl/intext/etc):{BLUE} "
    ).lower()
    if not dork_query:
        return []

    print(WHITE + LINES_SEPARATOR)

    output_fh = open(RESULTS_GODORKER_TXT, "w", encoding="utf-8")
    output_fh.write(f"# Dork: {dork_query}\n\n")

    def _on_result(result: DorkResult) -> None:
        if result.title:
            wrapper = textwrap.TextWrapper(width=47)
            shortened = textwrap.shorten(text=result.title, width=47)
            formatted = wrapper.fill(text=shortened)
            print(
                f"{SPACE_PREFIX}{BG_BLUE} FOUND {WHITE} {formatted}\n"
                f"{SPACE_PREFIX}{DARK_GRAY}{result.url}{WHITE}"
            )
        output_fh.write(f"{result.url}\n")

    try:
        provider = GoDorkerProvider()
        results: list[DorkResult] = provider.run(dork_query, on_result=_on_result)  # type: ignore[assignment]
    except KeyboardInterrupt:
        print(f"{RED}Dorking aborted by user.{WHITE}")
        results = []
    finally:
        output_fh.close()

    print(WHITE + LINES_SEPARATOR)
    print(
        f"{SPACE_PREFIX}{BLUE}>{WHITE} {len(results)} retrieved as: "
        f"{YELLOW}{RESULTS_GODORKER_TXT}"
    )
    getpass(SPACE_PREFIX + "press enter for back to previous menu ")
    return results