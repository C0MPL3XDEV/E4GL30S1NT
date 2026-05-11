"""Email address finder via permutation + real-email validation."""
import json
import threading
from getpass import getpass
from concurrent.futures import ThreadPoolExecutor
from time import sleep

import requests

from eagleosint.config import CONFIGS, REALEMAIL_API_CONFIG_KEY, logger, save_config
from eagleosint.display import (
    RED, GREEN, YELLOW, BLUE, WHITE,
    BG_RED, BG_GREEN, BG_YELLOW,
    SPACE_PREFIX, LINES_SEPARATOR,
)
from eagleosint.session import session as _session

REALEMAIL_API_URL = "https://isitarealemail.com/api/email/validate"

CHECK_EMAIL_NUM = 0
_EMAIL_LOCK = threading.Lock()


def check_email(email, api, total, ok_list, output_file):
    global CHECK_EMAIL_NUM
    try:
        response = _session.get(
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
                with _EMAIL_LOCK:
                    CHECK_EMAIL_NUM += 1
                    current_count = CHECK_EMAIL_NUM
                print(
                    f"{SPACE_PREFIX}{BG_RED}{WHITE}  ERROR  {WHITE}{BLUE} "
                    f"{current_count}/{total}{WHITE} Status: {RED}API "
                    f"error or invalid JSON for {email}{WHITE}"
                )
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

        with _EMAIL_LOCK:
            CHECK_EMAIL_NUM += 1
            current_count = CHECK_EMAIL_NUM
            if status_val == "valid":
                ok_list.append(email)
                output_file.write(email + "\n")

        print_space_val = "  " if status_val == "valid" else " "
        print(
            f"{SPACE_PREFIX}{back_color_code}{WHITE}{print_space_val}{status_val.upper()}"
            f"{print_space_val}{WHITE}{BLUE} {current_count}/{total}{WHITE} Status: "
            f"{color_code}{status_val}{WHITE} Email: {email}"
        )
    except requests.exceptions.RequestException as e_check_email:
        with _EMAIL_LOCK:
            CHECK_EMAIL_NUM += 1
            current_count = CHECK_EMAIL_NUM
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
            api_key = CONFIGS.get(REALEMAIL_API_CONFIG_KEY)
            if not api_key:
                api_key = input(
                    f"{SPACE_PREFIX}{WHITE}{BLUE}>{WHITE} enter your api key "
                    f"(https://isitarealemail.com) :{BLUE} "
                )
                CONFIGS[REALEMAIL_API_CONFIG_KEY] = api_key
                save_config()
            print(WHITE + LINES_SEPARATOR)

            global CHECK_EMAIL_NUM
            CHECK_EMAIL_NUM = 0
            total = len(email_providers) * len(user_variations)

            with ThreadPoolExecutor(max_workers=20) as executor:
                for user_variation in user_variations:
                    for provider_domain in email_providers:
                        email_address = f"{user_variation}@{provider_domain}"
                        executor.submit(
                            check_email,
                            email_address, api_key, total,
                            valid_emails, mail_file
                        )
                        sleep(0.20)
            CHECK_EMAIL_NUM = 0

        except KeyboardInterrupt:
            print("ERROR")
            print(f"\r{RED}{SPACE_PREFIX}* Operation aborted by user.{WHITE}")
    print(WHITE + LINES_SEPARATOR)
    print(
        f"{SPACE_PREFIX}{BLUE}>{WHITE} {str(len(valid_emails))} retrieved as: "
        f"{YELLOW}{results_file}"
    )
    getpass(SPACE_PREFIX + "press enter for back to previous menu ")