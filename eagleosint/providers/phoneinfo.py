"""Phone number information via Veriphone API."""
from __future__ import annotations
import json
import logging
import urllib.parse
from typing import ClassVar
from getpass import getpass

import requests

from eagleosint.config import settings, save_config
from eagleosint.display import (
    RED, YELLOW, BLUE, WHITE,
    BG_BLUE, BG_RED,
    SPACE_PREFIX, LINES_SEPARATOR,
)
from eagleosint.models import PhoneResult
from eagleosint.plugin import BaseProvider, ProviderCategory
from eagleosint.session import session as _session

logger = logging.getLogger(__name__)

VERIPHONE_API_BASE_URL = "https://api.veriphone.io/v2/verify"

class PhoneInfoProvider(BaseProvider):
    name = "phoneinfo"
    version = "1.0.0"
    description = "Phone number validation and carrier lookup via Veriphone API"
    category = ProviderCategory.PHONE
    required_keys: ClassVar[list[str]] = ["veriphone-api-key"]

    def execute(self, query: str, api_key: str | None = None) -> list[PhoneResult]:
        error = self.validate_query(query)
        if error:
            logger.warning("invalid query: %s", error)
            return []

        key = api_key or settings.get_key("veriphone-api-key")
        if not key:
            logger.error("missing Veriphone API key")
            return []

        api_url = (
            f"{VERIPHONE_API_BASE_URL}?phone="
            f"{urllib.parse.quote(query.strip())}&key={key}"
        )
        try:
            resp = _session.get(api_url, timeout=10)
            resp.raise_for_status()
            data = resp.json()
        except requests.exceptions.RequestException as e:
            logger.error("Veriphone API error: %s", e)
            return []
        except json.JSONDecodeError:
            logger.error("invalid JSON from Veriphone API")
            return []

        return [PhoneResult(
            query=query,
            phone=data.get("phone", query),
            phone_valid=data.get("phone_valid"),
            country=data.get("country"),
            country_code=data.get("country_code"),
            carrier=data.get("carrier"),
            line_type=data.get("line_type"),
            international_number=data.get("international_number"),
            raw=data,
        )]

def phoneinfo() -> PhoneResult | None:
    """Interactive CLI wrapper — prompts for number and API key."""
    phone_number = input(f"{SPACE_PREFIX}{BLUE}>{WHITE} enter number:{BLUE} ")

    api_key = settings.get_key("veriphone-api-key")
    if not api_key:
        api_key = input(
            f"{SPACE_PREFIX}{WHITE}{BLUE}>{WHITE} enter your api key "
            f"(https://veriphone.io) :{BLUE} "
        )
        settings.set_key("veriphone-api-key", api_key)
        save_config()

    provider = PhoneInfoProvider()
    results = provider.run(phone_number, api_key=api_key)

    print(WHITE + LINES_SEPARATOR)
    if not results:
        print(f"{RED}No results for '{phone_number}'.{WHITE}")
        print(WHITE + LINES_SEPARATOR)
        getpass(SPACE_PREFIX + "press enter for back to previous menu ")
        return None

    result = results[0]
    if result.raw:
        for info_key, info_value in result.raw.items():
            print(
                f"{SPACE_PREFIX}{BLUE}-{WHITE} {info_key}"
                f"{' ' * (23 - len(info_key))}:    {YELLOW}"
                f"{info_value}{WHITE}"
            )

    print(WHITE + LINES_SEPARATOR)
    print(f"{SPACE_PREFIX}{BG_BLUE} DONE {BG_RED} {phone_number} {WHITE}")

    getpass(SPACE_PREFIX + "press enter for back to previous menu ")
    return result