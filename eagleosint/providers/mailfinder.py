"""Email address finder via permutation + real-email validation."""
from __future__ import annotations

import json
import logging
import threading
from getpass import getpass
from concurrent.futures import ThreadPoolExecutor
from random import seed
from time import sleep
from typing import Callable

import requests

from eagleosint.config import settings, save_config
from eagleosint.display import (
    RED, GREEN, YELLOW, BLUE, WHITE,
    BG_RED, BG_GREEN, BG_YELLOW,
    SPACE_PREFIX, LINES_SEPARATOR,
)
from eagleosint.plugin import BaseProvider, ProviderCategory
from eagleosint.session import session as _session
from eagleosint.models import EmailStatus, EmailResult

logger = logging.getLogger(__name__)

PINGUTIL_DEMO_URL = "https://pingutil.com/v1/demo/lookup"
PINGUTIL_AUTH_URL = "https://pingutil.com/v1/lookup"

EMAIL_PROVIDERS = [
    "gmail.com", "yahoo.com", "hotmail.com", "aol.com", "msn.com",
    "comcast.net", "live.com", "rediffmail.com", "ymail.com",
    "outlook.com", "cox.net", "googlemail.com", "rocketmail.com",
    "att.net", "facebook.com", "bellsouth.net", "charter.net", "sky.com",
    "earthlink.net", "optonline.net", "qq.com", "me.com", "gmx.net",
    "mail.com", "ntlworld.com", "frontiernet.net", "windstream.net",
    "mac.com", "centurytel.net", "aim.com",
]

def _generate_variations(full_name: str) -> list[str]:
    """Generate username variations from a full name."""
    name = full_name.lower().strip()
    joined = name.replace(" ", "")
    variations = [
        joined, joined + "123",
        joined + "1234", joined.replace("i", "1"),
        joined.replace("a", "4"), joined.replace("e", "3"),
        joined.replace("i", "1").replace("a", "4").replace("e", "3"),
        joined.replace("i", "1").replace("a", "4"),
        joined.replace("i", "1").replace("e", "3"),
        joined.replace("a", "4").replace("e", "3"),
    ]
    for part in name.split(" "):
        variations.extend([part, part + "123", part + "1234"])
    return variations

class MailFinderProvider(BaseProvider):
    name = "mailfinder"
    version = "1.0.0"
    description = "Find email addresses by name permutation + Pingutil validation"
    category = ProviderCategory.EMAIL

    def _check_single(self, email: str, api_key: str | None) -> EmailResult:
        """Validate a single email address against Pingutil API."""
        url = PINGUTIL_AUTH_URL if api_key else PINGUTIL_DEMO_URL
        headers = {"Authorization": f"Bearer {api_key}"} if api_key else {}

        try:
            resp = _session.post(
                url, json={"input": email}, headers=headers, timeout=10
            )
            if resp.status_code != 200:
                logger.warning("HTTP %d for %s", resp.status_code, email)
                return EmailResult(
                    query=email, email=email, status=EmailStatus.UNKNOWN
                )
            category = resp.json().get("category", "unknown")
        except requests.exceptions.RequestException as e:
            logger.error("request error for %s: %s", email, e)
            return EmailResult(
                query=email, email=email, status=EmailStatus.UNKNOWN
            )
        except json.JSONDecodeError:
            logger.error("invalid JSON for %s", email)
            return EmailResult(
                query=email, email=email, status=EmailStatus.UNKNOWN
            )

        if category == "disposable":
            status = EmailStatus.INVALID
        elif category == "unknown":
            status = EmailStatus.UNKNOWN
        else:
            status = EmailStatus.VALID

        return EmailResult(query=email, email=email, status=status)

    def execute(
            self,
            query: str,
            api_key: str | None = None,
            max_workers: int = 20,
            delay: float | None = None,
            on_result: Callable | None = None,
    ) -> list[EmailResult]:
        error = self.validate_query(query)
        if error:
            logger.warning("invalid query: %s", error)
            return []

        key = api_key or settings.get_key("pingutil-api-key")
        if delay is None:
            delay = 6.1 if not key else 0.20

        variations = _generate_variations(query)
        emails = [
            f"{v}@{domain}"
            for v in variations
            for domain in EMAIL_PROVIDERS
        ]

        results: list[EmailResult] = []
        lock = threading.Lock()

        def _worker(email: str) -> None:
            result = self._check_single(email, key)
            with lock:
                results.append(result)
            if on_result:
                on_result(result, len(results), len(emails))

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            for email in emails:
                executor.submit(_worker, email)
                sleep(delay)

        return results

# ------------------------------------------------------------------
# Interactive CLI wrapper
# ------------------------------------------------------------------

def mailfinder() -> list[EmailResult]:
    """Interactive CLI wrapper — prompts for name, prints progress."""
    full_name = input(f"{SPACE_PREFIX}{BLUE}>{WHITE} enter name:{BLUE} ").lower()
    if not full_name:
        return []

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

    results_file = "result_mailfinder.txt"
    output_fh = open(results_file, "w", encoding="utf-8")

    def _on_result(result: EmailResult, current: int, total: int) -> None:
        if result.status == EmailStatus.VALID:
            color, bg = GREEN, BG_GREEN
            pad = "  "
            output_fh.write(result.email + "\n")
        elif result.status == EmailStatus.INVALID:
            color, bg = RED, BG_RED
            pad = " "
        else:
            color, bg = YELLOW, BG_YELLOW
            pad = " "
        print(
            f"{SPACE_PREFIX}{bg}{WHITE}{pad}{result.status.value.upper()}"
            f"{pad}{WHITE}{BLUE} {current}/{total}{WHITE} Status: "
            f"{color}{result.status.value}{WHITE} Email: {result.email}"
        )

    try:
        provider = MailFinderProvider()
        results: list[EmailResult] = provider.run(  # type: ignore[assignment]
            full_name, api_key=api_key, on_result=_on_result
        )
    except KeyboardInterrupt:
        print(f"\r{RED}{SPACE_PREFIX}* Operation aborted by user.{WHITE}")
        results = []
    finally:
        output_fh.close()

    valid = [r for r in results if r.status == EmailStatus.VALID]
    print(WHITE + LINES_SEPARATOR)
    print(
        f"{SPACE_PREFIX}{BLUE}>{WHITE} {len(valid)} retrieved as: "
        f"{YELLOW}{results_file}"
    )
    getpass(SPACE_PREFIX + "press enter for back to previous menu ")
    return results