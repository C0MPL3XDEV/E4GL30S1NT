from __future__ import annotations
import logging
import threading
from getpass import getpass
from concurrent.futures import ThreadPoolExecutor
from time import sleep
from typing import Callable, ClassVar

import requests

from eagleosint.display import (
    RED, GREEN, YELLOW, BLUE, WHITE,
    SPACE_PREFIX, LINES_SEPARATOR, display_progress
)
from eagleosint.models import AccountHit, AccountStatus
from eagleosint.plugin import BaseProvider, ProviderCategory
from eagleosint.session import HEADERS, session as _session

logger = logging.getLogger(__name__)

PLATFORM_URLS = [
    "https://facebook.com/{}", "https://instagram.com/{}",
    "https://twitter.com/{}", "https://youtube.com/{}",
    "https://vimeo.com/{}", "https://github.com/{}",
    "https://plus.google.com/{}", "https://pinterest.com/{}",
    "https://flickr.com/people/{}", "https://vk.com/{}",
    "https://about.me/{}", "https://disqus.com/{}",
    "https://bitbucket.org/{}", "https://flipboard.com/@{}",
    "https://medium.com/@{}", "https://hackerone.com/{}",
    "https://keybase.io/{}", "https://buzzfeed.com/{}",
    "https://slideshare.net/{}", "https://mixcloud.com/{}",
    "https://soundcloud.com/{}", "https://badoo.com/en/{}",
    "https://imgur.com/user/{}", "https://open.spotify.com/user/{}",
    "https://pastebin.com/u/{}", "https://wattpad.com/user/{}",
    "https://canva.com/{}", "https://codecademy.com/{}",
    "https://last.fm/user/{}", "https://blip.fm/{}",
    "https://dribbble.com/{}", "https://en.gravatar.com/{}",
    "https://foursquare.com/{}", "https://creativemarket.com/{}",
    "https://ello.co/{}", "https://cash.me/{}", "https://angel.co/{}",
    "https://500px.com/{}", "https://houzz.com/user/{}",
    "https://tripadvisor.com/members/{}",
    "https://kongregate.com/accounts/{}", "https://{}.blogspot.com/",
    "https://{}.tumblr.com/", "https://{}.wordpress.com/",
    "https://{}.devianart.com/", "https://{}.slack.com/",
    "https://{}.livejournal.com/", "https://{}.newgrounds.com/",
    "https://{}.hubpages.com", "https://{}.contently.com",
    "https://steamcommunity.com/id/{}",
    "https://www.wikipedia.org/wiki/User:{}",
    "https://www.freelancer.com/u/{}", "https://www.dailymotion.com/{}",
    "https://www.etsy.com/shop/{}", "https://www.scribd.com/{}",
    "https://www.patreon.com/{}", "https://www.behance.net/{}",
    "https://www.goodreads.com/{}", "https://www.gumroad.com/{}",
    "https://www.instructables.com/member/{}",
    "https://www.codementor.io/{}", "https://www.reverbnation.com/{}",
    "https://www.designspiration.net/{}", "https://www.bandcamp.com/{}",
    "https://www.colourlovers.com/love/{}", "https://www.ifttt.com/p/{}",
    "https://www.trakt.tv/users/{}", "https://www.okcupid.com/profile/{}",
    "https://www.trip.skyscanner.com/user/{}",
    "http://www.zone-h.org/archive/notifier={}",
]

class UserReconProvider(BaseProvider):
    name = "userrecon"
    version = "1.0.0"
    description = "Username reconnaissance across 71 platforms"
    category = ProviderCategory.USERNAME

    def _check_platform(self, url_template: str, username: str) -> AccountHit:
        """Check a single platform for the username"""
        url = url_template.format(username)
        try:
            resp = _session.get(url, headers=HEADERS, timeout=10)
            resp.raise_for_status()
            status = AccountStatus.FOUND if resp.status_code == 200 else AccountStatus.NOT_FOUND
            return AccountHit(
                query=username,
                platform=url_template.split("/")[2],
                url=url,
                status=status,
                http_status_code=resp.status_code,
            )
        except requests.exceptions.HTTPError:
            return AccountHit(
                query=username,
                platform=url_template.split("/")[2],
                url=url,
                status=AccountStatus.NOT_FOUND,
                http_status_code=getattr(resp, "status_code", 0),
            )
        except requests.exceptions.RequestException:
            return AccountHit(
                query=username,
                platform=url_template.split("/")[2],
                url=url,
                status=AccountStatus.UNKNOWN,
                http_status_code=0,
            )

    def execute(
        self,
        query: str,
        max_workers: int = 20,
        delay: float = 0.7,
        on_result: Callable | None = None,
    ) -> list[AccountHit]:
        error = self.validate_query(query)
        if error:
            logger.warning("invalid query: %s", error)
            return []

        username = query.lower().strip()
        results: list[AccountHit] = []
        lock = threading.Lock()
        total = len(PLATFORM_URLS)

        def _worker(url_template: str) -> None:
            hit = self._check_platform(url_template, username)
            with lock:
                results.append(hit)
            if on_result:
                on_result(hit, len(results), total)

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            for url_template in PLATFORM_URLS:
                executor.submit(_worker, url_template)
                sleep(delay)

        return results

# ------------------------------------------------------------------
# Interactive CLI wrapper
# ------------------------------------------------------------------

def userrecon() -> list[AccountHit]:
    """Interactive CLI wrapper — prompts for username, prints progress."""
    username = input(
        f"{SPACE_PREFIX}{WHITE}{BLUE}>{WHITE} enter username:{BLUE} "
    ).lower()
    if not username:
        return []

    found_count = 0
    found_lock = threading.Lock()

    def _on_result(hit: AccountHit, current: int, total: int) -> None:
        nonlocal found_count
        if hit.status == AccountStatus.FOUND:
            color = GREEN
            with found_lock:
                found_count += 1
        elif hit.status == AccountStatus.NOT_FOUND:
            color = RED
        else:
            color = YELLOW

        display_progress(current, total, f"FOUND: {found_count}")
        print(
            f"  {SPACE_PREFIX}{BLUE}[{color}{hit.http_status_code}{BLUE}] "
            f"{current}/{total} {WHITE}{hit.url}"
        )

    print(WHITE + LINES_SEPARATOR)
    provider = UserReconProvider()
    results = provider.run(username, on_result=_on_result)

    print()
    print(WHITE + LINES_SEPARATOR)
    getpass(SPACE_PREFIX + "press enter for back to previous menu ")
    return results