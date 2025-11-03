#!/usr/bin/env python3
"""Generate exploratory (design-aware) summaries for key survey outcomes.

This script is deterministic and intended for reproducible exploratory analysis.
It produces:
  1. A summary table with weighted descriptive statistics per outcome.
  2. A distribution table with weighted response frequencies (small-cell suppressed).

Example:
python analysis/code/eda_weighted_summaries.py \
    --dataset childhoodbalancedpublic_original.csv \
    --codebook docs/codebook.json \
    --config config/agent_config.yaml \
    --out-summary tables/exploratory_outcome_summary.csv \
    --out-distribution tables/exploratory_outcome_distribution.csv
"""

from __future__ import annotations

import argparse
import json
import math
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable, List, Tuple

import numpy as np
import pandas as pd
import yaml


DEFAULT_OUTCOMES: Tuple[str, ...] = (
    "I love myself (2l8994l)",
    "I tend to suffer from depression (wz901dj)",
    "I tend to suffer from anxiety (npvfh98)-neg",
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Create exploratory weighted summaries for key survey outcomes."
    )
    parser.add_argument("--dataset", required=True, help="Path to survey microdata (CSV/Parquet).")
    parser.add_argument("--codebook", required=True, help="Path to JSON codebook for labels.")
    parser.add_argument("--config", required=True, help="Path to agent configuration YAML.")
    parser.add_argument(
        "--out-summary",
        default="tables/exploratory_outcome_summary.csv",
        help="Output CSV path for summary statistics.",
    )
    parser.add_argument(
        "--out-distribution",
        default="tables/exploratory_outcome_distribution.csv",
        help="Output CSV path for response distributions.",
    )
    parser.add_argument(
        "--outcomes",
        nargs="+",
        default=list(DEFAULT_OUTCOMES),
        help="Column names to summarise. Defaults to key outcomes tracked in hypotheses.",
    )
    parser.add_argument(
        "--weight",
        default=None,
        help="Optional weight column name. If omitted or null in survey design, uniform weights are used.",
    )
    parser.add_argument(
        "--timestamp",
        default=datetime.now(tz=timezone.utc).isoformat(timespec="seconds"),
        help="Timestamp metadata recorded in outputs (default is current UTC time).",
    )
    return parser.parse_args()


def load_codebook_labels(codebook_path: Path) -> dict:
    with codebook_path.open("r", encoding="utf-8") as fh:
        codebook = json.load(fh)
    label_map = {entry["name"]: entry.get("label", entry["name"]) for entry in codebook.get("variables", [])}
    return label_map


def load_config(config_path: Path) -> dict:
    with config_path.open("r", encoding="utf-8") as fh:
        return yaml.safe_load(fh)


def weighted_quantiles(values: np.ndarray, weights: np.ndarray, quantiles: Iterable[float]) -> List[float]:
    if values.size == 0:
        return [math.nan for _ in quantiles]
    order = np.argsort(values)
    sorted_values = values[order]
    sorted_weights = weights[order]
    cumulative = np.cumsum(sorted_weights)
    if cumulative[-1] == 0:
        return [math.nan for _ in quantiles]
    cumulative /= cumulative[-1]
    return [float(np.interp(q, cumulative, sorted_values)) for q in quantiles]


def ensure_parent(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def main() -> None:
    args = parse_args()

    dataset_path = Path(args.dataset)
    if not dataset_path.exists():
        raise SystemExit(f"Dataset not found: {dataset_path}")

    codebook_labels = load_codebook_labels(Path(args.codebook))
    config = load_config(Path(args.config))
    small_cell_threshold = config.get("small_cell_threshold", 10)
    seed = config.get("seed")

    df = pd.read_csv(dataset_path, low_memory=False)

    outcomes = list(dict.fromkeys(args.outcomes))  # preserve order, drop duplicates
    missing_columns = [col for col in outcomes if col not in df.columns]
    if missing_columns:
        raise SystemExit(f"Outcome columns missing from dataset: {missing_columns}")

    weight_col = args.weight
    if weight_col and weight_col not in df.columns:
        raise SystemExit(f"Weight column '{weight_col}' not found in dataset.")

    weights = pd.Series(1.0, index=df.index)
    weight_source = "uniform (SRS assumption)"
    if weight_col:
        weights = pd.to_numeric(df[weight_col], errors="coerce").fillna(0.0)
        weight_source = weight_col

    summary_records = []
    distribution_frames = []

    for col in outcomes:
        series = pd.to_numeric(df[col], errors="coerce")
        valid_mask = series.notna() & weights.notna()
        x = series[valid_mask].to_numpy(dtype=float)
        w = weights[valid_mask].to_numpy(dtype=float)

        weight_sum = float(w.sum()) if w.size else 0.0
        if weight_sum == 0.0:
            weighted_mean = math.nan
            weighted_std = math.nan
        else:
            weighted_mean = float(np.average(x, weights=w))
            weighted_var = float(np.average((x - weighted_mean) ** 2, weights=w))
            weighted_std = math.sqrt(weighted_var)

        quantile_values = weighted_quantiles(x, w, quantiles=(0.1, 0.25, 0.5, 0.75, 0.9))

        summary_records.append(
            {
                "variable": col,
                "label": codebook_labels.get(col, col),
                "n_unweighted": int(valid_mask.sum()),
                "n_weighted": weight_sum,
                "weighted_mean": weighted_mea
n,
                "weighted_sd": weighted_std,
                "p10": quantile_values[0],
                "p25": quantile_values[1],
                "median": quantile_values[2],
                "p75": quantile_values[3],
                "p90": quantile_values[4],
            }
        )

        # Weighted distribution with small-cell suppression
        value_counts = (
            pd.DataFrame({"value": series, "weight": weights})
            .dropna()
            .groupby("value", as_index=False)["weight"]
            .sum()
        )
        total_w = float(value_counts["weight"].sum())

        value_counts["proportion"] = value_counts["weight"] / total_w if total_w else math.nan
        value_counts["count_display"] = value_counts["weight"].apply(
            lambda v: "<10 (suppressed)" if v < small_cell_threshold else f"{v:.0f}"
        )
        value_counts["proportion_display"] = value_counts.apply(
            lambda row: "" if isinstance(row["count_display"], str) and "suppressed" in row["count_display"]
            else f"{row['proportion']:.4f}",
            axis=1,
        )
        value_counts["variable"] = col
        value_counts["label"] = codebook_labels.get(col, col)
        value_counts["weight_source"] = weight_source
        value_counts["small_cell_threshold"] = small_cell_threshold
        value_counts["seed"] = seed
        value_counts["timestamp_utc"] = args.timestamp

        distribution_frames.append(
            value_counts[
                [
                    "variable",
                    "label",
                    "value",
                    "count_display",
                    "proportion_display",
                    "weight_source",
                    "small_cell_threshold",
                    "seed",
                    "timestamp_utc",
                ]
            ]
        )

    summary_df = pd.DataFrame(summary_records)
    summary_df["weight_source"] = weight_source
    summary_df["seed"] = seed
    summary_df["timestamp_utc"] = args.timestamp

    ensure_parent(Path(args.out_summary))
    ensure_parent(Path(args.out_distribution))
    summary_df.to_csv(args.out_summary, index=False)
    pd.concat(distribution_frames, ignore_index=True).to_csv(args.out_distribution, index=False)

    print(
        json.dumps(
            {
                "script": "analysis/code/eda_weighted_summaries.py",
                "dataset": str(dataset_path),
                "weight_source": weight_source,
                "outcomes": outcomes,
                "outputs": [args.out_summary, args.out_distribution],
                "seed": seed,
                "timestamp_utc": args.timestamp,
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
