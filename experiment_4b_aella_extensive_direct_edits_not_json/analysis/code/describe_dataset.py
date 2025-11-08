#!/usr/bin/env python3
"""Summarize core dataset structure for reproducibility dashboards.

The script reads the survey dataset, computes descriptive metadata such as row/column
counts, missingness, and dtype distributions, and emits both JSON and Markdown reports.

Example
-------
python analysis/code/describe_dataset.py \
  --input data/raw/childhoodbalancedpublic_original.csv \
  --seed 20251016 \
  --output-json artifacts/describe_dataset_loop002.json \
  --output-md qc/data_overview_loop002.md
"""

from __future__ import annotations

import argparse
import json
import random
from pathlib import Path

import numpy as np
import pandas as pd


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Dataset structure summary utility.")
    parser.add_argument("--input", required=True, help="Path to the CSV dataset.")
    parser.add_argument("--seed", type=int, default=0, help="Random seed for reproducibility.")
    parser.add_argument(
        "--output-json",
        type=Path,
        required=True,
        help="Path to write the structured JSON summary.",
    )
    parser.add_argument(
        "--output-md",
        type=Path,
        help="Optional path to write a Markdown summary for QC folders.",
    )
    parser.add_argument(
        "--top-missing",
        type=int,
        default=20,
        help="Number of variables to highlight in the missingness table.",
    )
    return parser.parse_args()


def summarize_dataframe(df: pd.DataFrame, top_missing: int) -> dict:
    n_rows, n_cols = df.shape
    missing_fraction = float(df.isna().mean().mean())
    memory_mb = float(df.memory_usage(deep=True).sum() / 1_000_000)

    dtype_counts = df.dtypes.astype(str).value_counts().to_dict()

    column_details: list[dict] = []
    for col in df.columns:
        series = df[col]
        detail = {
            "name": col,
            "dtype": str(series.dtype),
            "missing_fraction": float(series.isna().mean()),
        }
        if pd.api.types.is_numeric_dtype(series):
            detail["min"] = float(series.min(skipna=True)) if series.notna().any() else None
            detail["max"] = float(series.max(skipna=True)) if series.notna().any() else None
        column_details.append(detail)

    top_missing_cols = sorted(
        column_details,
        key=lambda item: item["missing_fraction"],
        reverse=True,
    )[:top_missing]

    return {
        "rows": int(n_rows),
        "columns": int(n_cols),
        "missing_fraction": missing_fraction,
        "memory_mb": memory_mb,
        "dtype_counts": dtype_counts,
        "top_missing": top_missing_cols,
        "column_details": column_details,
    }


def write_markdown(summary: dict, output_path: Path):
    lines = [
        "# Data Overview (Automated)",
        "",
        f"- Rows: {summary['rows']}",
        f"- Columns: {summary['columns']}",
        f"- Mean missingness: {summary['missing_fraction']:.4f}",
        f"- Approx. memory footprint: {summary['memory_mb']:.2f} MB",
        "",
        "## Dtype distribution",
    ]
    for dtype, count in summary["dtype_counts"].items():
        lines.append(f"- {dtype}: {count}")

    lines.append("")
    lines.append("## Top variables by missingness")
    lines.append("| variable | dtype | missing_fraction |")
    lines.append("| --- | --- | --- |")
    for item in summary["top_missing"]:
        lines.append(
            f"| {item['name']} | {item['dtype']} | {item['missing_fraction']:.4f} |"
        )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(lines))


def main():
    args = parse_args()
    random.seed(args.seed)
    np.random.seed(args.seed)

    input_path = Path(args.input)
    if not input_path.exists():
        raise FileNotFoundError(f"Input dataset not found: {input_path}")

    df = pd.read_csv(input_path)
    summary = summarize_dataframe(df, args.top_missing)
    summary.update(
        {
            "input_path": str(input_path),
            "seed": args.seed,
            "top_missing_limit": args.top_missing,
        }
    )

    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    args.output_json.write_text(json.dumps(summary, indent=2))

    if args.output_md:
        write_markdown(summary, args.output_md)


if __name__ == "__main__":
    main()
