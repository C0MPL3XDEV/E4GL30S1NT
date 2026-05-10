"""Shared HTTP session with default headers for all outbound requests."""
import requests

HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:120.0) Gecko/20100101 Firefox/120.0"
}

session = requests.Session()
session.headers.update(HEADERS)
