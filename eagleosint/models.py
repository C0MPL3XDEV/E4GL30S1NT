from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

def _utcnow() -> datetime:
    return datetime.now(timezone.utc)

# ----------------------------------------------------------------------
# Enums
# ----------------------------------------------------------------------

class Confidence(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    UNKNOWN = "unknown"

class EmailStatus(str, Enum):
    VALID = "valid"
    INVALID = "invalid"
    UNKNOWN = "unknown"

class AccountStatus(str, Enum):
    FOUND = "found"
    NOT_FOUND = "not_found"
    UNKNOWN = "unknown"


# ----------------------------------------------------------------------
# Base
# ----------------------------------------------------------------------

class ProviderResult(BaseModel):
    """Base for every result returned by a provider."""
    source: str
    query: str
    timestamp: datetime = Field(default_factory=_utcnow)
    confidence: Confidence = Confidence.UNKNOWN
    raw: dict[str, Any] | None = None


# ----------------------------------------------------------------------
# Provider-specific results
# ----------------------------------------------------------------------

class AccountHit(ProviderResult):
    """Username probe result on a single platform."""
    source: str = "userrecon"
    platform: str
    url: str
    status: AccountStatus
    http_status_code: int

class EmailResult(ProviderResult):
    """Email address with validation status from isitrealmail.com."""
    source: str = "mailfinder"
    email: str
    status: EmailStatus


class PhoneResult(ProviderResult):
    """Phone number intelligence from Veriphone API."""
    model_config = ConfigDict(extra="allow")  # preserve undocumented API fields
    source:               str = "phoneinfo"
    phone:                str
    phone_valid:          bool | None = None
    country:              str | None = None
    country_code:         str | None = None
    carrier:              str | None = None
    line_type:            str | None = None
    international_number: str | None = None


class IPResult(ProviderResult):
    """IP geolocation result from ipinfo.io."""
    source:      str = "network"
    ip:          str
    city:        str | None = None
    region:      str | None = None
    country:     str | None = None
    coordinates: str | None = None   # ipinfo "loc" field: "lat,lon"
    org:         str | None = None   # ASN + organisation name
    timezone:    str | None = None
    hostname:    str | None = None


class DomainResult(ProviderResult):
    """HackerTarget API result for a domain or IP (DNS, WHOIS, etc.)."""
    source:     str = "network"
    query_type: str                          # "dnslookup" | "whois" | "hostsearch" | ...
    records:    list[str] = Field(default_factory=list)


class GitHubProfile(ProviderResult):
    """GitHub user profile from the public REST API."""
    model_config = ConfigDict(extra="allow")
    source:       str = "github"
    username:     str
    name:         str | None = None
    email:        str | None = None
    bio:          str | None = None
    location:     str | None = None
    company:      str | None = None
    blog:         str | None = None
    public_repos: int | None = None
    followers:    int | None = None
    following:    int | None = None
    created_at:   str | None = None
    avatar_url:   str | None = None
    html_url:     str | None = None

class DorkResult(ProviderResult):
    """A single URL result from a Google dork query."""
    source: str = "godorker"
    url:    str
    title:  str | None = None


class URLExpansion(ProviderResult):
    """Resolved original URL from a shortener."""
    source:       str = "bitly"
    short_url:    str
    original_url: str


# ----------------------------------------------------------------------
# Investigation container (in-memory for now; persistence comes later)
# ----------------------------------------------------------------------

class Investigation(BaseModel):
    """Named investigation session holding all results from a case."""
    name:       str
    created_at: datetime       = Field(default_factory=_utcnow)
    tags:       list[str]      = Field(default_factory=list)
    notes:      str            = ""
    results:    list[ProviderResult] = Field(default_factory=list)

    def add(self, result: ProviderResult) -> None:
        self.results.append(result)

    def by_source(self, source: str) -> list[ProviderResult]:
        return [r for r in self.results if r.source == source]