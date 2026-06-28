"""Network lookups: IP geolocation and HackerTarget API queries."""
from __future__ import annotations

import ipaddress
import logging
import socket
import subprocess
import urllib.parse
from getpass import getpass

import requests

from eagleosint.display import (
    RED, YELLOW, BLUE, WHITE,
    SPACE_PREFIX, LINES_SEPARATOR,
)
from eagleosint.plugin import BaseProvider, ProviderCategory
from eagleosint.session import session as _session
from eagleosint.models import IPResult, DomainResult

logger = logging.getLogger(__name__)

API_HACKERTARGET = "https://api.hackertarget.com/{}/?q={}"
IPINFO_API_URL   = "https://ipinfo.io/{}/json"


class IPLocationProvider(BaseProvider):
    name = "iplocation"
    version = "1.0.0"
    description = "IP geolocation via ipinfo.io"
    category = ProviderCategory.IP

    def validate_query(self, query: str) -> str | None:
        base = super().validate_query(query)
        if base:
            return base
        try:
            ipaddress.ip_address(query.strip())
        except ValueError:
            return "Invalid IP address"
        return None

    def execute(self, query: str) -> list[IPResult]:
        error = self.validate_query(query)
        if error:
            logger.warning("invalid query: %s", error)
            return []

        try:
            resp = _session.get(
                IPINFO_API_URL.format(query.strip()), timeout=10
            )
            data = resp.json()
        except requests.exceptions.RequestException as e:
            logger.error("ipinfo API error: %s", e)
            return []

        return [IPResult(
            query=query,
            ip=data.get("ip", query),
            city=data.get("city"),
            region=data.get("region"),
            country=data.get("country"),
            coordinates=data.get("loc"),
            org=data.get("org"),
            timezone=data.get("timezone"),
            hostname=data.get("hostname"),
            raw=data,
        )]

class DomainInfoProvider(BaseProvider):
    name = "network"
    version = "1.0.0"
    description = "DNS, WHOIS, and host lookups via HackerTarget API"
    category = ProviderCategory.DOMAIN

    def execute(self, query: str, query_type: str = "dnslookup") -> list[DomainResult]:
        error = self.validate_query(query)
        if error:
            logger.warning("invalid query: %s", error)
            return []

        target = urllib.parse.quote(query.strip(), safe="-._~")
        if target.split(".")[0].isnumeric():
            try:
                target = socket.gethostbyname(target)
            except socket.gaierror as e:
                logger.error("hostname resolution error: %s", e)
                return []

        try:
            resp = _session.get(
                API_HACKERTARGET.format(query_type, target),
                stream=True, timeout=10,
            )
            lines = [
                line.decode("utf-8")
                for line in resp.iter_lines()
                if line
            ]
        except requests.exceptions.RequestException as e:
            logger.error("HackerTarget API error: %s", e)
            return []

        return [DomainResult(
            query=query,
            query_type=query_type,
            records=lines,
        )]

# ------------------------------------------------------------------
# Interactive CLI wrappers (unchanged interface for cli.py)
# ------------------------------------------------------------------

def iplocation() -> IPResult | None:
    """Interactive CLI wrapper for IP geolocation."""
    try:
        process = subprocess.run(
            ["curl", "ifconfig.co", "--silent"],
            capture_output=True, text=True, check=True, timeout=10,
        )
        local_ip = process.stdout.strip()
        print(f"{SPACE_PREFIX}{BLUE}>{WHITE} local IP: {local_ip}")
    except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
        pass

    ip_address = input(f"{SPACE_PREFIX}{BLUE}>{WHITE} enter IP:{BLUE} ").strip()

    provider = IPLocationProvider()
    results = provider.run(ip_address)

    print(WHITE + LINES_SEPARATOR)
    if not results:
        print(f"{RED}No results for '{ip_address}'.{WHITE}")
        print(WHITE + LINES_SEPARATOR)
        getpass(SPACE_PREFIX + "press enter for back to previous menu ")
        return None

    result: IPResult = results[0]  # type: ignore[assignment]
    for label, value in [
        ("IP", result.ip), ("CITY", result.city), ("COUNTRY", result.country),
        ("LOC", result.coordinates), ("ORG", result.org), ("TIMEZONE", result.timezone),
    ]:
        print(f"{SPACE_PREFIX}{BLUE}-{WHITE} {label}: {value or ''}")

    print(WHITE + LINES_SEPARATOR)
    getpass(SPACE_PREFIX + "press enter for back to previous menu ")
    return result

def infoga(option: str) -> DomainResult | None:
    """Interactive CLI wrapper for HackerTarget queries."""
    target = input(f"{SPACE_PREFIX}{BLUE}>{WHITE} enter domain or IP:{BLUE} ").strip()
    if not target:
        return None

    provider = DomainInfoProvider()
    results = provider.run(target, query_type=option)

    print(WHITE + LINES_SEPARATOR)
    if not results:
        print(f"{RED}No results for '{target}'.{WHITE}")
        print(WHITE + LINES_SEPARATOR)
        getpass(SPACE_PREFIX + "press enter for back to previous menu ")
        return None

    result: DomainResult = results[0]  # type: ignore[assignment]
    for line in result.records:
        print(f"{SPACE_PREFIX}{BLUE}-{WHITE} {line}")

    print(WHITE + LINES_SEPARATOR)
    getpass(SPACE_PREFIX + "press enter for back to previous menu ")
    return result