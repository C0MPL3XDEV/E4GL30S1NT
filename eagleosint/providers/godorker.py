"""Google dorking search and result scraper."""
import textwrap
from getpass import getpass

import requests
from googlesearch import search  # type: ignore
from lxml.html import fromstring

from eagleosint.display import (
    RED, YELLOW, BLUE, WHITE, DARK_GRAY,
    BG_BLUE,
    SPACE_PREFIX, LINES_SEPARATOR,
)
from eagleosint.session import HEADERS, session as _session

RESULTS_GODORKER_TXT = "result_godorker.txt"


def godorker():
    """Performs Google dorking and saves the results to a file."""
    dork_query = input(
        f"{SPACE_PREFIX}{BLUE}>{WHITE} enter dork (inurl/intext/etc):{BLUE} "
    ).lower()
    if not dork_query:
        return
    print(WHITE + LINES_SEPARATOR)
    urls_found = []
    try:
        for result_url in search(dork_query, num_results=30, timeout=5):
            urls_found.append(result_url)
    except Exception as e_search:
        print(f"{RED}Error during Google search: {e_search}{WHITE}")

    with open(RESULTS_GODORKER_TXT, "w", encoding="utf-8") as dork_file:
        dork_file.write(f"# Dork: {dork_query}\n\n")
        for result_url in urls_found:
            try:
                req = _session.get(result_url, headers=HEADERS, timeout=10)
                req.raise_for_status()
                res_content = fromstring(req.content)
                title_text = res_content.findtext(".//title")
                if title_text:
                    wrapper = textwrap.TextWrapper(width=47)
                    dedented_text = textwrap.dedent(text=title_text)
                    original_text = wrapper.fill(text=dedented_text)
                    shortened_text = textwrap.shorten(text=original_text, width=47)
                    formatted_title = wrapper.fill(text=shortened_text)
                    dork_file.write(f"{result_url}\n")
                    print(
                        f"{SPACE_PREFIX}{BG_BLUE} FOUND {WHITE} {formatted_title}\n"
                        f"{SPACE_PREFIX}{DARK_GRAY}{result_url}{WHITE}"
                    )
            except requests.exceptions.HTTPError as http_err_dork:
                print(f"{RED}HTTP error accessing {result_url}: {http_err_dork}{WHITE}")
            except requests.exceptions.RequestException as req_err_dork:
                print(f"{RED}Request error accessing {result_url}: {req_err_dork}{WHITE}")
            except TypeError:
                print(f"{YELLOW}Could not parse title for {result_url}{WHITE}")
            except KeyboardInterrupt:
                print(f"{RED}Dorking aborted by user.{WHITE}")
                break
    print(WHITE + LINES_SEPARATOR)
    print(
        f"{SPACE_PREFIX}{BLUE}>{WHITE} {str(len(urls_found))} retrieved as: "
        f"{YELLOW}{RESULTS_GODORKER_TXT}"
    )
    getpass(SPACE_PREFIX + "press enter for back to previous menu ")