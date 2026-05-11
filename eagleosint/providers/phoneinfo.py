"""Phone number information via Veriphone API."""
import json
import urllib.parse
from getpass import getpass

import requests

from eagleosint.config import CONFIGS, VERIPHONE_API_CONFIG_KEY, save_config
from eagleosint.display import (
    RED, YELLOW, BLUE, WHITE,
    BG_BLUE, BG_RED,
    SPACE_PREFIX, LINES_SEPARATOR,
)
from eagleosint.session import session as _session

VERIPHONE_API_BASE_URL = "https://api.veriphone.io/v2/verify"


def phoneinfo():
    """Retrieves information about a phone number."""
    phone_number = input(f"{SPACE_PREFIX}{BLUE}>{WHITE} enter number:{BLUE} ")
    api_key = CONFIGS.get(VERIPHONE_API_CONFIG_KEY)
    if not api_key:
        api_key = input(
            f"{SPACE_PREFIX}{WHITE}{BLUE}>{WHITE} enter your api key "
            f"(https://veriphone.io) :{BLUE} "
        )
        CONFIGS[VERIPHONE_API_CONFIG_KEY] = api_key
        save_config()
    if not phone_number:
        return
    print(WHITE + LINES_SEPARATOR)
    api_url = (
        f"{VERIPHONE_API_BASE_URL}?phone="
        f"{urllib.parse.quote(phone_number.strip())}&key={api_key}"
    )
    try:
        req = _session.get(api_url, timeout=10)
        req.raise_for_status()
        res = req.json()
        for info_key, info_value in res.items():
            print(
                f"{SPACE_PREFIX}{BLUE}-{WHITE} {info_key}"
                f"{' ' * (23 - len(info_key))}:    {YELLOW}"
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