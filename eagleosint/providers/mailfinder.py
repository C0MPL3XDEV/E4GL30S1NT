"""Email address finder via permutation + real-email validation."""
import json
import threading
from getpass import getpass
from concurrent.futures import ThreadPoolExecutor
from random import seed
from time import sleep

import requests

from eagleosint.config import settings, logger, save_config
from eagleosint.display import (
    RED, GREEN, YELLOW, BLUE, WHITE,
    BG_RED, BG_GREEN, BG_YELLOW,
    SPACE_PREFIX, LINES_SEPARATOR,
)
from eagleosint.session import session as _session
from eagleosint.models import EmailStatus

PINGUTIL_DEMO_URL = "https://pingutil.com/v1/demo/lookup"
PINGUTIL_AUTH_URL = "https://pingutil.com/v1/lookup"

class _State:
    __slots__ = ("num", "lock")
    def __init__(self):
        self.num = 0
        self.lock = threading.Lock()


def check_email(email, api_key, total, ok_list, output_file, state):
    url = PINGUTIL_AUTH_URL if api_key else PINGUTIL_DEMO_URL
    headers = {"Authorization": f"Bearer {api_key}"} if api_key else {}

    try:
        response = _session.post(url, json={"input": email}, headers=headers, timeout=10)
        if response.status_code != 200:
            with state.lock:
                state.num += 1
                current_count = state.num
            print(
                f"{SPACE_PREFIX}{BG_RED}{WHITE}  ERROR  {WHITE}{BLUE} "
                f"{current_count}/{total}{WHITE} Status: {RED}HTTP "
                f"{response.status_code} for {email}{WHITE}"
            )
            return
        try:
            category = response.json().get("category", "unknown")
        except json.JSONDecodeError:
            with state.lock:
                state.num += 1
                current_count = state.num
            print(
                f"{SPACE_PREFIX}{BG_RED}{WHITE}  ERROR  {WHITE}{BLUE} "
                f"{current_count}/{total}{WHITE} Status: {RED}invalid JSON "
                f"for {email}{WHITE}"
            )
            return
        if category == "disposable":
            status_val = EmailStatus.INVALID
        elif category == "unknown":
            status_val = EmailStatus.UNKNOWN
        else:
            status_val = EmailStatus.VALID

        if status_val == EmailStatus.INVALID:
            color_code, back_color_code = RED, BG_RED
        elif status_val == EmailStatus.UNKNOWN:
            color_code, back_color_code = YELLOW, BG_YELLOW
        else:
            color_code, back_color_code = GREEN, BG_GREEN

        with state.lock:
            state.num += 1
            current_count = state.num
            if status_val == EmailStatus.VALID:
                ok_list.append(email)
                output_file.write(email + "\n")

        pad = "  " if status_val == EmailStatus.VALID else " "
        print(
            f"{SPACE_PREFIX}{back_color_code}{WHITE}{pad}{status_val.value.upper()}"
            f"{pad}{WHITE}{BLUE} {current_count}/{total}{WHITE} Status: "
            f"{color_code}{status_val.value}{WHITE} Email: {email}"
        )
    except requests.exceptions.RequestException as e_check_email:
        with state.lock:
            state.num += 1
            current_count = state.num
        print(
            f"{SPACE_PREFIX}{BG_RED}{WHITE}  ERROR  {WHITE}{BLUE} "
            f"{current_count}/{total}{WHITE} Status: {RED}"
            f"{str(e_check_email)}{WHITE} Email: {email}"
        )


def mailfinder():
    """Finds email addresses associated with a given name."""
    full_name = input(f"{SPACE_PREFIX}{BLUE}>{WHITE} enter name:{BLUE} ").lower()
    if not full_name:
        return
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

    for name_part in full_name.split(" "):
        user_variations.append(name_part)
        user_variations.append(name_part + "123")
        user_variations.append(name_part + "1234")

    results_file = "result_mailfinder.txt"
    with open(results_file, "w", encoding="utf-8") as mail_file:
        valid_emails = []
        try:
            api_key = settings.get_key("pingutil-api-key")
            if not api_key:
                entered = input(
                    f"{SPACE_PREFIX}{WHITE}{BLUE}>{WHITE} pingutil API key "
                    f"(enter to skip, uses demo mode — 10 req/min):{BLUE} "
                ).strip()
                if entered:
                    api_key = entered
                    settings.set_key("pingutil-api-key", api_key)
                    save_config()
            if not api_key:
                print(f"{SPACE_PREFIX}{YELLOW}! demo mode active — rate limited to 10 req/min{WHITE}")

            print(WHITE + LINES_SEPARATOR)
            state = _State()
            total = len(email_providers) * len(user_variations)

            with ThreadPoolExecutor(max_workers=20) as executor:
                for user_variation in user_variations:
                    for provider_domain in email_providers:
                        email_address = f"{user_variation}@{provider_domain}"
                        executor.submit(
                            check_email,
                            email_address, api_key, total,
                            valid_emails, mail_file, state
                        )
                        sleep(6.1 if not api_key else 0.20)

        except KeyboardInterrupt:
            print("ERROR")
            print(f"\r{RED}{SPACE_PREFIX}* Operation aborted by user.{WHITE}")
    print(WHITE + LINES_SEPARATOR)
    print(
        f"{SPACE_PREFIX}{BLUE}>{WHITE} {str(len(valid_emails))} retrieved as: "
        f"{YELLOW}{results_file}"
    )
    getpass(SPACE_PREFIX + "press enter for back to previous menu ")