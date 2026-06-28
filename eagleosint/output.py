"""Structured output serialization for ProviderResult objects"""
from __future__ import annotations

import csv
import json
import sys
from typing import TextIO, Any

from eagleosint.masking import mask_result, mask_results
from eagleosint.models import ProviderResult

def write_results(
        results: list[ProviderResult],
        fmt: str,
        dest: TextIO = sys.stdout,
        show_pii: bool = False
) -> None:
    """
    Serialize results to dest in the requested format.
    Supports: "json", "csv"
    Raises ValueError for unknown formats.
    """
    if not results:
        return

    rows: list[dict[str, Any]]
    if show_pii:
        rows = [r.model_dump(mode="json") for r in results]
    else:
        rows = mask_results(results)

    if fmt == "json":
        json.dump(rows, dest, indent=2, default=str)
        dest.write("\n")

    elif fmt == "csv":
        fieldnames = list(dict.fromkeys(k for row in rows for k in row))
        writer = csv.DictWriter(
            dest, fieldnames=fieldnames,
            extrasaction="ignore", lineterminator="\n"
        )
        writer.writeheader()
        writer.writerows(rows)
    else:
        raise ValueError(f"unsupported output format: {fmt!r}")