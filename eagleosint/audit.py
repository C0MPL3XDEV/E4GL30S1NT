"""Append-only audit log for all provider queries.

Every provider execution is recorded as a JSON Lines entry.
The log is immutable by design: opened in append-only mode.
Queries are SHA256-hashed to avoid storing PII in plaintext.
"""
from __future__ import annotations

import hashlib
import json
import os
import uuid
from datetime import datetime, timezone
from typing import Any

from platformdirs import user_data_dir

# Audit log lives in the data directory, not config
_DATA_DIR = user_data_dir("eagleosint", appauthor=False)
AUDIT_LOG_PATH = os.path.join(_DATA_DIR, "audit.jsonl")

os.makedirs(_DATA_DIR, exist_ok=True)

# Session ID: unique per process run - groups all queries from one session
SESSION_ID = uuid.uuid4().hex[:12]

def _hash_query(query: str) -> str:
    """SHA256 hash of the query string - PII never stored in plaintext."""
    return hashlib.sha256(query.encode("utf-8")).hexdigest()

def audit_log(
        event: str,
        provider: str,
        query: str,
        *,
        result_count: int | None = None,
        success: bool = True,
        extra: dict[str, Any] | None = None
) -> None:
    """Append a single audit entry to the log file.

    Args:
        event: Event type -- "query_start", "query_end", "query_error".
        provider: Provider name (e.g. "github", "userrecon").
        query: Raw query string — will be hashed before writing.
        result_count: Number of results returned (for query_end).
        success: Whether the query succeeded.
        extra: Optional additional metadata.
    """
    entry: dict[str, Any] = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "session_id": SESSION_ID,
        "event": event,
        "provider": provider,
        "query_hash": _hash_query(query),
        "success": success,
    }
    if result_count is not None:
        entry["result_count"] = result_count
    if extra is not None:
        entry["extra"] = extra

    with open(AUDIT_LOG_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, separators=(",", ":")) + "\n")