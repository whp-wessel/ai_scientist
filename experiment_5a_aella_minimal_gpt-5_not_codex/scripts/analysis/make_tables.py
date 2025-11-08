#!/usr/bin/env python3
"""
Create safe public cross-tabulation tables with small-cell suppression.

Example:
  python scripts/analysis/make_tables.py \
    --input childhoodbalancedpublic_original.csv \
    --var1 religion \
    --var2 monogamy \
    --output tables/religion_by_monogamy.csv \
    --threshold 10

Rules:
- Cells with counts < threshold are masked as "<10" (default threshold=10).
- Only counts are reported to minimize disclosure risk.
"""
from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

REPO = Path(__file__).resolve().parents[2]


def mask_count(n: int, threshold: int = 10) -> str:
    return "<10" if n < threshold else str(n)


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--input", required=True)
    p.add_argument("--var1", required=True)
    p.add_argument("--var2", required=True)
    p.add_argument("--output", required=True)
    p.add_argument("--threshold", type=int, default=10)
    args = p.parse_args()

    df = pd.read_csv(REPO / args.input)
    # Drop empty first column if present
    if df.columns[0].strip() == "":
        df = df.drop(columns=df.columns[0])

    if args.var1 not in df.columns or args.var2 not in df.columns:
        raise SystemExit(f"Variables not found: {args.var1}, {args.var2}")

    ct = pd.crosstab(df[args.var1], df[args.var2], dropna=False)
    # Flatten to long format with masking
    rows = []
    for v1 in ct.index.tolist():
        for v2 in ct.columns.tolist():
            n = int(ct.loc[v1, v2])
            rows.append({
                args.var1: "<NA>" if pd.isna(v1) else str(v1),
                args.var2: "<NA>" if pd.isna(v2) else str(v2),
                "count": mask_count(n, args.threshold),
            })

    out_path = REPO / args.output
    out_path.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).to_csv(out_path, index=False)
    print(str(out_path))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

