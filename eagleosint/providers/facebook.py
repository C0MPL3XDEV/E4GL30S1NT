"""Facebook data dumper using mbasic + Graph API."""
import json
import re
import sys
from getpass import getpass

import requests

from eagleosint.config import COOKIE_FILE, logger
from eagleosint.display import (
    RED, YELLOW, BLUE, WHITE, DARK_GRAY,
    BG_BLUE, BG_RED,
    SPACE_PREFIX, LINES_SEPARATOR,
)
from eagleosint.session import HEADERS

MBASIC_FB_URL  = "https://mbasic.facebook.com{}"
GRAPH_FB_URL   = "https://graph.facebook.com{}"
DUMP_IDFRIENDS_TXT = "dump_idfriends.txt"
DUMP_EMAIL_TXT     = "dump_email.txt"
DUMP_PHONE_TXT     = "dump_phone.txt"
DUMP_BIRTHDAY_TXT  = "dump_birthday.txt"
DUMP_LOCATION_TXT  = "dump_location.txt"


class Facebook:
    """A class for interacting with Facebook data."""

    def __init__(self):
        self.cookies = self._load_cookies()

    def _load_cookies(self):
        try:
            with open(COOKIE_FILE, "r", encoding="utf-8") as cf:
                return {"cookie": cf.read().strip()}
        except FileNotFoundError:
            return self._prompt_for_cookies()

    def _prompt_for_cookies(self):
        while True:
            coki_input = getpass(
                f"{SPACE_PREFIX}{BLUE}>{WHITE} enter facebook cookies (hidden input): "
            )
            if coki_input:
                with open(COOKIE_FILE, "w", encoding="utf-8") as cf:
                    cf.write(coki_input)
                return {"cookie": coki_input}

    def user_token(self):
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
        try:
            req_content = requests.get(
                MBASIC_FB_URL.format("/me"), cookies=self.cookies, timeout=10
            ).content
            if b"mbasic_logout_button" not in req_content:
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
                return
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
                    if res_friend_data.get("email"):
                        print(f"{SPACE_PREFIX}{BLUE}-{WHITE} Email: {res_friend_data['email']}")
                    if res_friend_data.get("phone"):
                        print(f"{SPACE_PREFIX}{BLUE}-{WHITE} Phone: {res_friend_data['phone']}")
                    if res_friend_data.get("birthday"):
                        print(f"{SPACE_PREFIX}{BLUE}-{WHITE} Birthday: {res_friend_data['birthday']}")
                    if res_friend_data.get("location", {}).get("name"):
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

    def dump_id(self):
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
            if "id_file" in locals() and not id_file.closed:
                id_file.close()

        print(WHITE + LINES_SEPARATOR)
        print(
            f"{SPACE_PREFIX}{BLUE}>{WHITE} {str(len(id_list))} retrieved as: {YELLOW}{DUMP_IDFRIENDS_TXT}"
        )
        getpass(SPACE_PREFIX + "press enter for back to previous menu ")

    def _dump_field(self, field_key: str, output_path: str, display_label: str) -> None:
        token = self.user_token()
        if not token:
            return
        result_list = []
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
            with open(output_path, "w", encoding="utf-8") as out_file:
                try:
                    for item in res_data.get("data", []):
                        try:
                            r = requests.get(
                                GRAPH_FB_URL.format(
                                    f"/{item['id']}?access_token={token}&limit=5000"
                                ),
                                headers=HEADERS,
                                timeout=10,
                            )
                            r.raise_for_status()
                            d = r.json()
                            name = d.get("name")
                            fid = d.get("id")
                            val = d
                            for part in field_key.split("."):
                                val = val.get(part) if isinstance(val, dict) else None
                            if name and val and fid:
                                print(
                                    f"{SPACE_PREFIX}{BG_BLUE} DONE {WHITE} "
                                    f"{display_label}: {val} {RED}->{WHITE} {name}"
                                )
                                result_list.append(val)
                                out_file.write(f"{val}|{fid}|{name}\n")
                        except (requests.exceptions.RequestException, json.JSONDecodeError):
                            continue
                        except KeyboardInterrupt:
                            break
                except KeyboardInterrupt:
                    pass
        except requests.exceptions.RequestException as e:
            print(f"{RED}Error fetching friend list: {e}{WHITE}")
        except json.JSONDecodeError:
            print(f"{RED}Error decoding friend list response.{WHITE}")
        print(WHITE + LINES_SEPARATOR)
        print(
            f"{SPACE_PREFIX}{BLUE}>{WHITE} {len(result_list)} retrieved as: "
            f"{YELLOW}{output_path}"
        )
        getpass(SPACE_PREFIX + "press enter for back to previous menu ")

    def dump_email(self):
        self._dump_field("email", DUMP_EMAIL_TXT, "Email")

    def dump_phone(self):
        self._dump_field("mobile_phone", DUMP_PHONE_TXT, "Phone")

    def dump_birthday(self):
        self._dump_field("birthday", DUMP_BIRTHDAY_TXT, "Birthday")

    def dump_location(self):
        self._dump_field("location.name", DUMP_LOCATION_TXT, "Location")