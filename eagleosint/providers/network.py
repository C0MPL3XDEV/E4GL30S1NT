"""Network lookups: IP geolocation and HackerTarget API queries."""
import ipaddress
import socket
import subprocess
import urllib.parse
from getpass import getpass

import requests

from eagleosint.display import (
    RED, YELLOW, BLUE, WHITE,
    SPACE_PREFIX, LINES_SEPARATOR,
)
from eagleosint.session import session as _session

API_HACKERTARGET = "https://api.hackertarget.com/{}/?q={}"
IPINFO_API_URL   = "https://ipinfo.io/{}/json"


def iplocation():
    """Retrieves and displays geolocation information for an IP address."""
    try:
        process = subprocess.run(
            ["curl", "ifconfig.co", "--silent"],
            capture_output=True, text=True, check=True, timeout=10,
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

    ip_address = input(f"{SPACE_PREFIX}{BLUE}>{WHITE} enter IP:{BLUE} ").strip()
    try:
        ipaddress.ip_address(ip_address)
    except ValueError:
        print(f"{RED}Invalid IP address.{WHITE}")
        return
    print(WHITE + LINES_SEPARATOR)
    try:
        req = _session.get(IPINFO_API_URL.format(ip_address), timeout=10).json()
        for label, key in [
            ("IP", "ip"), ("CITY", "city"), ("COUNTRY", "country"),
            ("LOC", "loc"), ("ORG", "org"), ("TIMEZONE", "timezone"),
        ]:
            print(f"{SPACE_PREFIX}{BLUE}-{WHITE} {label}: {req.get(key, '')}")
    except requests.exceptions.RequestException as e:
        print(f"{RED}Error fetching IP information: {e}{WHITE}")
    print(WHITE + LINES_SEPARATOR)
    getpass(SPACE_PREFIX + "press enter for back to previous menu ")


def infoga(option):
    """Retrieves information about a domain or IP address."""
    target = input(f"{SPACE_PREFIX}{BLUE}>{WHITE} enter domain or IP:{BLUE} ").strip()
    if not target:
        return
    target = urllib.parse.quote(target, safe="-._~")
    if target.split(".")[0].isnumeric():
        try:
            target = socket.gethostbyname(target)
        except socket.gaierror as e:
            print(f"{RED}Error resolving hostname: {e}{WHITE}")
            return
    print(WHITE + LINES_SEPARATOR)
    try:
        req = _session.get(
            API_HACKERTARGET.format(option, target), stream=True, timeout=10
        )
        for res_line in req.iter_lines():
            print(f"{SPACE_PREFIX}{BLUE}-{WHITE} {res_line.decode('utf-8')}")
    except requests.exceptions.RequestException as e:
        print(f"{RED}Error fetching information: {e}{WHITE}")
    print(WHITE + LINES_SEPARATOR)
    getpass(SPACE_PREFIX + "press enter for back to previous menu ")