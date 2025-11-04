#!/usr/bin/env python3
"""
Summarise missingness patterns for candidate social support predictors.

Regeneration example:
python analysis/code/social_support_missingness.py \
    --dataset data/clean/childhoodbalancedpublic_with_csa_indicator.csv \
    --out-csv tables/social_support_missingness.csv \
    --config config/agent_config.yaml
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List

import pandas as pd
import yaml


DEFAULT_COLUMNS: List[str] = [
    "In general, people in my *current* social circles tend treat me really well (tmt46e6)",
    "In general, people in my *current* social circles tend to treat me really well (71mn55g)",
    "In general, people in my *current* social circles tend treat me really well",
    "In general, people in my *current* social circles tend to treat me really well",
]


@dataclass
class Config:
    seed: int = 0
    small_cell_threshold: int = 10


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Compute summary statistics for social support predictor coverage."
    )
    parser.add_argument("--dataset", required=True, help="Input CSV dataset path.")
    parser.add_argument(
        "--out-csv",
        required=True,
        help="Destination CSV with missingness summary.",
    )
    parser.add_argument(
        "--columns",
        nargs="+",
        default=DEFAULT_COLUMNS,
        help="Column names to profile (default matches current hypotheses).",
    )
    parser.add_argument(
        "--config", required=False, help="Optional config YAML to capture metadata."
    )
    return parser.parse_args()


def load_config(path: str | None) -> Config:
    if path is None:
        return Config()
    config_path = Path(path)
    data = yaml.safe_load(config_path.read_text())
    return Config(
        seed=int(data.get("seed", 0)),
        small_cell_threshold=int(data.get("small_cell_threshold", 10)),
    )


def sanitise_columns(columns: Iterable[str]) -> List[str]:
    """Drop duplicates while preserving order."""
    seen = set()
    ordered = []
    for col in columns:
        if col not in seen:
            seen.add(col)
            ordered.append(col)
    return ordered


def build_summary(
    df: pd.DataFrame, columns: Iterable[str], threshold: int
) -> pd.DataFrame:
    rows = []
    total = len(df)
    for col in columns:
        available = missing = unique = suppression = None
        if col in df.columns:
            series = df[col]
            missing = int(series.isna().sum())
            available = total - missing
            unique = int(series.nunique(dropna=True))
            suppression = "ok" if available >= threshold else "review"
        else:
            missing = total
            available = 0
            unique = 0
            suppression = "missing_column"
        rows.append(
            {
                "variable": col,
                "available_obs": available,
                "missing_obs": missing,
                "missing_pct": round(missing / total, 6) if total else None,
                "unique_values": unique,
                "disclosure_check": suppression,
            }
        )
    return pd.DataFrame(rows)


def main() -> None:
    args = parse_args()
    config = load_config(args.config)

    dataset_path = Path(args.dataset)
    out_path = Path(args.out_csv)

    df = pd.read_csv(dataset_path, low_memory=False)
    columns = sanitise_columns(args.columns)
    summary = build_summary(df, columns, config.small_cell_threshold)
    summary.to_csv(out_path, index=False)


if __name__ == "__main__":
    main()
