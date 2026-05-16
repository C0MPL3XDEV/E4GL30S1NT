"""
BaseProvider ABC and ProviderCategory Enum

Every provider plugin must subclass BaseProvider and implement execute().
Existing CLI are not yet migrated -- this is the target interface.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from enum import Enum
from typing import ClassVar

from eagleosint.models import ProviderResult

class ProviderCategory(str, Enum):
    USERNAME       = "username"
    EMAIL          = "email"
    PHONE          = "phone"
    DOMAIN         = "domain"
    IP             = "ip"
    SOCIAL         = "social"
    BREACH         = "breach"
    IMAGE          = "image"
    DOCUMENT       = "document"
    DARK_WEB       = "dark_web"
    INFRASTRUCTURE = "infrastructure"
    UTILITY        = "utility"


class BaseProvider(ABC):
    """
    Contract every provider plugin must satisfy.

    Class-level attributes declare metadata.
    execute() is the single required async entry point.

    Rules of implementors:
    - execute() must return a list (empty on failure, never raise)
    - execute() must catch all internal exceptions and log them
    - required_keys must list every config key the provider needs
    """

    name: ClassVar[str]
    version: ClassVar[str]             = "1.0.0"
    description: ClassVar[str]         = ""
    category: ClassVar[ProviderCategory]
    required_keys: ClassVar[list[str]] = []

    # ----------------------------------------------------------
    # Abstract interface
    # ----------------------------------------------------------

    @abstractmethod
    async def execute(self, query: str) -> list[ProviderResult]:
        """
        Run the provider against a query string.
        Return a list of ProviderResult subclass instances.
        Return an empty list on any failure - never raise.
        """

    # ----------------------------------------------------------
    # Concrete helpers (override if needed)
    # ----------------------------------------------------------

    def is_available(self) -> bool:
        """
        True if all required API keys are present in CONFIGS.
        Override for providers whose availability depends on other factors.
        """
        from eagleosint.config import settings
        return all(settings.get_key(k) for k in self.required_keys)

    def validate_query(self, query: str) -> str | None:
        """
        Optional pre-execution validation.
        Return None if the query is acceptable.
        Return an error message string if it should be rejected.
        """
        if not query or not query.strip():
            return "Query must not be empty"
        return None

    def __repr__(self) -> str:
        return (
            f"<Provider {self.name} v{self.version} "
            f"[{self.category.value}]>"
        )