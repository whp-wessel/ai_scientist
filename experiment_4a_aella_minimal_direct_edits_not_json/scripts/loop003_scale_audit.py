#!/usr/bin/env python3
"""Diagnose Likert polarity and export alignment diagnostics for Loop 003."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from likert_utils import align_likert, ensure_columns, get_likert_specs

DATA_PATH = Path("childhoodbalancedpublic_original.csv")
TABLES_DIR = Path("tables")
TABLES_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_PATH = TABLES_DIR / "loop003_likert_alignment.csv"


def describe(series: pd.Series) -> dict[str, float]:
    series = series.dropna()
    return {
        "mean": series.mean(),
        "std": series.std(ddof=0),
        "min": series.min(),
        "max": series.max(),
    }


def main() -> None:
    df = pd.read_csv(DATA_PATH, low_memory=False)
    specs = get_likert_specs()
    ensure_columns(df, specs)

    aligned = align_likert(df, specs)
    rows: list[dict[str, object]] = []
    for spec in specs:
        raw_series = df[spec.column]
        aligned_series = aligned[spec.aligned_column]
        raw_stats = describe(raw_series)
        aligned_stats = describe(aligned_series)
        rows.append(
            {
                "variable_id": spec.variable_id,
                "column_label": spec.column,
                "concept": spec.concept,
                "flip_sign": spec.flip_sign,
                "raw_mean": raw_stats["mean"],
                "raw_std": raw_stats["std"],
                "raw_min": raw_stats["min"],
                "raw_max": raw_stats["max"],
                "aligned_mean": aligned_stats["mean"],
                "aligned_std": aligned_stats["std"],
                "aligned_min": aligned_stats["min"],
                "aligned_max": aligned_stats["max"],
                "note": "Aligned value = raw * -1 (since survey encodes Strongly Agree = -3).",
            }
        )

    pd.DataFrame(rows).to_csv(OUTPUT_PATH, index=False)


if __name__ == "__main__":
    main()
