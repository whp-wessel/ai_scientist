"""Compare aggregated diagnostics between two multiply-imputed runs.

The script ingests run-level summary CSVs produced by `mice_prototype.py`
and generates a reproducible comparison table/markdown report that highlight
mean and standard-deviation shifts across overlapping variables.

Usage
-----
python analysis/code/compare_imputation_runs.py \
    --summary-a analysis/imputation/mice_imputation_summary.csv \
    --summary-b analysis/imputation/mice_imputation_summary__reduced_aux.csv \
    --label-a prototype \
    --label-b reduced_aux \
    --csv-out tables/imputation_run_comparison__prototype_vs_reduced_aux.csv \
    --md-out analysis/imputation/imputation_run_comparison__prototype_vs_reduced_aux.md
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

SHIFT_ALERT_THRESHOLD = 15.0  # percent change threshold for alerting


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Compare two imputation summary tables")
    parser.add_argument("--summary-a", type=Path, required=True, help="CSV summary for baseline run")
    parser.add_argument("--summary-b", type=Path, required=True, help="CSV summary for comparison run")
    parser.add_argument("--label-a", type=str, required=True, help="Label describing baseline run")
    parser.add_argument("--label-b", type=str, required=True, help="Label describing comparison run")
    parser.add_argument("--csv-out", type=Path, required=True, help="Output CSV path for merged comparison table")
    parser.add_argument("--md-out", type=Path, required=True, help="Output Markdown summary path")
    parser.add_argument("--seed", type=int, default=20251016, help="Logged seed (no randomness used)")
    return parser.parse_args()


def compute_percent_change(a: float, b: float) -> float:
    if np.isnan(a) or np.isnan(b) or b == 0:
        return np.nan
    return (a - b) / abs(b) * 100.0


def main() -> None:
    args = parse_args()

    df_a = pd.read_csv(args.summary_a)
    df_b = pd.read_csv(args.summary_b)

    merged = df_a.merge(df_b, on="variable", how="outer", suffixes=(f"__{args.label_a}", f"__{args.label_b}"))

    # Identify columns that do not overlap across runs.
    only_in_a = merged[merged[f"mean_after__{args.label_b}"].isna()]["variable"].dropna().tolist()
    only_in_b = merged[merged[f"mean_after__{args.label_a}"].isna()]["variable"].dropna().tolist()

    merged[f"delta_mean__{args.label_b}_minus_{args.label_a}"] = (
        merged[f"mean_after__{args.label_b}"] - merged[f"mean_after__{args.label_a}"]
    )
    merged[f"delta_sd__{args.label_b}_minus_{args.label_a}"] = (
        merged[f"sd_after__{args.label_b}"] - merged[f"sd_after__{args.label_a}"]
    )
    merged[f"pct_change_mean__{args.label_b}_vs_{args.label_a}"] = merged.apply(
        lambda row: compute_percent_change(row[f"mean_after__{args.label_b}"], row[f"mean_after__{args.label_a}"]),
        axis=1,
    )

    merged.sort_values("variable", inplace=True)
    args.csv_out.parent.mkdir(parents=True, exist_ok=True)
    merged.to_csv(args.csv_out, index=False)

    timestamp = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

    md_lines = [
        "# Imputation Run Comparison (Exploratory)",
        "",
        f"- Completed: {timestamp}",
        f"- Baseline summary (`label_a`): `{args.summary_a}` ({args.label_a})",
        f"- Comparison summary (`label_b`): `{args.summary_b}` ({args.label_b})",
        f"- Output CSV: `{args.csv_out}`",
        f"- Seed (logged): {args.seed}",
        "- No randomness introduced; deterministic join of summary tables.",
        "",
        "## Key Findings",
    ]

    alert_rows = merged[
        merged[f"pct_change_mean__{args.label_b}_vs_{args.label_a}"].abs() > SHIFT_ALERT_THRESHOLD
    ]["variable"].dropna().tolist()

    if alert_rows:
        for var in sorted(set(alert_rows)):
            md_lines.append(
                f"- Mean shift exceeds {SHIFT_ALERT_THRESHOLD:.0f}% for `{var}` when comparing {args.label_b} against {args.label_a}."
            )
    else:
        md_lines.append(
            f"- No variables show mean shifts beyond {SHIFT_ALERT_THRESHOLD:.0f}% between `{args.label_b}` and `{args.label_a}` runs."
        )

    if only_in_a:
        md_lines.append(
            f"- Variables only present in `{args.label_a}` run (dropped in `{args.label_b}`): {', '.join(sorted(set(only_in_a)))}."
        )
    if only_in_b:
        md_lines.append(
            f"- Variables unique to `{args.label_b}` run (missing from `{args.label_a}`): {', '.join(sorted(set(only_in_b)))}."
        )

    md_lines.extend(
        [
            "",
            "## Regeneration",
            "```bash",
            f"python analysis/code/compare_imputation_runs.py --summary-a {args.summary_a} --summary-b {args.summary_b} --label-a {args.label_a} --label-b {args.label_b} --csv-out {args.csv_out} --md-out {args.md_out} --seed {args.seed}",
            "```",
        ]
    )

    args.md_out.parent.mkdir(parents=True, exist_ok=True)
    args.md_out.write_text("\n".join(md_lines))


if __name__ == "__main__":
    main()
