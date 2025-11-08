#!/usr/bin/env python3
"""Generate deterministic missingness profiles for the survey dataset.

The output CSV lists every variable with counts and percentages of missing
responses. A companion Markdown stub highlights the top-K variables with the
highest missingness rate (labelled Exploratory per governance instructions).
"""

from __future__ import annotations

import argparse
import csv
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Missingness profile generator.")
    parser.add_argument("--input", required=True, help="Path to the raw CSV dataset.")
    parser.add_argument(
        "--output-csv",
        type=Path,
        required=True,
        help="Path to write the full missingness table (CSV).",
    )
    parser.add_argument(
        "--output-md",
        type=Path,
        required=True,
        help="Path to write a Markdown summary (Exploratory).",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=0,
        help="Seed for deterministic ordering (ties).",
    )
    parser.add_argument(
        "--top-n",
        type=int,
        default=25,
        help="Number of variables to display in the Markdown summary.",
    )
    return parser.parse_args()


def compute_missingness(df: pd.DataFrame) -> list[dict[str, Any]]:
    n_rows = len(df)
    profile: list[dict[str, Any]] = []
    for column in df.columns:
        series = df[column]
        missing = int(series.isna().sum())
        profile.append(
            {
                "variable": column,
                "dtype": str(series.dtype),
                "n_missing": missing,
                "n_obs": int(n_rows - missing),
                "pct_missing": float(missing / n_rows) if n_rows else 0.0,
            }
        )
    return profile


def write_csv(profile: list[dict[str, Any]], output_path: Path):
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", newline="") as f:
        writer = csv.DictWriter(
            f, fieldnames=["variable", "dtype", "n_missing", "n_obs", "pct_missing"]
        )
        writer.writeheader()
        for row in profile:
            writer.writerow(row)


def write_markdown(
    profile: list[dict[str, Any]], output_path: Path, top_n: int, seed: int
):
    rng = np.random.default_rng(seed)
    sorted_profile = sorted(
        profile,
        key=lambda item: (item["pct_missing"], rng.random()),
        reverse=True,
    )
    top = sorted_profile[:top_n]
    lines = [
        "# Missingness Snapshot (Exploratory)",
        "",
        f"- Total variables: {len(profile)}",
        f"- Top {len(top)} listed below (highest missingness first).",
        "",
        "| variable | dtype | n_missing | pct_missing |",
        "| --- | --- | --- | --- |",
    ]
    for row in top:
        lines.append(
            f"| {row['variable']} | {row['dtype']} | {row['n_missing']} | {row['pct_missing']:.4f} |"
        )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(lines))


def main():
    args = parse_args()
    df = pd.read_csv(args.input, low_memory=False)
    profile = compute_missingness(df)
    write_csv(profile, args.output_csv)
    write_markdown(profile, args.output_md, args.top_n, args.seed)


if __name__ == "__main__":
    main()
