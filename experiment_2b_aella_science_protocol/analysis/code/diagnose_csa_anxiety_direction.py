#!/usr/bin/env python3
"""
Diagnose the direction of the CSA indicator association with the anxiety outcome.

Regeneration example:
python analysis/code/diagnose_csa_anxiety_direction.py \
    --dataset data/clean/childhoodbalancedpublic_with_csa_indicator.csv \
    --config config/agent_config.yaml \
    --outcome "I tend to suffer from anxiety (npvfh98)-neg" \
    --indicator CSA_score_indicator \
    --out-table tables/diagnostics/csa_anxiety_direction.csv \
    --out-md qc/csa_anxiety_direction.md
"""

from __future__ import annotations

import argparse
import math
import random
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd
import yaml


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Summarise anxiety outcome by CSA indicator and report mean differences."
    )
    parser.add_argument("--dataset", required=True, help="Input CSV dataset path.")
    parser.add_argument(
        "--config", required=True, help="Path to config YAML with seed and thresholds."
    )
    parser.add_argument(
        "--outcome",
        default="I tend to suffer from anxiety (npvfh98)-neg",
        help="Outcome column capturing anxiety tendency (neg-coded).",
    )
    parser.add_argument(
        "--indicator",
        default="CSA_score_indicator",
        help="Binary CSA exposure indicator column (1 = exposure).",
    )
    parser.add_argument(
        "--out-table",
        required=True,
        help="Destination CSV for group summary statistics.",
    )
    parser.add_argument(
        "--out-md",
        required=True,
        help="Destination Markdown file describing diagnostic findings.",
    )
    return parser.parse_args()


def load_config(path: Path) -> tuple[int, int]:
    config = yaml.safe_load(path.read_text())
    seed = int(config.get("seed", 0))
    threshold = int(config.get("small_cell_threshold", 10))
    return seed, threshold


def compute_group_stats(
    df: pd.DataFrame, outcome: str, indicator: str
) -> pd.DataFrame:
    grouped = []
    for level, sub in df.groupby(indicator, dropna=False):
        n = int(sub.shape[0])
        mean = float(sub[outcome].mean())
        std = float(sub[outcome].std(ddof=1))
        se = float(std / math.sqrt(n)) if n > 0 else float("nan")
        ci_half_width = 1.96 * se if not math.isnan(se) else float("nan")
        grouped.append(
            {
                indicator: int(level),
                "n": n,
                "mean": mean,
                "std": std,
                "se": se,
                "ci_low": mean - ci_half_width,
                "ci_high": mean + ci_half_width,
            }
        )
    return pd.DataFrame(grouped).sort_values(indicator).reset_index(drop=True)


def compute_difference(summary: pd.DataFrame, indicator: str) -> pd.Series:
    exposed = summary.loc[summary[indicator] == 1].iloc[0]
    control = summary.loc[summary[indicator] == 0].iloc[0]
    diff = exposed["mean"] - control["mean"]
    se_diff = math.sqrt(exposed["se"] ** 2 + control["se"] ** 2)
    ci_half_width = 1.96 * se_diff
    return pd.Series(
        {
            indicator: "diff_1_minus_0",
            "n": exposed["n"],
            "mean": diff,
            "std": float("nan"),
            "se": se_diff,
            "ci_low": diff - ci_half_width,
            "ci_high": diff + ci_half_width,
        }
    )


def main() -> None:
    args = parse_args()

    dataset_path = Path(args.dataset)
    config_path = Path(args.config)
    out_table_path = Path(args.out_table)
    out_md_path = Path(args.out_md)
    outcome = args.outcome
    indicator = args.indicator

    seed, threshold = load_config(config_path)
    random.seed(seed)
    np.random.seed(seed)

    df = pd.read_csv(dataset_path, low_memory=False)
    missing_columns = [col for col in (outcome, indicator) if col not in df.columns]
    if missing_columns:
        missing_fmt = ", ".join(missing_columns)
        raise ValueError(f"Dataset is missing required columns: {missing_fmt}")

    working = df[[outcome, indicator]].dropna()
    if working.empty:
        raise ValueError("Complete cases for outcome and indicator are empty.")

    # Validate counts exceed suppression threshold.
    counts = working[indicator].value_counts(dropna=False)
    for level, count in counts.items():
        if count < threshold:
            raise ValueError(
                f"Cell count for {indicator}={level} below suppression threshold {threshold}."
            )

    summary = compute_group_stats(working, outcome, indicator)
    diff_row = compute_difference(summary, indicator)
    combined = pd.concat([summary, diff_row.to_frame().T], ignore_index=True)

    out_table_path.parent.mkdir(parents=True, exist_ok=True)
    combined.to_csv(out_table_path, index=False)

    timestamp = datetime.now(timezone.utc).isoformat()
    mean_exposed = summary.loc[summary[indicator] == 1, "mean"].iloc[0]
    mean_control = summary.loc[summary[indicator] == 0, "mean"].iloc[0]

    interpretation = (
        "The anxiety outcome is negative-coded (higher values indicate stronger agreement). "
        "The negative difference implies CSA-exposed respondents report lower agreement with "
        "the anxiety statement."
    )

    md_lines = [
        "# CSA–Anxiety Direction Diagnostics",
        f"Generated: {timestamp} | Seed: {seed}",
        "",
        f"- Outcome column: `{outcome}`",
        f"- Indicator column: `{indicator}`",
        f"- Complete cases analysed: {int(working.shape[0])}",
        "",
        "## Group Means",
        f"- CSA=0 (no exposure): mean = {mean_control:.3f}",
        f"- CSA=1 (reported exposure): mean = {mean_exposed:.3f}",
        "",
        "## Difference (CSA=1 minus CSA=0)",
        f"- Estimate: {diff_row['mean']:.3f}",
        f"- 95% CI: [{diff_row['ci_low']:.3f}, {diff_row['ci_high']:.3f}]",
        "",
        "## Interpretation",
        f"{interpretation}",
    ]

    out_md_path.parent.mkdir(parents=True, exist_ok=True)
    out_md_path.write_text("\n".join(md_lines))


if __name__ == "__main__":
    main()
