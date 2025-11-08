#!/usr/bin/env python3
"""
Extract DOIs from a saved Semantic Scholar search JSON and append them to lit/evidence_map.csv.

Usage:
  python scripts/lit/extract_dois.py \
    --input lit/queries/loop_007/query_001.json \
    --output lit/evidence_map.csv \
    --topic "childhood religiosity and wellbeing"

Notes:
  - Skips DOIs already present in the evidence map (by exact DOI string).
  - Generates incremental IDs like E2, E3, ... based on existing rows.
  - Adds a brief note with the paper title and source JSON path.
"""
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Dict, List, Tuple

REPO = Path(__file__).resolve().parents[2]


def read_existing_map(path: Path) -> Tuple[List[Dict[str, str]], set]:
    rows: List[Dict[str, str]] = []
    existing_dois: set = set()
    if path.exists():
        with path.open("r", newline="") as f:
            r = csv.DictReader(f)
            for row in r:
                rows.append(row)
                doi = (row.get("doi") or "").strip()
                if doi:
                    existing_dois.add(doi)
    return rows, existing_dois


def next_id(existing: List[Dict[str, str]]) -> str:
    max_n = 0
    for row in existing:
        rid = (row.get("id") or "").strip()
        if rid.startswith("E"):
            try:
                n = int(rid[1:])
                if n > max_n:
                    max_n = n
            except ValueError:
                continue
    return f"E{max_n + 1}"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True)
    ap.add_argument("--output", default=str(REPO / "lit" / "evidence_map.csv"))
    ap.add_argument("--topic", default="childhood religiosity and wellbeing")
    args = ap.parse_args()

    src = REPO / args.input
    out_path = REPO / args.output

    data = json.loads(src.read_text())
    results = data.get("data") or []

    existing_rows, existing_dois = read_existing_map(out_path)
    new_rows: List[Dict[str, str]] = []

    for item in results:
        ext = item.get("externalIds") or {}
        doi = (ext.get("DOI") or "").strip()
        if not doi or doi in existing_dois:
            continue
        rid = next_id(existing_rows + new_rows)
        url = f"https://doi.org/{doi}"
        title = (item.get("title") or "").strip()
        note = f"title: {title}; source: {args.input}"
        new_rows.append({
            "id": rid,
            "doi": doi,
            "url": url,
            "topic": args.topic,
            "notes": note,
        })

    # Write (append) with header if needed
    out_path.parent.mkdir(parents=True, exist_ok=True)
    write_header = not out_path.exists() or out_path.read_text().strip() == ""
    with out_path.open("a", newline="") as f:
        fieldnames = ["id", "doi", "url", "topic", "notes"]
        w = csv.DictWriter(f, fieldnames=fieldnames)
        if write_header:
            w.writeheader()
        for row in new_rows:
            w.writerow(row)

    print(f"Appended {len(new_rows)} DOI(s) to {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

