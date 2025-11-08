#!/usr/bin/env python3
"""
Minimal EDA script for childhoodbalancedpublic_original.csv

Outputs:
- JSON summary with dataset shape, candidate survey design hints, and key vars info
- Public table under tables/key_vars_value_counts.csv with n<10 suppression

Usage:
  python scripts/analysis/eda.py \
    --input childhoodbalancedpublic_original.csv \
    --summary outputs/eda_summary.json \
    --public-counts tables/key_vars_value_counts.csv

Notes:
- Key variables are inferred from analysis/hypotheses.csv (outcomes + predictors).
- Suppression threshold is 10 per AGENTS.md (cells with n < 10 are masked as "<10").
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Iterable, List, Set

import pandas as pd

REPO = Path(__file__).resolve().parents[2]


def read_key_vars(hypotheses_csv: Path) -> List[str]:
    if not hypotheses_csv.exists():
        return []
    df = pd.read_csv(hypotheses_csv)
    cols: Set[str] = set()
    for col in ("outcome_var", "predictor_var", "covariates"):
        if col in df.columns:
            for entry in df[col].dropna().astype(str).tolist():
                # entries may be comma-separated lists
                for token in [t.strip() for t in entry.split(',')]:
                    if token:
                        cols.add(token)
    return sorted(cols)


def infer_design_hints(columns: Iterable[str]) -> List[str]:
    hints = []
    targets = [
        "weight", "weights", "wgt", "wt",
        "strata", "stratum", "strat",
        "psu", "cluster", "primary_sampling_unit",
    ]
    low = [c.lower() for c in columns]
    for t in targets:
        for i, c in enumerate(low):
            if t in c:
                hints.append(f"{columns[i]}")
    return sorted(set(hints))


def mask_counts(n: int, threshold: int = 10) -> str:
    return "<10" if n < threshold else str(n)


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--input", required=True)
    p.add_argument("--summary", required=True)
    p.add_argument("--public-counts", required=True)
    p.add_argument("--hypotheses", default=str(REPO / "analysis" / "hypotheses.csv"))
    p.add_argument("--threshold", type=int, default=10)
    args = p.parse_args()

    data_path = REPO / args.input
    summary_path = REPO / args.summary
    public_counts_path = REPO / args.public_counts
    hypotheses_path = Path(args.hypotheses)

    df = pd.read_csv(data_path)
    # Drop entirely empty unnamed columns if present
    if df.columns[0].strip() == "":
        df = df.drop(columns=df.columns[0])

    key_vars = read_key_vars(hypotheses_path)
    key_vars_existing = [c for c in key_vars if c in df.columns]
    missing_key_vars = [c for c in key_vars if c not in df.columns]

    # Build JSON summary
    design_hints = infer_design_hints(df.columns)
    key_info = {}
    for c in key_vars_existing:
        s = df[c]
        key_info[c] = {
            "non_missing": int(s.notna().sum()),
            "missing": int(s.isna().sum()),
            "unique": int(s.nunique(dropna=True)),
            "dtype": str(s.dtype),
        }

    summary = {
        "dataset": str(data_path.name),
        "rows": int(df.shape[0]),
        "cols": int(df.shape[1]),
        "design_hints": design_hints,
        "key_vars": key_vars_existing,
        "missing_key_vars": missing_key_vars,
        "key_info": key_info,
        "note": "Counts below threshold are suppressed in public tables.",
    }

    summary_path.parent.mkdir(parents=True, exist_ok=True)
    summary_path.write_text(json.dumps(summary, indent=2))

    # Create public counts table for key vars only, with suppression
    rows = []
    for c in key_vars_existing:
        vc = df[c].value_counts(dropna=False)
        for val, n in vc.items():
            label = "<NA>" if pd.isna(val) else str(val)
            rows.append({
                "variable": c,
                "value": label,
                "count": mask_counts(int(n), args.threshold),
            })

    public_counts_path.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).to_csv(public_counts_path, index=False)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

