#!/usr/bin/env python3
"""Generate Loop 002 teen exposure and covariate descriptives."""

from __future__ import annotations

import math
from pathlib import Path

import pandas as pd

DATA_PATH = Path("childhoodbalancedpublic_original.csv")
OUT_DIR = Path("tables")
OUT_DIR.mkdir(parents=True, exist_ok=True)

# Mapping from short variable id to the actual column label in the CSV.
NUMERIC_VARS = {
    "v1k988q": "during ages *13-18*: your parents verbally or emotionally abused you (v1k988q)",
    "dcrx5ab": "during ages *13-18*: Your parents gave useful guidance (dcrx5ab)",
    "classteen": "classteen",
    "classcurrent": "classcurrent",
    "selfage": "selfage",
    "education": "education",
    "gendermale": "gendermale",
    "cis": "cis",
}

CATEGORICAL_VARS = {
    "uky2ksa": "When you were a teen (13-18 years old), your family was (uky2ksa)",
}


def summarize_numeric(df: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, float | int | str | None]] = []
    for var_id, col_label in NUMERIC_VARS.items():
        if col_label not in df.columns:
            raise KeyError(f"Column '{col_label}' not found in dataframe")
        series = df[col_label]
        non_missing = int(series.notna().sum())
        missing_pct = 0.0 if non_missing == len(series) else (1 - non_missing / len(series)) * 100
        mean = series.mean() if non_missing else math.nan
        std = series.std(ddof=0) if non_missing else math.nan
        row = {
            "variable_id": var_id,
            "column_label": col_label,
            "non_missing_n": non_missing,
            "missing_pct": round(missing_pct, 3),
            "mean": round(mean, 3) if non_missing else "",
            "std": round(std, 3) if non_missing else "",
            "min": round(series.min(), 3) if non_missing else "",
            "max": round(series.max(), 3) if non_missing else "",
        }
        rows.append(row)
    return pd.DataFrame(rows)


def summarize_categorical(df: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, str | int | float]] = []
    n = len(df)
    for var_id, col_label in CATEGORICAL_VARS.items():
        if col_label not in df.columns:
            raise KeyError(f"Column '{col_label}' not found in dataframe")
        series = df[col_label]
        counts = series.value_counts(dropna=True)
        for category, count in counts.items():
            if count < 10:
                continue  # suppress small cells per privacy rule
            rows.append(
                {
                    "variable_id": var_id,
                    "column_label": col_label,
                    "category": category,
                    "count": int(count),
                    "share": round(count / n, 4),
                }
            )
    return pd.DataFrame(rows)


def main() -> None:
    df = pd.read_csv(DATA_PATH, low_memory=False)
    numeric_df = summarize_numeric(df)
    categorical_df = summarize_categorical(df)
    numeric_df.to_csv(OUT_DIR / "loop002_teen_covariate_numeric.csv", index=False)
    categorical_df.to_csv(OUT_DIR / "loop002_teen_covariate_categorical.csv", index=False)


if __name__ == "__main__":
    main()
