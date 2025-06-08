#! /usr/bin/env python3
# Authors: C0MPL3XDEV & JProgrammer-it
# Support me with follow my instagram page and github page
# Disclaimer: please dont edit or recode the original source code !
# Last update: 21/09/2021 - version 1.1
"""Simple Information Gathering Toolkit"""
import json
import os
import random
import re
import socket
import sys
import textwrap
import subprocess
from getpass import getpass
from shutil import which
from threading import Thread
from time import sleep

import requests
from bs4 import BeautifulSoup
from googlesearch import search # type: ignore
from lxml.html import fromstring
from tabulate import tabulate
import debugpy # Added debugpy import

# ANSI escape codes for colors
RED = "\033[31m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
BLUE = "\033[34m"
PURPLE = "\033[35m"
DARK_GRAY = "\033[2;37m"
WHITE = "\033[0m"
LIGHT_RED = "\u001b[38;5;196m"

# ANSI escape codes for background colors
BG_WHITE = f"{WHITE}\033[1;47m"
BG_RED = f"{WHITE}\033[1;41m"
BG_GREEN = f"{WHITE}\033[1;42m"
BG_YELLOW = f"{WHITE}\033[1;43m"
BG_BLUE = f"{WHITE}\033[1;44m"


MAIL_PRINTATE = []
# Determine the config path in the user's home directory
CONFIG_DIR_NAME = ".config"
E4GL30S1NT_CONFIG_DIR_NAME = "E4GL30S1NT"
CONFIG_FILENAME = "config.json"

CONFIG_DIR = os.path.join(os.path.expanduser("~"), CONFIG_DIR_NAME, E4GL30S1NT_CONFIG_DIR_NAME)
CONFIG_PATH = os.path.join(CONFIG_DIR, CONFIG_FILENAME)

# Create config directory and file if they do not exist
if not os.path.exists(CONFIG_DIR):
    os.makedirs(CONFIG_DIR)
if not os.path.exists(CONFIG_PATH):
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        f.write("{}\n")

with open(CONFIG_PATH, "r", encoding="utf-8") as config_file:
    CONFIGS = json.load(config_file)

HOME_DIR = os.getenv("HOME", "") # Provide a default for HOME_DIR
COOKIE_FILENAME = ".cookies"
COOKIE_FILE = os.path.join(HOME_DIR, COOKIE_FILENAME) if HOME_DIR else ""


SPACE_PREFIX = "         "
LINES_SEPARATOR = SPACE_PREFIX + "-" * 44

# API URLs and Keys
API_HACKERTARGET = "https://api.hackertarget.com/{}/?q={}"
MBASIC_FB_URL = "https://mbasic.facebook.com{}"
GRAPH_FB_URL = "https://graph.facebook.com{}"
IPINFO_API_URL = "https://ipinfo.io/{}/json"
VERIPHONE_API_BASE_URL = "https://api.veriphone.io/v2/verify"
REALEMAIL_API_URL = "https://isitarealemail.com/api/email/validate"
GITHUB_API_URL = "https://api.github.com/users/{}"
TEMPMAIL_API_URL = "https://www.1secmail.com/api/v1/"
TEMPMAIL_MAILBOX_URL = "https://www.1secmail.com/mailbox"

# Config Keys for API
REALEMAIL_API_CONFIG_KEY = "real-email-api-key"
VERIPHONE_API_CONFIG_KEY = "veriphone-api-key"

# Filenames for results
RESULTS_GODORKER_TXT = "result_godorker.txt"
RESULTS_MAILFINDER_TXT = "result_mailfinder.txt"
DUMP_IDFRIENDS_TXT = "dump_idfriends.txt"
DUMP_EMAIL_TXT = "dump_email.txt"
DUMP_PHONE_TXT = "dump_phone.txt"
DUMP_BIRTHDAY_TXT = "dump_birthday.txt"
DUMP_LOCATION_TXT = "dump_location.txt"
ALL_MAILS_DIRNAME = "All Mails"


# Global counters (handle with care, especially with threading)
USER_RECON_NUM = 0
USER_RECON_WORKING = 0
CHECK_EMAIL_NUM = 0

HEADERS = {
    "User-Agent": "Opera/9.80 (J2ME/MIDP; Opera Mini/9.80 (S60; SymbOS; Opera Mobi/23.334; U; id) Presto/2.5.25 Version/10.54"
}
LOGO = f"""{BLUE}
      .---.        .-----------
     /     \\  __  /    ------
    / /     \\(  )/    -----
   //////   ' \\/ `   ---            ┏───────────────────────────────┓
  //// / // :    : ---              │     WELCOME TO E4GL30S1NT     │
 // /   /  /`    '--                │     https://c0mpl3xdev.tk     │
//          //..\\                  │ https://JProgrammerIt.web.app │
       ====UU====UU====             └───────────────────────────────┘
           '//||\\`
             ''``
  {DARK_GRAY}Simple Information Gathering Toolkit{WHITE}
  {DARK_GRAY}Authors: {WHITE}{RED}@C0MPL3XDEV{DARK_GRAY} & {WHITE}{RED}@JProgrammer-it{WHITE}
"""


def menu():
    """Displays the main menu of the E4GL30S1NT toolkit."""
    os.system("clear")
    print(LOGO)
    print(
        f"""
         {BG_WHITE}\\033[2;30m Choose number or type exit for exiting {WHITE}

        {WHITE}{BLUE}  01{WHITE} Userrecon     {DARK_GRAY} Username reconnaissance
        {WHITE}{BLUE}  02{WHITE} Facedumper    {DARK_GRAY} Dump facebook information
        {WHITE}{BLUE}  03{WHITE} Mailfinder    {DARK_GRAY} Find email with name
        {WHITE}{BLUE}  04{WHITE} Godorker      {DARK_GRAY} Dorking with google search
        {WHITE}{BLUE}  05{WHITE} Phoneinfo     {DARK_GRAY} Phone number information
        {WHITE}{BLUE}  06{WHITE} DNSLookup     {DARK_GRAY} Domain name system lookup
        {WHITE}{BLUE}  07{WHITE} Whoislookup   {DARK_GRAY} Identify who is on domain
        {WHITE}{BLUE}  08{WHITE} Sublookup     {DARK_GRAY} Subnetwork lookup
        {WHITE}{BLUE}  09{WHITE} Hostfinder    {DARK_GRAY} Find host domain
        {WHITE}{BLUE}  10{WHITE} DNSfinder     {DARK_GRAY} Find host domain name system
        {WHITE}{BLUE}  11{WHITE} RIPlookup     {DARK_GRAY} Reverse IP lookup
        {WHITE}{BLUE}  12{WHITE} IPlocation    {DARK_GRAY} IP to location tracker
        {WHITE}{BLUE}  13{WHITE} Bitly Bypass  {DARK_GRAY} Bypass all bitly urls
        {WHITE}{BLUE}  14{WHITE} Github Lookup {DARK_GRAY} Dump GitHub information
        {WHITE}{BLUE}  15{WHITE} TempMail {DARK_GRAY}      Generate Temp Mail and Mail Box
        {WHITE}{BLUE}  00{WHITE} Exit          {DARK_GRAY} bye bye ):
        """
    )
    mainmenu()


def mainmenu():
    """Handles the main menu input and navigation."""
    fb_instance = Facebook()
    while True:
        try:
            cmd = input(f"{SPACE_PREFIX}{WHITE}{BLUE}>{WHITE} choose:{BLUE} ")
            if int(len(cmd)) < 6:
                if cmd in ("exit", "Exit", "00", "0"):
                    sys.exit(RED + SPACE_PREFIX + "* Exiting !" + WHITE)
                elif cmd in ("1", "01"):
                    userrecon()
                elif cmd in ("2", "02"):
                    fb_instance.facedumper()
                elif cmd in ("3", "03"):
                    mailfinder()
                elif cmd in ("4", "04"):
                    godorker()
                elif cmd in ("5", "05"):
                    phoneinfo()
                elif cmd in ("6", "06"):
                    infoga("dnslookup")
                elif cmd in ("7", "07"):
                    infoga("whois")
                elif cmd in ("8", "08"):
                    infoga("subnetcalc")
                elif cmd in ("9", "09"):
                    infoga("hostsearch")
                elif cmd in ("10"):
                    infoga("mtr")
                elif cmd in ("11"):
                    infoga("reverseiplookup")
                elif cmd in ("12"):
                    iplocation()
                elif cmd in ("14"):
                    github_lookup()
                elif cmd in ("13"):
                    bypass_bitly()
                elif cmd in ("15"):
                    temp_mail_gen()
            else:
                continue
        except KeyboardInterrupt:
            sys.exit(f"{RED}\n{SPACE_PREFIX}* Aborted !")


def display_progress(iteration, total, text=""):
    """Displays a progress bar in the console."""
    bar_max_width = 40
    bar_current_width = int(bar_max_width * iteration / total)
    progress_bar = "█" * bar_current_width + " " * (bar_max_width - bar_current_width)
    progress_percentage = f"{(iteration / total * 100):.1f}"
    print(
        f"{SPACE_PREFIX}{iteration}/{total} |{progress_bar}| {progress_percentage}% {text}",
        end="\r",
    )
    if iteration == total:
        print()


def send_req(url, username):
    """Sends a request to a given URL and prints the status code."""
    try:
        req = requests.get(url.format(username), headers=HEADERS, timeout=10)
        req.raise_for_status()
    except requests.exceptions.HTTPError as http_err:
        print(f"{RED}HTTP error for {url.format(username)}: {http_err}{WHITE}")
        return
    except requests.exceptions.Timeout:
        print(f"{YELLOW}Timeout for {url.format(username)}{WHITE}")
        return
    except requests.exceptions.TooManyRedirects:
        print(f"{YELLOW}Too many redirects for {url.format(username)}{WHITE}")
        return
    except requests.exceptions.ConnectionError:
        print(f"{YELLOW}Connection error for {url.format(username)}{WHITE}")
        return

    # pylint: disable=global-statement
    global USER_RECON_NUM, USER_RECON_WORKING
    USER_RECON_NUM += 1
    user_recon_num_local = USER_RECON_NUM
    user_recon_working_local = USER_RECON_WORKING

    if req.status_code == 200:
        color_code = GREEN
        USER_RECON_WORKING += 1
        user_recon_working_local = USER_RECON_WORKING
    elif req.status_code == 404:
        color_code = RED
    else:
        color_code = YELLOW

    display_progress(user_recon_num_local, 71, f"FOUND: {user_recon_working_local}")

    print(
        f"  {SPACE_PREFIX}{BLUE}[{color_code}{req.status_code}{BLUE}] {user_recon_num_local}/71 {WHITE}{url.format(username)}"
    )


def check_email(email, api, total, ok_list, output_file):
    """Checks if an email address is valid using an API."""
    # pylint: disable=global-statement
    global CHECK_EMAIL_NUM
    try:
        response = requests.get(
            REALEMAIL_API_URL,
            params={"email": email},
            headers={"Authorization": "Bearer " + api},
            timeout=10,
        )
        if response.status_code != 200:
            color_code = RED
            back_color_code = BG_RED
            status_val = f"HTTP {response.status_code}"
        else:
            try:
                status_val = response.json().get("status", "unknown")
            except json.JSONDecodeError:
                color_code = RED
                back_color_code = BG_RED
                status_val = "invalid response"
                print(
                    f"{SPACE_PREFIX}{back_color_code}{WHITE}  ERROR  {WHITE}{BLUE} "
                    f"{CHECK_EMAIL_NUM+1}/{total}{WHITE} Status: {color_code}API "
                    f"error or invalid JSON for {email}{WHITE}"
                )
                CHECK_EMAIL_NUM +=1
                return

        if status_val == "invalid":
            color_code = RED
            back_color_code = BG_RED
        elif status_val == "unknown":
            color_code = YELLOW
            back_color_code = BG_YELLOW
        elif status_val == "valid":
            color_code = GREEN
            back_color_code = BG_GREEN
        else:
            color_code = RED
            back_color_code = BG_RED

        CHECK_EMAIL_NUM += 1
        if status_val == "valid":
            ok_list.append(email)
            output_file.write(email + "\n")
            print_space_val = "  "
        else:
            print_space_val = " "

        print(
            f"{SPACE_PREFIX}{back_color_code}{WHITE}{print_space_val}{status_val.upper()}"
            f"{print_space_val}{WHITE}{BLUE} {CHECK_EMAIL_NUM}/{total}{WHITE} Status: "
            f"{color_code}{status_val}{WHITE} Email: {email}"
        )
    except requests.exceptions.RequestException as e_check_email:
        color_code = RED
        back_color_code = BG_RED
        CHECK_EMAIL_NUM += 1
        print(
            f"{SPACE_PREFIX}{back_color_code}{WHITE}  ERROR  {WHITE}{BLUE} "
            f"{CHECK_EMAIL_NUM}/{total}{WHITE} Status: {color_code}"
            f"{str(e_check_email)}{WHITE} Email: {email}"
        )


def iplocation():
    """Retrieves and displays geolocation information for an IP address."""
    try:
        process = subprocess.run(
            ["curl", "ifconfig.co", "--silent"],
            capture_output=True,
            text=True,
            check=True,
            timeout=10,
        )
        local_ip = process.stdout.strip()
        print(f"{SPACE_PREFIX}{BLUE}>{WHITE} local IP: {local_ip}")
    except subprocess.CalledProcessError as e:
        print(f"{RED}Error getting local IP: {e}{WHITE}")
        local_ip = "Unknown"
    except FileNotFoundError:
        print(f"{RED}Error: curl command not found.{WHITE}")
        local_ip = "Unknown"
    except subprocess.TimeoutExpired:
        print(f"{RED}Timeout getting local IP.{WHITE}")
        local_ip = "Unknown"

    ip_address = input(f"{SPACE_PREFIX}{BLUE}>{WHITE} enter IP:{BLUE} ")
    if not ip_address.split(".")[0].isnumeric():
        menu()
    print(WHITE + LINES_SEPARATOR)
    try:
        req = requests.get(
            IPINFO_API_URL.format(ip_address), timeout=10
        ).json()
        ip_info = f"IP: {req.get('ip', '')}"
        city_info = f"CITY: {req.get('city', '')}"
        country_info = f"COUNTRY: {req.get('country', '')}"
        loc_info = f"LOC: {req.get('loc', '')}"
        org_info = f"ORG: {req.get('org', '')}"
        tz_info = f"TIMEZONE: {req.get('timezone', '')}"
        info_list = [
            ip_info,
            city_info,
            country_info,
            loc_info,
            org_info,
            tz_info,
        ]
        for res_item in info_list:
            print(f"{SPACE_PREFIX}{BLUE}-{WHITE} {res_item}")
    except requests.exceptions.RequestException as e:
        print(f"{RED}Error fetching IP information: {e}{WHITE}")
    print(WHITE + LINES_SEPARATOR)
    getpass(SPACE_PREFIX + "press enter for back to previous menu ")
    menu()


def infoga(option):
    """Retrieves information about a domain or IP address."""
    target = input(f"{SPACE_PREFIX}{BLUE}>{WHITE} enter domain or IP:{BLUE} ")
    if not target:
        menu()
    if target.split(".")[0].isnumeric():
        try:
            target = socket.gethostbyname(target)
        except socket.gaierror as e:
            print(f"{RED}Error resolving hostname: {e}{WHITE}")
            menu()
            return
    print(WHITE + LINES_SEPARATOR)
    try:
        req = requests.get(
            API_HACKERTARGET.format(option, target), stream=True, timeout=10
        )
        for res_line in req.iter_lines():
            print(f"{SPACE_PREFIX}{BLUE}-{WHITE} {res_line.decode('utf-8')}")
    except requests.exceptions.RequestException as e:
        print(f"{RED}Error fetching information: {e}{WHITE}")
    print(WHITE + LINES_SEPARATOR)
    getpass(SPACE_PREFIX + "press enter for back to previous menu ")
    menu()


def phoneinfo():
    """Retrieves information about a phone number."""
    phone_number = input(f"{SPACE_PREFIX}{BLUE}>{WHITE} enter number:{BLUE} ")
    api_key = CONFIGS.get(VERIPHONE_API_CONFIG_KEY)
    if not api_key:
        api_key = input(
            f"{SPACE_PREFIX}{WHITE}{BLUE}>{WHITE} enter your api key (https://veriphone.io) "
            f":{BLUE} "
        )
        CONFIGS[VERIPHONE_API_CONFIG_KEY] = api_key
        with open(CONFIG_PATH, "w", encoding="utf-8") as configs_file:
            json.dump(CONFIGS, configs_file)
    if not phone_number:
        menu()
    print(WHITE + LINES_SEPARATOR)
    api_url = f"{VERIPHONE_API_BASE_URL}?phone={phone_number}&key={api_key}"
    try:
        req = requests.get(api_url, timeout=10)
        req.raise_for_status()
        res = req.json()
        for info_key, info_value in res.items():
            print(
                f"{SPACE_PREFIX}{BLUE}-{WHITE} {info_key}"
                f"{' '*(23-len(info_key))}:    {YELLOW}"
                f"{info_value}{WHITE}"
            )
    except requests.exceptions.HTTPError as http_err_phone:
        print(f"{RED}HTTP error fetching phone information: {http_err_phone}{WHITE}")
    except requests.exceptions.RequestException as e_phone:
        print(f"{RED}Error fetching phone information: {e_phone}{WHITE}")
    except json.JSONDecodeError:
        print(f"{RED}Error decoding JSON response for phone info.{WHITE}")

    print(WHITE + LINES_SEPARATOR)
    print(f"{SPACE_PREFIX}{BG_BLUE} DONE {BG_RED} {phone_number} {WHITE}")

    getpass(SPACE_PREFIX + "press enter for back to previous menu ")
    menu()


def godorker():
    """Performs Google dorking and saves the results to a file."""
    dork_query = input(
        f"{SPACE_PREFIX}{BLUE}>{WHITE} enter dork (inurl/intext/etc):{BLUE} "
    ).lower()
    if not dork_query:
        menu()
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
                req = requests.get(result_url, headers=HEADERS, timeout=10)
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
        f"{SPACE_PREFIX}{BLUE}>{WHITE} {str(len(urls_found))} retrieved as: {YELLOW}{RESULTS_GODORKER_TXT}"
    )
    getpass(SPACE_PREFIX + "press enter for back to previous menu ")
    menu()


def mailfinder():
    """Finds email addresses associated with a given name."""
    full_name = input(f"{SPACE_PREFIX}{BLUE}>{WHITE} enter name:{BLUE} ").lower()
    if not full_name:
        menu()
    email_providers = [
        "gmail.com", "yahoo.com", "hotmail.com", "aol.com", "msn.com",
        "comcast.net", "live.com", "rediffmail.com", "ymail.com",
        "outlook.com", "cox.net", "googlemail.com", "rocketmail.com",
        "att.net", "facebook.com", "bellsouth.net", "charter.net", "sky.com",
        "earthlink.net", "optonline.net", "qq.com", "me.com", "gmx.net",
        "mail.com", "ntlworld.com", "frontiernet.net", "windstream.net",
        "mac.com", "centurytel.net", "aim.com",
    ]
    user_variations = [
        full_name.replace(" ", ""), full_name.replace(" ", "") + "123",
        full_name.replace(" ", "") + "1234", full_name.replace("i", "1"),
        full_name.replace("a", "4"), full_name.replace("e", "3"),
        full_name.replace("i", "1").replace("a", "4").replace("e", "3"),
        full_name.replace("i", "1").replace("a", "4"),
        full_name.replace("i", "1").replace("e", "3"),
        full_name.replace("a", "4").replace("e", "3"),
    ]

    name_parts = []
    for name_part in full_name.split(" "):
        user_variations.append(name_part)
        user_variations.append(name_part + "123")
        user_variations.append(name_part + "1234")
        name_parts.append(name_part)

    with open(RESULTS_MAILFINDER_TXT, "w", encoding="utf-8") as mail_file:
        valid_emails = []
        try:
            api_key = CONFIGS.get(REALEMAIL_API_CONFIG_KEY)
            if not api_key:
                api_key = input(
                    f"{SPACE_PREFIX}{WHITE}{BLUE}>{WHITE} enter your api key (https://isitarealemail.com) :{BLUE} "
                )
                CONFIGS[REALEMAIL_API_CONFIG_KEY] = api_key
                with open(CONFIG_PATH, "w", encoding="utf-8") as cf_file:
                    json.dump(CONFIGS, cf_file)
            print(WHITE + LINES_SEPARATOR)
            threads = []
            global CHECK_EMAIL_NUM
            CHECK_EMAIL_NUM = 0

            for user_variation in user_variations:
                for provider_domain in email_providers:
                    email_address = f"{user_variation}@{provider_domain}"
                    thread = Thread(
                        target=check_email,
                        args=(
                            email_address,
                            api_key,
                            len(email_providers) * len(user_variations),
                            valid_emails,
                            mail_file,
                        ),
                    )
                    threads.append(thread)
                    thread.start()
                    sleep(0.20)

            for t_item in threads:
                t_item.join()

            CHECK_EMAIL_NUM = 0

        except KeyboardInterrupt:
            print("ERROR")
            print(f"\r{RED}{SPACE_PREFIX}* Operation aborted by user.{WHITE}")
    print(WHITE + LINES_SEPARATOR)
    print(
        f"{SPACE_PREFIX}{BLUE}>{WHITE} {str(len(valid_emails))} retrieved as: {YELLOW}{RESULTS_MAILFINDER_TXT}"
    )
    getpass(SPACE_PREFIX + "press enter for back to previous menu ")
    menu()


def userrecon():
    """Performs username reconnaissance across various platforms."""
    global USER_RECON_NUM, USER_RECON_WORKING
    USER_RECON_NUM = 0
    USER_RECON_WORKING = 0

    username_to_check = input(
        f"{SPACE_PREFIX}{WHITE}{BLUE}>{WHITE} enter username:{BLUE} "
    ).lower()
    if not username_to_check:
        menu()
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
    threads = []
    for site_url in url_list:
        thread = Thread(target=send_req, args=(site_url, username_to_check))
        threads.append(thread)
        thread.start()
        sleep(0.7)

    for t_item in threads:
        t_item.join()

    print()
    print(WHITE + LINES_SEPARATOR)
    getpass(SPACE_PREFIX + "press enter for back to previous menu ")
    menu()


def bypass_bitly():
    """Bypasses Bitly URL shorteners."""
    print(WHITE + LINES_SEPARATOR)
    bitly_url_input = input(f"{SPACE_PREFIX}{WHITE}{BLUE}>{WHITE} Bitly URL: {BLUE}")
    try:
        bitly_code_response = requests.get(
            bitly_url_input, allow_redirects=False, timeout=10
        )
        soup_parser = BeautifulSoup(bitly_code_response.text, "lxml")
        original_link_found = soup_parser.find_all("a", href=True)[0]["href"]
        print(
            f"{SPACE_PREFIX}{BG_BLUE} DONE {WHITE} Original URL: \u001b[38;5;32m{original_link_found}"
        )
    except requests.exceptions.RequestException as e:
        print(f"{RED}Error fetching Bitly URL: {e}{WHITE}")
    except (IndexError, KeyError) as e:
        print(f"{RED}Error parsing Bitly response: {e}{WHITE}")
    print(WHITE + LINES_SEPARATOR)
    getpass(SPACE_PREFIX + "press enter for back to previous menu ")
    menu()


def github_lookup():
    """Retrieves and displays information about a GitHub user."""
    print(WHITE + LINES_SEPARATOR)
    github_user = input(
        f"{SPACE_PREFIX}{WHITE}{BLUE}>{WHITE} Github username: {BLUE}"
    )
    print(WHITE)
    try:
        req = requests.get(
            GITHUB_API_URL.format(github_user), timeout=10
        )
        res_data = req.json()
        table_formatted_data = []
        for info_key, info_value in res_data.items():
            table_formatted_data.append([str(info_key), str(info_value)])
        table_headers_list = ["info", "content"]
        for line_item in tabulate(
            table_formatted_data,
            headers=table_headers_list,
            tablefmt="fancy_grid",
        ).splitlines():
            print(" " * int(len(SPACE_PREFIX) / 2) + line_item)
    except requests.exceptions.RequestException as e:
        print(f"{RED}Error fetching GitHub user information: {e}{WHITE}")
    except json.JSONDecodeError:
        print(f"{RED}Error decoding JSON response from GitHub.{WHITE}")
    print(WHITE + LINES_SEPARATOR)
    getpass(SPACE_PREFIX + "press enter for back to previous menu ")
    menu()


class Facebook:
    """A class for interacting with Facebook data."""

    def __init__(self):
        self.cookies = self._load_cookies()

    def _load_cookies(self):
        """Loads Facebook cookies from file."""
        try:
            with open(COOKIE_FILE, "r", encoding="utf-8") as cf:
                return {"cookie": cf.read().strip()}
        except FileNotFoundError:
            return self._prompt_for_cookies()

    def _prompt_for_cookies(self):
        """Prompts the user to enter Facebook cookies."""
        while True:
            coki_input = getpass(
                f"{SPACE_PREFIX}{BLUE}>{WHITE} enter facebook cookies (hidden input): "
            )
            if coki_input:
                with open(COOKIE_FILE, "w", encoding="utf-8") as cf:
                    cf.write(coki_input)
                return {"cookie": coki_input}

    def user_token(self):
        """Retrieves a Facebook user token."""
        try:
            response = requests.get(
                "https://m.facebook.com/composer/ocelot/async_loader/?publisher=feed#_=_",
                headers=HEADERS,
                cookies=self.cookies,
                timeout=10,
            )
            response.raise_for_status()
            find_token_match = re.search(r"(EAAA\w+)", response.text)
            if find_token_match is None:
                sys.exit(RED + "[!] failed to get session token" + WHITE)
            return find_token_match.group(1)
        except requests.exceptions.RequestException as e:
            sys.exit(f"{RED}[!] Error fetching token: {e}{WHITE}")
        return None

    def facedumper(self):
        """Dumps Facebook information based on user choice."""
        try:
            req_content = requests.get(
                MBASIC_FB_URL.format("/me"), cookies=self.cookies, timeout=10
            ).content
            if b"mbasic_logout_button" in req_content:
                if b"Apa yang Anda pikirkan sekarang" not in req_content:
                    try:
                        bs_parser = BeautifulSoup(req_content, "html.parser")
                        lang_link = bs_parser.find("a", string="Bahasa Indonesia")
                        if lang_link and lang_link.get("href"):
                            requests.get(
                                MBASIC_FB_URL.format(lang_link["href"]),
                                cookies=self.cookies,
                                timeout=10,
                            )
                        follow_page_bs = BeautifulSoup(
                            requests.get(
                                MBASIC_FB_URL.format("/termuxhackers.id"), cookies=self.cookies, timeout=10
                            ).content,
                            "html.parser",
                        )
                        follow_link = follow_page_bs.find("a", string="Ikuti")
                        if follow_link and follow_link.get("href"):
                            session = requests.Session()
                            session.get(
                                MBASIC_FB_URL.format(follow_link["href"]),
                                cookies=self.cookies,
                                timeout=10,
                            )
                    except requests.exceptions.RequestException:
                        pass
            else:
                sys.exit(RED + "* invalid credentials: cookies" + WHITE)
        except requests.exceptions.RequestException as e:
            sys.exit(f"{RED}Error during Facebook check: {e}{WHITE}")

        print(
            f"""
        {WHITE}{BLUE}  01{WHITE} Dump all     {DARK_GRAY} Dump all info from friendlist
        {WHITE}{BLUE}  02{WHITE} Dump uid     {DARK_GRAY} Dump user id from friendlist
        {WHITE}{BLUE}  03{WHITE} Dump email   {DARK_GRAY} Dump email from friendlist
        {WHITE}{BLUE}  04{WHITE} Dump phone   {DARK_GRAY} Dump phone from friendlist
        {WHITE}{BLUE}  05{WHITE} Dump birthday{DARK_GRAY} Dump birthday from friendlist
        {WHITE}{BLUE}  06{WHITE} Dump location{DARK_GRAY} Dump location from friendlist
        """
        )
        while True:
            user_choice = input(f"{SPACE_PREFIX}{WHITE}{BLUE}>{WHITE} choose: {BLUE}")
            if not user_choice:
                menu()
            elif user_choice in ("1", "01"):
                self.dump_all()
            elif user_choice in ("2", "02"):
                self.dump_id()
            elif user_choice in ("3", "03"):
                self.dump_email()
            elif user_choice in ("4", "04"):
                self.dump_phone()
            elif user_choice in ("5", "05"):
                self.dump_birthday()
            elif user_choice in ("6", "06"):
                self.dump_location()
            else:
                continue

    def dump_all(self):
        """Dumps all available information from the friend list."""
        token = self.user_token()
        if not token:
            return
        try:
            req = requests.get(
                GRAPH_FB_URL.format(
                    f"/v3.2/me/friends/?fields=name,email&access_token={token}&limit=5000"
                ),
                headers=HEADERS,
                timeout=10,
            )
            req.raise_for_status()
            res_data = req.json()
            print(WHITE + LINES_SEPARATOR)
            counter = 0
            for data_item_info in res_data.get("data", []):
                counter += 1
                try:
                    req_friend = requests.get(
                        GRAPH_FB_URL.format(
                            f"/{data_item_info['id']}?access_token={token}&limit=5000"
                        ),
                        headers=HEADERS,
                        timeout=10,
                    )
                    req_friend.raise_for_status()
                    res_friend_data = req_friend.json()
                    friend_id_val = data_item_info.get("id")
                    friend_name_val = data_item_info.get("name")
                    print(f"{SPACE_PREFIX}{BG_BLUE} DONE {BG_RED} {str(counter)} {WHITE}")
                    if friend_name_val:
                        print(f"{SPACE_PREFIX}{BLUE}-{WHITE} Name: {friend_name_val}")
                    if friend_id_val:
                        print(f"{SPACE_PREFIX}{BLUE}-{WHITE} ID: {friend_id_val}")
                    if res_friend_data.get('email'):
                        print(f"{SPACE_PREFIX}{BLUE}-{WHITE} Email: {res_friend_data['email']}")
                    if res_friend_data.get('phone'):
                        print(f"{SPACE_PREFIX}{BLUE}-{WHITE} Phone: {res_friend_data['phone']}")
                    if res_friend_data.get('birthday'):
                        print(f"{SPACE_PREFIX}{BLUE}-{WHITE} Birthday: {res_friend_data['birthday']}")
                    if res_friend_data.get('location', {}).get('name'):
                        print(f"{SPACE_PREFIX}{BLUE}-{WHITE} Location: {res_friend_data['location']['name']}")
                except requests.exceptions.RequestException as e_friend:
                    print(f"{RED}Error fetching friend data: {e_friend}{WHITE}")
                except json.JSONDecodeError:
                    print(f"{RED}Error decoding friend data.{WHITE}")
                except KeyboardInterrupt:
                    break
        except requests.exceptions.RequestException as e:
            print(f"{RED}Error fetching friend list: {e}{WHITE}")
        except json.JSONDecodeError:
            print(f"{RED}Error decoding friend list response.{WHITE}")
        print(WHITE + LINES_SEPARATOR)
        getpass(SPACE_PREFIX + "press enter for back to previous menu ")
        menu()

    def dump_id(self):
        """Dumps Facebook user IDs from the friend list."""
        token = self.user_token()
        if not token:
            return
        try:
            req = requests.get(
                GRAPH_FB_URL.format(
                    f"/v3.2/me/friends/?fields=name,email&access_token={token}&limit=5000"
                ),
                headers=HEADERS,
                timeout=10,
            )
            req.raise_for_status()
            res_data = req.json()
            id_list = []
            print(WHITE + LINES_SEPARATOR)
            with open(DUMP_IDFRIENDS_TXT, "w", encoding="utf-8") as id_file:
                try:
                    for data_item_info in res_data.get("data", []):
                        try:
                            id_val = data_item_info.get("id")
                            name_val = data_item_info.get("name")
                            if id_val and name_val:
                                print(f"{SPACE_PREFIX}{BG_BLUE} DONE {WHITE} ID: {id_val} {RED}->{WHITE} {name_val}")
                                id_list.append(id_val)
                                id_file.write(f"{id_val}|{name_val}\n")
                        except KeyboardInterrupt:
                            break
                except KeyboardInterrupt:
                    pass
        except requests.exceptions.RequestException as e:
            print(f"{RED}Error fetching friend IDs: {e}{WHITE}")
        except json.JSONDecodeError:
            print(f"{RED}Error decoding friend ID response.{WHITE}")
        finally:
            if 'id_file' in locals() and not id_file.closed:
                id_file.close()

        print(WHITE + LINES_SEPARATOR)
        print(
            f"{SPACE_PREFIX}{BLUE}>{WHITE} {str(len(id_list))} retrieved as: {YELLOW}{DUMP_IDFRIENDS_TXT}"
        )
        getpass(SPACE_PREFIX + "press enter for back to previous menu ")
        menu()

    def dump_email(self):
        """Dumps email addresses from the friend list."""
        token = self.user_token()
        if not token:
            return
        try:
            req = requests.get(
                GRAPH_FB_URL.format(
                    f"/v3.2/me/friends/?fields=name,email&access_token={token}&limit=5000"
                ),
                headers=HEADERS,
                timeout=10,
            )
            req.raise_for_status()
            res_data = req.json()
            email_list = []
            print(WHITE + LINES_SEPARATOR)
            with open(DUMP_EMAIL_TXT, "w", encoding="utf-8") as email_file:
                try:
                    for data_item_info in res_data.get("data", []):
                        try:
                            req_friend_email = requests.get(
                                GRAPH_FB_URL.format(
                                    f"/{data_item_info['id']}?access_token={token}&limit=5000"
                                ),
                                headers=HEADERS,
                                timeout=10,
                            )
                            req_friend_email.raise_for_status()
                            res_friend_email_data = req_friend_email.json()
                            name_val = res_friend_email_data.get("name")
                            email_val = res_friend_email_data.get("email")
                            friend_id_val = res_friend_email_data.get("id")
                            if name_val and email_val and friend_id_val:
                                print(
                                    f"{SPACE_PREFIX}{BG_BLUE} DONE {WHITE} Email: {email_val} {RED}->{WHITE} {name_val}"
                                )
                                email_list.append(email_val)
                                email_file.write(f"{email_val}|{friend_id_val}|{name_val}\n")
                        except requests.exceptions.RequestException:
                            continue
                        except json.JSONDecodeError:
                            continue
                        except KeyboardInterrupt:
                            break
                except KeyboardInterrupt:
                    pass
        except requests.exceptions.RequestException as e:
            print(f"{RED}Error fetching email list: {e}{WHITE}")
        except json.JSONDecodeError:
            print(f"{RED}Error decoding email list response.{WHITE}")
        finally:
            if 'email_file' in locals() and not email_file.closed:
                email_file.close()
        print(WHITE + LINES_SEPARATOR)
        print(f"{SPACE_PREFIX}{BLUE}>{WHITE} {str(len(email_list))} retrieved as: {YELLOW}{DUMP_EMAIL_TXT}")
        getpass(SPACE_PREFIX + "press enter for back to previous menu ")
        menu()

    def dump_phone(self):
        """Dumps phone numbers from the friend list."""
        token = self.user_token()
        if not token:
            return
        try:
            req = requests.get(
                GRAPH_FB_URL.format(
                    f"/v3.2/me/friends/?fields=name,email&access_token={token}&limit=5000"
                ),
                headers=HEADERS,
                timeout=10,
            )
            req.raise_for_status()
            res_data = req.json()
            phone_list = []
            print(WHITE + LINES_SEPARATOR)
            with open(DUMP_PHONE_TXT, "w", encoding="utf-8") as phone_file:
                try:
                    for data_item_info in res_data.get("data", []):
                        try:
                            req_friend_phone = requests.get(
                                GRAPH_FB_URL.format(
                                    f"/{data_item_info['id']}?access_token={token}&limit=5000"
                                ),
                                headers=HEADERS,
                                timeout=10,
                            )
                            req_friend_phone.raise_for_status()
                            res_friend_phone_data = req_friend_phone.json()
                            name_val = res_friend_phone_data.get("name")
                            phone_val = res_friend_phone_data.get("mobile_phone")
                            friend_id_val = res_friend_phone_data.get("id")
                            if name_val and phone_val and friend_id_val:
                                print(
                                    f"{SPACE_PREFIX}{BG_BLUE} DONE {WHITE} Phone: {phone_val} {RED}->{WHITE} {name_val}"
                                )
                                phone_list.append(phone_val)
                                phone_file.write(f"{phone_val}|{friend_id_val}|{name_val}\n")
                        except requests.exceptions.RequestException:
                            continue
                        except json.JSONDecodeError:
                            continue
                        except KeyboardInterrupt:
                            break
                except KeyboardInterrupt:
                    pass
        except requests.exceptions.RequestException as e:
            print(f"{RED}Error fetching phone list: {e}{WHITE}")
        except json.JSONDecodeError:
            print(f"{RED}Error decoding phone list response.{WHITE}")
        finally:
            if 'phone_file' in locals() and not phone_file.closed:
                phone_file.close()
        print(WHITE + LINES_SEPARATOR)
        print(
            f"{SPACE_PREFIX}{BLUE}>{WHITE} {str(len(phone_list))} retrieved as: {YELLOW}{DUMP_PHONE_TXT}"
        )
        getpass(SPACE_PREFIX + "press enter for back to previous menu ")
        menu()

    def dump_birthday(self):
        """Dumps birthdays from the friend list."""
        token = self.user_token()
        if not token:
            return
        try:
            req = requests.get(
                GRAPH_FB_URL.format(
                    f"/v3.2/me/friends/?fields=name,email&access_token={token}&limit=5000"
                ),
                headers=HEADERS,
                timeout=10,
            )
            req.raise_for_status()
            res_data = req.json()
            birthday_list = []
            print(WHITE + LINES_SEPARATOR)
            with open(DUMP_BIRTHDAY_TXT, "w", encoding="utf-8") as birthday_file:
                try:
                    for data_item_info in res_data.get("data", []):
                        try:
                            req_friend_bday = requests.get(
                                GRAPH_FB_URL.format(
                                    f"/{data_item_info['id']}?access_token={token}&limit=5000"
                                ),
                                headers=HEADERS,
                                timeout=10,
                            )
                            req_friend_bday.raise_for_status()
                            res_friend_bday_data = req_friend_bday.json()
                            name_val = res_friend_bday_data.get("name")
                            day_val = res_friend_bday_data.get("birthday")
                            friend_id_val = res_friend_bday_data.get("id")
                            if name_val and day_val and friend_id_val:
                                print(
                                    f"{SPACE_PREFIX}{BG_BLUE} DONE {WHITE} Birthday: {day_val} {RED}->{WHITE} {name_val}"
                                )
                                birthday_list.append(day_val)
                                birthday_file.write(f"{day_val}|{friend_id_val}|{name_val}\n")
                        except requests.exceptions.RequestException:
                            continue
                        except json.JSONDecodeError:
                            continue
                        except KeyboardInterrupt:
                            break
                except KeyboardInterrupt:
                    pass
        except requests.exceptions.RequestException as e:
            print(f"{RED}Error fetching birthday list: {e}{WHITE}")
        except json.JSONDecodeError:
            print(f"{RED}Error decoding birthday list response.{WHITE}")
        finally:
            if 'birthday_file' in locals() and not birthday_file.closed:
                birthday_file.close()
        print(WHITE + LINES_SEPARATOR)
        print(
            f"{SPACE_PREFIX}{BLUE}>{WHITE} {str(len(birthday_list))} retrieved as: {YELLOW}{DUMP_BIRTHDAY_TXT}"
        )
        getpass(SPACE_PREFIX + "press enter for back to previous menu ")
        menu()

    def dump_location(self):
        """Dumps locations from the friend list."""
        token = self.user_token()
        if not token:
            return
        try:
            req = requests.get(
                GRAPH_FB_URL.format(
                    f"/v3.2/me/friends/?fields=name,email&access_token={token}&limit=5000"
                ),
                headers=HEADERS,
                timeout=10,
            )
            req.raise_for_status()
            res_data = req.json()
            location_list = []
            print(WHITE + LINES_SEPARATOR)
            with open(DUMP_LOCATION_TXT, "w", encoding="utf-8") as location_file:
                try:
                    for data_item_info in res_data.get("data", []):
                        try:
                            req_friend_loc = requests.get(
                                GRAPH_FB_URL.format(
                                    f"/{data_item_info['id']}?access_token={token}&limit=5000"
                                ),
                                headers=HEADERS,
                                timeout=10,
                            )
                            req_friend_loc.raise_for_status()
                            res_friend_loc_data = req_friend_loc.json()
                            name_val = res_friend_loc_data.get("name")
                            loc_val = res_friend_loc_data.get("location", {}).get("name")
                            friend_id_val = res_friend_loc_data.get("id")
                            if name_val and loc_val and friend_id_val:
                                location_file.write(f"{loc_val}|{friend_id_val}|{name_val}\n")
                                location_list.append(loc_val)
                                print(
                                    f"{SPACE_PREFIX}{BG_BLUE} DONE {WHITE} Location: {loc_val} {RED}->{WHITE} {name_val}"
                                )
                        except requests.exceptions.RequestException:
                            continue
                        except json.JSONDecodeError:
                            continue
                        except KeyboardInterrupt:
                            break
                except KeyboardInterrupt:
                    pass
        except requests.exceptions.RequestException as e:
            print(f"{RED}Error fetching location list: {e}{WHITE}")
        except json.JSONDecodeError:
            print(f"{RED}Error decoding location list response.{WHITE}")
        finally:
            if 'location_file' in locals() and not location_file.closed:
                location_file.close()
        print(WHITE + LINES_SEPARATOR)
        print(
            f"{SPACE_PREFIX}{BLUE}>{WHITE} {str(len(location_list))} retrieved as: {YELLOW}{DUMP_LOCATION_TXT}"
        )
        getpass(SPACE_PREFIX + "press enter for back to previous menu ")
        menu()


def settings():
    """Allows the user to change settings in the config file."""
    os.system("clear")
    print(
        f"""{RED}
      .---.        .-----------
     /     \\  __  /    ------
    / /     \\(  )/    -----
   //////   ' \\/ `   ---            ┏───────────────────────────────┓
  //// / // :    : ---              │     WELCOME TO E4GL30S1NT     │
 // /   /  /`    '--                │    {LIGHT_RED}https://c0mpl3x.web.app/{RED}   │
//          //..\\                   │ {LIGHT_RED}https://JProgrammerIt.web.app{RED} │
       ====UU====UU====             └───────────────────────────────┘
           '//||\\`
             ''``
  {LIGHT_RED}Simple Information Gathering Toolkit{WHITE}
  {LIGHT_RED}Authors: {WHITE}{RED}@C0MPL3XDEV{LIGHT_RED} & {WHITE}{RED}@JProgrammer-it{WHITE}
"""
    )
    print(
        f"""\
         {WHITE}{BG_RED} \\033[1mSETTINGS CHANGER MODE {WHITE}
"""
    )
    setting_counter = 0
    config_options = {}
    for setting_key_name, setting_value_item in CONFIGS.items():
        if setting_key_name != "headers":
            setting_counter += 1
            config_options[str(setting_counter)] = setting_key_name
            print(
                f"         {WHITE}{RED}  0{setting_counter} {setting_key_name}"
                + " " * (20 - len(setting_key_name))
                + f'{LIGHT_RED}:  "{setting_value_item}" '
            )
    exit_option_key = "exit".upper()
    print(
        f"         {WHITE}{RED}  00{RED} {exit_option_key}"
        + " " * (20 - len(exit_option_key))
        + f"{LIGHT_RED}:  bye bye ): "
    )

    chosen_option = ""
    while chosen_option not in config_options:
        chosen_option = input(
            f"{SPACE_PREFIX}{LIGHT_RED}>{RED} What do you want to change?{LIGHT_RED} "
        )
        if chosen_option in ("0", "00"):
            sys.exit()

    new_setting_value = input(
        f"{SPACE_PREFIX}{LIGHT_RED}>{RED} Insert the new value of {config_options[chosen_option]} :{LIGHT_RED} "
    )
    CONFIGS[config_options[chosen_option]] = new_setting_value
    with open(CONFIG_PATH, "w", encoding="utf-8") as configs_file_to_write:
        json.dump(CONFIGS, configs_file_to_write)


def temp_mail_gen():
    """Generates a temporary email address and checks for incoming mail."""
    temp_api_url = TEMPMAIL_API_URL
    domain_choices = ["1secmail.com", "1secmail.net", "1secmail.org"]
    chosen_domain = random.choice(domain_choices)

    _new_mail_url_local = ""

    def extract_mail_details_nested(mail_url_to_extract):
        """Extracts username and domain from the mail URL."""
        username_match = re.search(r"login=(.*)&", mail_url_to_extract)
        domain_match = re.search(r"domain=(.*)", mail_url_to_extract)
        if username_match and domain_match:
            return [username_match.group(1), domain_match.group(1)]
        return [None, None]

    # pylint: disable=possibly-unused-variable
    def delete_temp_mail_nested(current_mail_address, mail_url_for_delete):
        """Deletes the temporary email address."""
        delete_url = TEMPMAIL_MAILBOX_URL
        extracted_details = extract_mail_details_nested(mail_url_for_delete)
        if extracted_details[0] and extracted_details[1]:
            delete_data = {
                "action": "deleteMailbox",
                "login": extracted_details[0],
                "domain": extracted_details[1],
            }
            print(f"Disposing your email address - {current_mail_address}\n")
            try:
                requests.post(delete_url, data=delete_data, timeout=10)
            except requests.exceptions.RequestException as e_delete:
                print(f"{RED}Error deleting email: {e_delete}{WHITE}")

    def check_temp_mails_nested(mail_url_to_check):
        """Checks for new emails in the temporary mailbox."""
        extracted_details = extract_mail_details_nested(mail_url_to_check)
        if not (extracted_details[0] and extracted_details[1]):
            return

        check_link = f"{temp_api_url}?action=getMessages&login={extracted_details[0]}&domain={extracted_details[1]}"
        try:
            response_data = requests.get(check_link, timeout=10).json()
            if len(response_data) != 0:
                mail_ids = [
                    item.get("id") for item in response_data if item.get("id")
                ]

                mails_dir = os.path.join(os.getcwd(), ALL_MAILS_DIRNAME)
                if not os.path.exists(mails_dir):
                    os.makedirs(mails_dir)

                for mail_item_id in mail_ids:
                    if mail_item_id not in MAIL_PRINTATE:
                        MAIL_PRINTATE.append(mail_item_id)
                        read_msg_link = f"{temp_api_url}?action=readMessage&login={extracted_details[0]}&domain={extracted_details[1]}&id={mail_item_id}"
                        msg_content_response = requests.get(read_msg_link, timeout=10).json()
                        mail_sender = msg_content_response.get("from", "")
                        mail_subject = msg_content_response.get("subject", "")
                        mail_date = msg_content_response.get("date", "")
                        mail_body = msg_content_response.get("textBody", "")

                        mail_table_data = [
                            ["From", mail_sender],
                            ["Subject", mail_subject],
                            ["Content", mail_body],
                            ["Date", mail_date],
                        ]
                        mail_table_headers = ["info", "content"]
                        for line_item_text in tabulate(
                            mail_table_data,
                            headers=mail_table_headers,
                            tablefmt="fancy_grid",
                        ).splitlines():
                            print(f"{SPACE_PREFIX}   {WHITE}{line_item_text}")
                        print()
        except requests.exceptions.RequestException as e_check:
            print(f"{RED}Error checking emails: {e_check}{WHITE}")
        except json.JSONDecodeError:
            print(f"{RED}Error decoding email list.{WHITE}")

    current_mail_address_local = ""
    try:
        custom_email_name = input(
            f"{SPACE_PREFIX}{BLUE}>{WHITE} Insert a custom name for the email:{BLUE} "
        )
        _new_mail_url_local = f"{temp_api_url}?login={custom_email_name}&domain={chosen_domain}"
        try:
            requests.get(_new_mail_url_local, timeout=10)
        except requests.exceptions.RequestException as e_register:
            print(f"{RED}Error registering temporary email: {e_register}{WHITE}")
            return

        extracted = extract_mail_details_nested(_new_mail_url_local)
        if extracted[0] and extracted[1]:
            current_mail_address_local = f"{extracted[0]}@{extracted[1]}"
            print(f"{SPACE_PREFIX}{BLUE}>{WHITE} Temp mail: {BLUE}{current_mail_address_local}")
            getpass(f"{SPACE_PREFIX}{BLUE}> {WHITE}Press enter to continue")
            print(
                f"{SPACE_PREFIX}{BLUE}-------------------[ INBOX ]-------------------\n"
            )
            while True:
                check_temp_mails_nested(_new_mail_url_local)
                sleep(5)
        else:
            print(f"{RED}Could not create temporary email address.{WHITE}")

    except KeyboardInterrupt:
        if current_mail_address_local and _new_mail_url_local:
            delete_temp_mail_nested(current_mail_address_local, _new_mail_url_local)
        sys.exit(f"{RED}\n{SPACE_PREFIX}* Aborted Temp Mail!{WHITE}")
    except requests.exceptions.RequestException as e_temp_mail_req:
        print(f"{RED}A network error occurred in Temp Mail: {e_temp_mail_req}{WHITE}")
        if current_mail_address_local and _new_mail_url_local:
            delete_temp_mail_nested(current_mail_address_local, _new_mail_url_local)
        sys.exit()
    except Exception as e_temp_mail_other: # General catch for other unexpected errors
        print(f"{RED}An unexpected error occurred in Temp Mail: {e_temp_mail_other}{WHITE}")
        if current_mail_address_local and _new_mail_url_local:
            delete_temp_mail_nested(current_mail_address_local, _new_mail_url_local)
        sys.exit()


if __name__ == "__main__":
    # # For debugging with debugpy:
    # # 1. Ensure debugpy is installed (e.g., via install_deps.sh or pip install debugpy).
    # # 2. Uncomment the following lines.
    # # 3. Run the script. It will wait for a debugger to attach on the specified port.
    # try:
    #     import debugpy
    #     DEBUGPY_PORT = 5678
    #     debugpy.listen(("0.0.0.0", DEBUGPY_PORT))
    #     print(f"debugpy: Listening for debugger attachment on port {DEBUGPY_PORT}...")
    #     debugpy.wait_for_client()
    #     print("debugpy: Debugger attached.")
    # except ImportError:
    #     print("debugpy: Module not found. Skipping debugger setup. Install with 'pip install debugpy'.")
    # except Exception as e:
    #     print(f"debugpy: Error setting up debugger: {e}")

    main_args = sys.argv
    fb_instance = Facebook()
    if len(main_args) == 1:
        menu()
    elif len(main_args) == 2:
        command_arg = main_args[1]
        if command_arg == "update":
            SCRIPT_PATH = ""
            if which("termux-setup-storage"):
                SCRIPT_PATH = "$PREFIX/bin/E4GL30S1NT"
            elif os.path.isdir("/usr/local/bin/"):
                SCRIPT_PATH = "/usr/local/bin/E4GL30S1NT"
            else:
                SCRIPT_PATH = "/usr/bin/sigit"
            update_url = "https://raw.githubusercontent.com/C0MPL3XDEV/E4GL3OS1NT/main/E4GL30S1NT.py"
            try:
                print(f"{YELLOW}Attempting to update script at {SCRIPT_PATH}...{WHITE}")
                subprocess.run(["wget", update_url, "-O", SCRIPT_PATH], check=True, timeout=60)
                subprocess.run(["chmod", "+x", SCRIPT_PATH], check=True, timeout=10)
                print(f"{BLUE}>{WHITE} wrapper script has been updated")
            except subprocess.CalledProcessError as e_update_script:
                print(f"{RED}Error updating script: {e_update_script}{WHITE}")
            except FileNotFoundError:
                print(f"{RED}Error: wget or chmod command not found. Please ensure they are installed and in your PATH.{WHITE}")
            except subprocess.TimeoutExpired:
                print(f"{RED}Update process timed out.{WHITE}")

        elif command_arg in ("settings", "configs"):
            settings()
        elif command_arg in (
            "01", "1", "02", "2", "03", "3", "04", "4", "05", "5", "06", "6", "07", "7",
            "08", "8", "09", "9", "10", "11", "12", "13", "14", "15"
        ):
            print(LOGO)
            if command_arg in ("1", "01"):
                userrecon()
            elif command_arg in ("2", "02"):
                fb_instance.facedumper()
            elif command_arg in ("3", "03"):
                mailfinder()
            elif command_arg in ("4", "04"):
                godorker()
            elif command_arg in ("5", "05"):
                phoneinfo()
            elif command_arg in ("6", "06"):
                infoga("dnslookup")
            elif command_arg in ("7", "07"):
                infoga("whois")
            elif command_arg in ("8", "08"):
                infoga("subnetcalc")
            elif command_arg in ("9", "09"):
                infoga("hostsearch")
            elif command_arg == "10":
                infoga("mtr")
            elif command_arg == "11":
                infoga("reverseiplookup")
            elif command_arg == "12":
                iplocation()
            elif command_arg == "13":
                bypass_bitly()
            elif command_arg == "14":
                github_lookup()
            elif command_arg == "15":
                temp_mail_gen()
        else:
            sys.exit(
                 RED + "* no command found for: " + main_args[1] + WHITE
            )
    else:
        sys.exit(
             RED + "* invalid number of arguments: " + str(len(main_args) - 1) + WHITE
        )

[end of E4GL30S1NT.py]
