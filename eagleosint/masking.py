"""PII masking utilities for provider results."""
from __future__ import annotations

import re
from typing import Any

from eagleosint.models import ProviderResult

_EMAIL_RE = re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}")
_PHONE_RE = re.compile(r"\+?\d[\d\s\-()]{6,}\d")
_IP_RE = re.compile(r"\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b")

def mask_email(value: str) -> str:
    local, domain = value.split("@", 1)
    parts = domain.rsplit(".", 1)
    masked_local = local[:3] + "***" if len(local) > 3 else local[0] + "***"
    masked_domain = parts[0][:2] + "***." + parts[1] if len(parts) == 2 else "***"
    return f"{masked_local}@{masked_domain}"

def mask_phone(value: str) -> str:
    digits = re.sub(r"\D", "", value)
    if len(digits) <= 4:
        return value
    return digits[:3] + "*" * (len(digits) - 6) + digits[-3:]

def mask_ip(value: str) -> str:
    octets = value.split(".")
    if len(octets) == 4:
        return f"{octets[0]}.{octets[1]}.*.*"
    return value

def mask_hostname(value: str) -> str:
    parts = value.split(".")
    if len(parts) >= 2:
        return parts[0][:3] + "***." + parts[-1]
    return value[:3] + "***"

def mask_string(text: str) -> str:
    text = _EMAIL_RE.sub(lambda m: mask_email(m.group()), text)
    text = _PHONE_RE.sub(lambda m: mask_phone(m.group()), text)
    text = _IP_RE.sub(lambda m: mask_ip(m.group()), text)
    return text

_PII_FIELDS = {"email", "phone", "ip", "international_number", "hostname", "coordinates"}

def mask_value(value: Any, field_name: str = "") -> Any:
    if isinstance(value, str):
        if field_name == "hostname":
            return mask_hostname(value)
        if field_name in _PII_FIELDS:
            return mask_string(value)
        return value
    if isinstance(value, list):
        return [mask_value(item, field_name) for item in value]
    if isinstance(value, dict):
        return {k: mask_value(v, k) for k, v in value.items()}
    return value

def mask_result(result: ProviderResult) -> dict[str, Any]:
    data = result.model_dump(mode="json")
    return {k: mask_value(v, k) for k, v in data.items()}

def mask_results(results: list[ProviderResult]) -> list[dict[str, Any]]:
    return [mask_result(result) for result in results]

