"""GitHub user profile lookup."""
import json
import re
from getpass import getpass
from typing import ClassVar
import logging

import requests
from tabulate import tabulate

from eagleosint.display import (
    RED, BLUE, WHITE,
    SPACE_PREFIX, LINES_SEPARATOR,
)
from eagleosint.plugin import BaseProvider, ProviderCategory
from eagleosint.session import session as _session
from eagleosint.models import GitHubProfile

logger = logging.getLogger(__name__)

GITHUB_API_URL = "https://api.github.com/users/{}"

class GithubProvider(BaseProvider):
    name = "github"
    version = "1.0.0"
    description = "GitHub user profile lookup via public REST API"
    category = ProviderCategory.SOCIAL
    required_keys: ClassVar[list[str]] = []

    def execute(self, query: str) -> list[GitHubProfile]:
        error = self.validate_query(query)
        if error:
            logger.warning("Invalid query: %s", error)
            return []

        if not re.match(r"^[a-zA-Z0-9][a-zA-Z0-9-]{0,37}$", query):
            logger.warning("Invalid GitHub username: %s", query)
            return []

        try:
            response = _session.get(GITHUB_API_URL.format(query), timeout=10)
            response.raise_for_status()
            data = response.json()
        except requests.exceptions.RequestException as e:
            logger.error("GitHub API error: %s", e)
            return []
        except json.JSONDecodeError:
            logger.error("Invalid JSON response from GitHub API")
            return []

        profile = GitHubProfile(
            query=query,
            username=data.get("login", query),
            name=data.get("name"),
            email=data.get("email"),
            bio=data.get("bio"),
            location=data.get("location"),
            company=data.get("company"),
            blog=data.get("blog"),
            public_repos=data.get("public_repos"),
            followers=data.get("followers"),
            following=data.get("following"),
            created_at=data.get("created_at"),
            avatar_url=data.get("avatar_url"),
            html_url=data.get("html_url"),
            raw=data,
        )
        return [profile]

def github_lookup() -> GitHubProfile | None:
    """Interactive CLI wrapper — prompts for username, prints table."""
    print(WHITE + LINES_SEPARATOR)
    github_user = input(
        f"{SPACE_PREFIX}{WHITE}{BLUE}>{WHITE} Github username: {BLUE}"
    ).strip()
    print(WHITE)

    provider = GithubProvider()
    results = provider.run(github_user)

    if not results:
        print(f"{RED}No results for '{github_user}'.{WHITE}")
        print(WHITE + LINES_SEPARATOR)
        getpass(SPACE_PREFIX + "press enter for back to previous menu ")
        return None

    profile: GitHubProfile = results[0]  # type: ignore[assignment]

    table_data = [[str(key), str(value)] for key, value in profile.raw.items()]
    for line_item in tabulate(
        table_data, headers=["info", "content"], tablefmt="fancy_grid"
    ).splitlines():
        print(" " * int(len(SPACE_PREFIX) / 2) + line_item)

    print(WHITE + LINES_SEPARATOR)
    getpass(SPACE_PREFIX + "press enter for back to previous menu ")
    return profile