"""
BaseProvider ABC and ProviderCategory Enum

Every provider plugin must subclass BaseProvider and implement execute().
Migrated: GitHubProvider, BitlyProvider, PhoneInfoProvider,
          IPLocationProvider, DomainInfoProvider, MailFinderProvider,
          UserReconProvider, GoDorkerProvider.
Pending:  Facebook (deprecated API — isolate/remove), TempMail (polling pattern).
"""
from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from enum import Enum
from typing import ClassVar

from eagleosint.models import ProviderResult

logger = logging.getLogger(__name__)


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
    execute() is the abstract entry point that subclasses implement.
    run() wraps execute() with automatic audit logging.

    Rules for implementors:
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
    def execute(self, query: str) -> list[ProviderResult]:
        """
        Run the provider against a query string.
        Return a list of ProviderResult subclass instances.
        Return an empty list on any failure — never raise.
        """

    # ----------------------------------------------------------
    # Audited entry point
    # ----------------------------------------------------------

    def run(self, query: str, **kwargs) -> list[ProviderResult]:
        """Execute the provider with automatic audit logging.

        This is the recommended way to call a provider. It wraps
        execute() with query_start/query_end/query_error audit events.
        """
        from eagleosint.audit import audit_log

        audit_log("query_start", self.name, query)
        try:
            results = self.execute(query, **kwargs)
            audit_log(
                "query_end", self.name, query,
                result_count=len(results), success=True,
            )
            return results
        except Exception as exc:
            logger.error("provider %s failed: %s", self.name, exc)
            audit_log(
                "query_error", self.name, query,
                success=False, extra={"error": str(exc)},
            )
            return []

    # ----------------------------------------------------------
    # Concrete helpers (override if needed)
    # ----------------------------------------------------------

    def is_available(self) -> bool:
        """True if all required API keys are present in config."""
        from eagleosint.config import settings
        return all(settings.get_key(k) for k in self.required_keys)

    def validate_query(self, query: str) -> str | None:
        """Optional pre-execution validation.
        Return None if acceptable, error message string if not.
        """
        if not query or not query.strip():
            return "Query must not be empty"
        return None

    def __repr__(self) -> str:
        return (
            f"<Provider {self.name} v{self.version} "
            f"[{self.category.value}]>"
        )