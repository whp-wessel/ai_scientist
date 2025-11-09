#!/usr/bin/env python3
"""Build publication-ready summary table from the BH-adjusted results."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

import pandas as pd


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Create tables/results_summary.* from analysis/results.csv")
    parser.add_argument(
        "--input",
        default="analysis/results.csv",
        help="BH-adjusted results file.",
    )
    parser.add_argument(
        "--output-csv",
        default="tables/results_summary.csv",
        help="CSV output path.",
    )
    parser.add_argument(
        "--output-md",
        default="tables/results_summary.md",
        help="Markdown summary path.",
    )
    return parser.parse_args()


def build_ci(row: pd.Series) -> str:
    low = float(row["ci_low"])
    high = float(row["ci_high"])
    return f"[{low:.3f}, {high:.3f}]"


def sanitize(value: Any) -> str:
    return str(value).replace("|", "\\|")


def main() -> None:
    args = parse_args()
    df = pd.read_csv(args.input)
    targeted_mask = df["targeted"].astype(str).str.upper() == "Y"
    targeted = df.loc[targeted_mask].copy()
    if targeted.empty:
        raise ValueError("No targeted hypotheses found in results file.")
    targeted["ci_range"] = targeted.apply(build_ci, axis=1)
    columns = [
        "hypothesis_id",
        "effect_size_metric",
        "estimate",
        "ci_range",
        "q_value",
        "n_unweighted",
        "confidence_rating",
        "limitations",
    ]
    table = targeted[columns]
    output_csv = Path(args.output_csv)
    output_csv.parent.mkdir(parents=True, exist_ok=True)
    table.to_csv(output_csv, index=False)

    header = "| Hypothesis | Effect metric | Estimate | 95% CI | q-value | n | Confidence | Limitations |"
    separator = "| --- | --- | --- | --- | --- | --- | --- | --- |"
    rows = []
    for row in table.itertuples(index=False):
        q_value = f"{float(row.q_value):.4g}"
        rows.append(
            "| "
            f"{sanitize(row.hypothesis_id)} | {sanitize(row.effect_size_metric)} | {row.estimate:.3f} | "
            f"{sanitize(row.ci_range)} | {q_value} | {int(row.n_unweighted)} | "
            f"{sanitize(row.confidence_rating)} | {sanitize(row.limitations or '')} |"
        )
    output_md = Path(args.output_md)
    output_md.parent.mkdir(parents=True, exist_ok=True)
    output_md.write_text("\n".join([header, separator, *rows]) + "\n")


if __name__ == "__main__":
    main()
