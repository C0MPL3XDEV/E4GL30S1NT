"""Structured output serialization for ProviderResult objects"""
from __future__ import annotations

import csv
import json
import sys
from typing import TextIO

from eagleosint.models import ProviderResult

def write_results(
        results: list[ProviderResult],
        fmt: str,
        dest: TextIO = sys.stdout
) -> None:
    """
    Serialize results to dest in the requested format.
    Supports: "json", "csv"
    Raises ValueError for unknown formats.
    """
    if not results:
        return

    if fmt == "json":
        payload = [r.model_dump(mode="json") for r in results]
        json.dump(payload, dest, indent=2, default=str)
        dest.write("\n")

    elif fmt == "csv":
        rows = [r.model_dump(mode="csv") for r in results]
        # union of all keys preserves columns across mixed result types
        fieldnames = list(dict.fromkeys(k for row in rows for k in row))
        writer = csv.DictWriter(
            dest, fieldnames=fieldnames,
            extrasaction="ignore", lineterminator="\n"
        )
        writer.writeheader()
        writer.writerows(rows)

    else:
        raise ValueError(f"Unknown format: {fmt}")