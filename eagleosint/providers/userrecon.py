import threading
from getpass import getpass
from concurrent.futures import ThreadPoolExecutor
from time import sleep

import requests

from eagleosint.config import logger
from eagleosint.display import (
    RED, GREEN, YELLOW, BLUE, WHITE,
    SPACE_PREFIX, LINES_SEPARATOR, display_progress
)
from eagleosint.session import HEADERS, session as _session

USER_RECON_NUM = 0
USER_RECON_WORKING = 0
_RECON_LOCK = threading.Lock()

def send_req(url, username):
    """Sends a request to a given URL and prints the status code."""
    try:
        req = _session.get(url.format(username), headers=HEADERS, timeout=10)
        req.raise_for_status()
    except requests.exceptions.HTTPError as http_err:
        logger.warning("HTTP error for %s: %s", url.format(username), http_err)
        print(f"{RED}HTTP error for {url.format(username)}: {http_err}{WHITE}")
        return
    except requests.exceptions.Timeout:
        logger.debug("Timeout: %s", url.format(username))
        print(f"{YELLOW}Timeout for {url.format(username)}{WHITE}")
        return
    except requests.exceptions.TooManyRedirects:
        logger.warning("Too many redirects: %s", url.format(username))
        print(f"{YELLOW}Too many redirects for {url.format(username)}{WHITE}")
        return
    except requests.exceptions.ConnectionError:
        logger.debug("Connection error: %s", url.format(username))
        print(f"{YELLOW}Connection error for {url.format(username)}{WHITE}")
        return

    global USER_RECON_NUM, USER_RECON_WORKING
    if req.status_code == 200:
        color_code = GREEN
    elif req.status_code == 404:
        color_code = RED
    else:
        color_code = YELLOW

    with _RECON_LOCK:
        USER_RECON_NUM += 1
        if req.status_code == 200:
            USER_RECON_WORKING += 1
        user_recon_num_local = USER_RECON_NUM
        user_recon_working_local = USER_RECON_WORKING

    display_progress(user_recon_num_local, 71, f"FOUND: {user_recon_working_local}")
    print(
        f"  {SPACE_PREFIX}{BLUE}[{color_code}{req.status_code}{BLUE}] "
        f"{user_recon_num_local}/71 {WHITE}{url.format(username)}"
    )

def userrecon():
    """Performs username reconnaissance across various platforms."""
    global USER_RECON_NUM, USER_RECON_WORKING
    USER_RECON_NUM = 0
    USER_RECON_WORKING = 0

    username_to_check = input(
        f"{SPACE_PREFIX}{WHITE}{BLUE}>{WHITE} enter username:{BLUE} "
    ).lower()
    if not username_to_check:
        return
    url_list = [
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

    print(WHITE + LINES_SEPARATOR)
    with ThreadPoolExecutor(max_workers=20) as executor:
        for site_url in url_list:
            executor.submit(send_req, site_url, username_to_check)
            sleep(0.7)

    print()
    print(WHITE + LINES_SEPARATOR)
    getpass(SPACE_PREFIX + "press enter for back to previous menu ")
