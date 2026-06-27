"""Bitly URL shortener bypass."""
import urllib.parse
from getpass import getpass

import requests
from bs4 import BeautifulSoup

from eagleosint.display import (
    RED, BLUE, WHITE, LIGHT_RED,
    BG_BLUE,
    SPACE_PREFIX, LINES_SEPARATOR,
)
from eagleosint.session import session as _session
from eagleosint.models import URLExpansion


def bypass_bitly() -> URLExpansion | None:
    """Bypasses Bitly URL shorteners."""
    print(WHITE + LINES_SEPARATOR)
    bitly_url_input = input(
        f"{SPACE_PREFIX}{WHITE}{BLUE}>{WHITE} Bitly URL: {BLUE}"
    ).strip()
    parsed = urllib.parse.urlparse(bitly_url_input)
    if parsed.scheme not in ("http", "https") or not parsed.netloc:
        print(f"{RED}Invalid URL. Must start with http:// or https://{WHITE}")
        return
    try:
        bitly_code_response = _session.get(
            bitly_url_input, allow_redirects=False, timeout=10
        )
        soup_parser = BeautifulSoup(bitly_code_response.text, "lxml")
        original_link_found = soup_parser.find_all("a", href=True)[0]["href"]
        result = URLExpansion(
            query=bitly_url_input,
            short_url=bitly_url_input,
            original_url=original_link_found,
        )
        print(
            f"{SPACE_PREFIX}{BG_BLUE} DONE {WHITE} Original URL: "
            f"\u001b[38;5;32m{original_link_found}"
        )
    except requests.exceptions.RequestException as e:
        print(f"{RED}Error fetching Bitly URL: {e}{WHITE}")
        return None
    except (IndexError, KeyError) as e:
        print(f"{RED}Error parsing Bitly response: {e}{WHITE}")
        return None
    print(WHITE + LINES_SEPARATOR)
    getpass(SPACE_PREFIX + "press enter for back to previous menu ")
    return result