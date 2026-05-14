"""GitHub user profile lookup."""
import json
import re
from getpass import getpass

import requests
from tabulate import tabulate

from eagleosint.display import (
    RED, BLUE, WHITE,
    SPACE_PREFIX, LINES_SEPARATOR,
)
from eagleosint.session import session as _session
from eagleosint.models import GitHubProfile

GITHUB_API_URL = "https://api.github.com/users/{}"


def github_lookup() -> GitHubProfile | None:
    """Retrieves and displays information about a GitHub user."""
    print(WHITE + LINES_SEPARATOR)
    github_user = input(
        f"{SPACE_PREFIX}{WHITE}{BLUE}>{WHITE} Github username: {BLUE}"
    ).strip()
    if not re.match(r"^[a-zA-Z0-9][a-zA-Z0-9-]{0,37}$", github_user):
        print(f"{RED}Invalid Github username.{WHITE}")
        return
    print(WHITE)
    try:
        req = _session.get(GITHUB_API_URL.format(github_user), timeout=10)
        res_data = req.json()
        table_data = [[str(k), str(v)] for k, v in res_data.items()]
        for line_item in tabulate(
            table_data, headers=["info", "content"], tablefmt="fancy_grid"
        ).splitlines():
            print(" " * int(len(SPACE_PREFIX) / 2) + line_item)
    except requests.exceptions.RequestException as e:
        print(f"{RED}Error fetching GitHub user information: {e}{WHITE}")
    except json.JSONDecodeError:
        print(f"{RED}Error decoding JSON response from GitHub.{WHITE}")
    print(WHITE + LINES_SEPARATOR)

    profile = GitHubProfile(
        query=github_user,
        username=res_data.get("login", github_user),
        name=res_data.get("name"),
        email=res_data.get("email"),
        bio=res_data.get("bio"),
        location=res_data.get("location"),
        company=res_data.get("company"),
        blog=res_data.get("blog"),
        public_repos=res_data.get("public_repos"),
        followers=res_data.get("followers"),
        following=res_data.get("following"),
        created_at=res_data.get("created_at"),
        avatar_url=res_data.get("avatar_url"),
        html_url=res_data.get("html_url"),
        raw=res_data,
    )

    return profile

    getpass(SPACE_PREFIX + "press enter for back to previous menu ")