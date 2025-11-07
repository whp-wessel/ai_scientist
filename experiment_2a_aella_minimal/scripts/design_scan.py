#!/usr/bin/env python3
"""
Scan the survey dataset header for potential design metadata columns.

Reproducibility:
    python scripts/design_scan.py --csv childhoodbalancedpublic_original.csv
"""
from __future__ import annotations

import argparse
import csv
from pathlib import Path


DEFAULT_KEYWORDS = (
    "weight",
    "strata",
    "cluster",
    "psu",
    "replicate",
    "brr",
    "jk",
    "fpc",
    "stage",
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Inspect column names for survey design metadata."
    )
    parser.add_argument(
        "--csv",
        default="childhoodbalancedpublic_original.csv",
        help="Path to the survey CSV file.",
    )
    parser.add_argument(
        "--keywords",
        nargs="*",
        default=list(DEFAULT_KEYWORDS),
        help="Case-insensitive substrings to search within column names.",
    )
    return parser.parse_args()


def load_header(csv_path: Path) -> list[str]:
    with csv_path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.reader(handle)
        try:
            header = next(reader)
        except StopIteration as exc:
            raise ValueError(f"{csv_path} appears to be empty.") from exc
    return header


def main() -> None:
    args = parse_args()
    csv_path = Path(args.csv).resolve()
    header = load_header(csv_path)
    matches: dict[str, list[str]] = {}

    for keyword in args.keywords:
        keyword_lower = keyword.lower()
        hits = [
            column for column in header if keyword_lower in column.lower()
        ]
        if hits:
            matches[keyword] = hits

    print(f"Scanned file: {csv_path}")
    print(f"Total columns: {len(header)}")
    if not matches:
        print("No columns matched the supplied keywords.")
    else:
        print("Matched columns by keyword:")
        for keyword, hits in matches.items():
            print(f"  {keyword}: {', '.join(hits)}")


if __name__ == "__main__":
    main()
