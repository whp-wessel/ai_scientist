#!/usr/bin/env python3
"""
Summarise CSA–anxiety outcome differences across analytic subgroups.

Example:
python analysis/code/anxiety_subgroup_summary.py \
    --dataset data/clean/childhoodbalancedpublic_with_csa_indicator.csv \
    --config config/agent_config.yaml \
    --out-table tables/diagnostics/anxiety_subgroup_summary.csv \
    --out-md qc/anxiety_subgroup_summary.md
"""

from __future__ import annotations

import argparse
import random
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Iterable, List

import numpy as np
import pandas as pd
import yaml


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Summarise CSA–anxiety differences across key subgroups."
    )
    parser.add_argument("--dataset", required=True, help="CSV or Parquet dataset.")
    parser.add_argument("--config", required=True, help="YAML config with seed info.")
    parser.add_argument(
        "--out-table",
        required=True,
        help="Destination CSV for subgroup statistics.",
    )
    parser.add_argument(
        "--out-md",
        help="Optional Markdown summary output.",
    )
    parser.add_argument(
        "--outcome",
        default="I tend to suffer from anxiety (npvfh98)-neg",
        help="Ordinal anxiety outcome column (negative-coded).",
    )
    parser.add_argument(
        "--csa",
        default="CSA_score_indicator",
        help="Binary CSA exposure indicator.",
    )
    return parser.parse_args()


def load_config(path: Path) -> Dict:
    config = yaml.safe_load(path.read_text())
    if not isinstance(config, dict):
        raise ValueError("Configuration file must be a mapping.")
    return config


def seed_everything(seed: int) -> None:
    random.seed(seed)
    np.random.seed(seed)


def load_dataset(path: Path) -> pd.DataFrame:
    if path.suffix.lower() == ".csv":
        return pd.read_csv(path, low_memory=False)
    if path.suffix.lower() in {".parquet", ".pq"}:
        return pd.read_parquet(path)
    raise ValueError(f"Unsupported dataset format: {path.suffix}")


def ensure_columns(df: pd.DataFrame, columns: Iterable[str]) -> None:
    missing = [col for col in columns if col not in df.columns]
    if missing:
        raise ValueError(f"Dataset missing required columns: {', '.join(missing)}")


def label_binary(series: pd.Series, true_label: str, false_label: str) -> pd.Series:
    mapping = {1: true_label, 1.0: true_label, 0: false_label, 0.0: false_label}
    return series.map(mapping)


def make_age_cohort(series: pd.Series) -> pd.Series:
    bins = [18, 30, 45, 60, 200]
    labels = ["18-29", "30-44", "45-59", "60+"]
    return pd.cut(series, bins=bins, labels=labels, right=False, include_lowest=True)


def make_class_group(series: pd.Series) -> pd.Series:
    bins = [-1, 1, 3, 7]
    labels = ["Lower (0-1)", "Middle (2-3)", "Upper (4-6)"]
    return pd.cut(series, bins=bins, labels=labels, include_lowest=True)


def summarise_subgroup(
    df: pd.DataFrame,
    subgroup_column: str,
    subgroup_label: str,
    outcome: str,
    csa: str,
    threshold: int,
) -> pd.DataFrame:
    stats = (
        df.groupby([subgroup_column, csa], dropna=False)[outcome]
        .agg(["count", "mean", "std"])
        .reset_index()
    )
    if stats["count"].min() < threshold:
        offender = stats.loc[stats["count"].idxmin()]
        raise ValueError(
            f"Cell count below {threshold} for {subgroup_label}="
            f"{offender[subgroup_column]!r}, CSA={offender[csa]!r}"
        )
    stats.insert(0, "subgroup_var", subgroup_label)
    stats = stats.rename(
        columns={
            subgroup_column: "subgroup_level",
            csa: "CSA_exposed",
            "count": "n",
            "mean": "mean_anxiety",
            "std": "sd_anxiety",
        }
    )
    stats["CSA_exposed"] = stats["CSA_exposed"].map({0: "No", 0.0: "No", 1: "Yes", 1.0: "Yes"})
    stats["subgroup_level"] = stats["subgroup_level"].astype("object").fillna("Missing")
    return stats


def dataframe_to_markdown(df: pd.DataFrame) -> str:
    headers = list(df.columns)
    lines = ["| " + " | ".join(headers) + " |", "| " + " | ".join(["---"] * len(headers)) + " |"]
    for _, row in df.iterrows():
        values = [("" if pd.isna(val) else str(val)) for val in row.tolist()]
        lines.append("| " + " | ".join(values) + " |")
    return "\n".join(lines)


def write_markdown(
    path: Path,
    timestamp: str,
    outcome: str,
    csa: str,
    summaries: pd.DataFrame,
    command: str,
) -> None:
    sections = [
        "# Anxiety Subgroup Summary",
        f"Generated: {timestamp}",
        "",
        f"- Outcome: `{outcome}`",
        f"- CSA indicator: `{csa}`",
        "",
        "## Subgroup statistics",
        "",
    ]
    for subgroup in summaries["subgroup_var"].unique():
        block = summaries[summaries["subgroup_var"] == subgroup].drop(columns=["subgroup_var"])
        block = block.sort_values(["subgroup_level", "CSA_exposed"])
        sections.append(f"### {subgroup}")
        sections.append("")
        sections.append(dataframe_to_markdown(block))
        sections.append("")
    sections.extend(
        [
            "## Reproducibility",
            f"- Command: `{command}`",
        ]
    )
    path.write_text("\n".join(sections))


def main() -> None:
    args = parse_args()
    dataset_path = Path(args.dataset)
    config_path = Path(args.config)
    out_table = Path(args.out_table)
    out_md = Path(args.out_md) if args.out_md else None

    config = load_config(config_path)
    seed = int(config.get("seed", 20251016))
    threshold = int(config.get("small_cell_threshold", 10))
    seed_everything(seed)

    df = load_dataset(dataset_path)
    ensure_columns(df, [args.outcome, args.csa, "gendermale", "cis", "selfage", "classchild"])
    df = df.dropna(subset=[args.outcome, args.csa]).copy()

    df["gender_group"] = label_binary(df["gendermale"], "Male", "Not male")
    df["cis_group"] = label_binary(df["cis"], "Cis", "Not cis")
    df["age_cohort"] = make_age_cohort(df["selfage"])
    df["classchild_group"] = make_class_group(df["classchild"])

    subgroup_specs: List[tuple[str, str]] = [
        ("gender_group", "Gender (male vs not male)"),
        ("cis_group", "Cisgender identity"),
        ("age_cohort", "Age cohort"),
        ("classchild_group", "Childhood class level"),
    ]

    summaries = []
    for column, label in subgroup_specs:
        stats = summarise_subgroup(df, column, label, args.outcome, args.csa, threshold)
        summaries.append(stats)

    result = pd.concat(summaries, ignore_index=True)
    timestamp = datetime.now(timezone.utc).isoformat()
    result["generated_at"] = timestamp
    result["seed"] = seed

    out_table.parent.mkdir(parents=True, exist_ok=True)
    result.to_csv(out_table, index=False)

    if out_md:
        command = (
            "python analysis/code/anxiety_subgroup_summary.py "
            f"--dataset {dataset_path} "
            f"--config {config_path} "
            f"--out-table {out_table} "
            f"--out-md {out_md}"
        )
        out_md.parent.mkdir(parents=True, exist_ok=True)
        write_markdown(out_md, timestamp, args.outcome, args.csa, result, command)


if __name__ == "__main__":
    main()
