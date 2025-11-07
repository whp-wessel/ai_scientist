#!/usr/bin/env python3
"""Deterministic analysis for Hypothesis H1: Religion practice by biological sex.

This script computes simple-random-sample (SRS) proportion estimates for the share
of respondents who actively practice a religion (any intensity) stratified by the
binary `biomale` indicator. Differences in proportions, standard errors, and
confidence intervals are exported alongside metadata needed for reproducibility.

The analysis honours the configured minimum cell size; any cell below the threshold
is suppressed to avoid privacy leakage.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

import numpy as np
import pandas as pd
import yaml


VALID_RELIGION_CODES: Tuple[int, ...] = (0, 1, 2, 3)


@dataclass(frozen=True)
class AnalysisConfig:
    seed: int
    min_cell_size: int
    weight_variable: Optional[str]
    variance_method: str
    design_assumption: str


def load_yaml(path: Path) -> Dict[str, Any]:
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as fh:
        return yaml.safe_load(fh) or {}


def resolve_seed(config: Dict[str, Any], default_seed: int = 20251016) -> int:
    value = config.get("seed", default_seed)
    try:
        return int(value)
    except (TypeError, ValueError):
        return default_seed


def resolve_min_cell_size(config: Dict[str, Any], override: Optional[int]) -> int:
    if override is not None:
        return int(override)
    try:
        return int(config.get("privacy", {}).get("min_cell_size", 10))
    except (TypeError, ValueError):
        return 10


def resolve_analysis_config(
    agent_config_path: Path,
    design_path: Optional[Path],
    min_cell_override: Optional[int],
) -> AnalysisConfig:
    agent_cfg = load_yaml(agent_config_path)
    design_cfg = load_yaml(design_path) if design_path else {}

    seed = resolve_seed(agent_cfg)
    min_cell = resolve_min_cell_size(agent_cfg, min_cell_override)
    analysis_defaults = agent_cfg.get("analysis_defaults", {})

    weight_variable = analysis_defaults.get("weight_variable")
    variance_method = analysis_defaults.get("variance_method", "taylor")
    design_assumption = design_cfg.get(
        "design_assumption",
        "Simple random sample treated as equal weights.",
    )

    return AnalysisConfig(
        seed=seed,
        min_cell_size=min_cell,
        weight_variable=weight_variable,
        variance_method=str(variance_method),
        design_assumption=str(design_assumption),
    )


def clamp(value: float, lower: float = 0.0, upper: float = 1.0) -> float:
    return max(lower, min(upper, value))


def compute_group_records(
    df: pd.DataFrame,
    config: AnalysisConfig,
) -> Tuple[List[Dict[str, Any]], Dict[str, Dict[str, Any]]]:
    records: List[Dict[str, Any]] = []
    grouped: Dict[str, Dict[str, Any]] = {}

    label_map = {0: "Not biologically male", 1: "Biologically male"}
    for biomale_code, group in sorted(df.groupby("biomale")):
        n_total = int(group.shape[0])
        any_count = int(group["any_practice"].sum())
        stats: Dict[str, Any] = {
            "biomale_code": int(biomale_code),
            "biomale_label": label_map.get(int(biomale_code), f"biomale={biomale_code}"),
            "n_total": n_total,
            "seed": config.seed,
            "min_cell_size": config.min_cell_size,
            "weight_variable": config.weight_variable,
            "variance_method": config.variance_method,
            "design_assumption": config.design_assumption,
        }

        if n_total < config.min_cell_size:
            stats.update(
                {
                    "n_any_practice": "suppressed_lt_10",
                    "prop_any_practice": "suppressed_lt_10",
                    "prop_any_practice_se": "suppressed_lt_10",
                    "prop_any_practice_ci_lower": "suppressed_lt_10",
                    "prop_any_practice_ci_upper": "suppressed_lt_10",
                }
            )
            for code in VALID_RELIGION_CODES:
                stats[f"prop_religion_{code}"] = "suppressed_lt_10"
            records.append(stats)
            grouped[str(int(biomale_code))] = stats
            continue

        any_prop = any_count / n_total
        any_se = math.sqrt(any_prop * (1.0 - any_prop) / n_total)
        stats["n_any_practice"] = any_count if any_count >= config.min_cell_size else "suppressed_lt_10"
        stats["prop_any_practice"] = round(any_prop, 6)
        stats["prop_any_practice_se"] = round(any_se, 6)
        stats["prop_any_practice_ci_lower"] = round(clamp(any_prop - 1.96 * any_se), 6)
        stats["prop_any_practice_ci_upper"] = round(clamp(any_prop + 1.96 * any_se), 6)

        intensity_counts = group["religion"].value_counts().reindex(VALID_RELIGION_CODES, fill_value=0)
        for code, count in intensity_counts.items():
            key = f"prop_religion_{code}"
            if count < config.min_cell_size:
                stats[key] = "suppressed_lt_10"
            else:
                stats[key] = round(count / n_total, 6)

        records.append(stats)
        grouped[str(int(biomale_code))] = stats

    return records, grouped


def compute_difference_record(
    grouped_stats: Dict[str, Dict[str, Any]],
    config: AnalysisConfig,
) -> Dict[str, Any]:
    male = grouped_stats.get("1")
    non_male = grouped_stats.get("0")

    base_record: Dict[str, Any] = {
        "comparison": "prop_any_practice_male_minus_non_male",
        "seed": config.seed,
        "min_cell_size": config.min_cell_size,
        "weight_variable": config.weight_variable,
        "variance_method": config.variance_method,
        "design_assumption": config.design_assumption,
    }

    if not male or not non_male:
        base_record.update(
            {
                "estimate": "insufficient_groups",
                "standard_error": "insufficient_groups",
                "ci_lower": "insufficient_groups",
                "ci_upper": "insufficient_groups",
            }
        )
        return base_record

    if isinstance(male.get("prop_any_practice"), str) or isinstance(non_male.get("prop_any_practice"), str):
        base_record.update(
            {
                "estimate": "suppressed_lt_10",
                "standard_error": "suppressed_lt_10",
                "ci_lower": "suppressed_lt_10",
                "ci_upper": "suppressed_lt_10",
            }
        )
        return base_record

    p1 = float(male["prop_any_practice"])
    p0 = float(non_male["prop_any_practice"])
    n1 = float(male["n_total"])
    n0 = float(non_male["n_total"])

    se_diff = math.sqrt((p1 * (1.0 - p1) / n1) + (p0 * (1.0 - p0) / n0))
    estimate = p1 - p0

    base_record.update(
        {
            "estimate": round(estimate, 6),
            "standard_error": round(se_diff, 6),
            "ci_lower": round(estimate - 1.96 * se_diff, 6),
            "ci_upper": round(estimate + 1.96 * se_diff, 6),
            "n_biomale": int(n1),
            "n_not_biomale": int(n0),
        }
    )
    return base_record


def parse_args(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Compute SRS-based estimates for Hypothesis H1 (religion by biological sex)."
    )
    parser.add_argument("--csv", required=True, help="Path to the survey CSV file.")
    parser.add_argument("--config", required=True, help="Path to the agent configuration YAML.")
    parser.add_argument(
        "--design",
        required=False,
        help="Optional path to survey design YAML for metadata inclusion.",
    )
    parser.add_argument("--out", required=True, help="Output CSV path for group-level statistics.")
    parser.add_argument("--diff-out", required=True, help="Output CSV path for difference estimates.")
    parser.add_argument("--manifest", required=True, help="Output JSON manifest path.")
    parser.add_argument(
        "--min-cell",
        type=int,
        default=None,
        help="Override minimum cell size (defaults to config privacy.min_cell_size).",
    )
    return parser.parse_args(argv)


def main(argv: Optional[Sequence[str]] = None) -> None:
    args = parse_args(argv)
    csv_path = Path(args.csv)
    config_path = Path(args.config)
    design_path = Path(args.design) if args.design else None
    out_group_path = Path(args.out)
    out_diff_path = Path(args.diff_out)
    manifest_path = Path(args.manifest)

    analysis_config = resolve_analysis_config(config_path, design_path, args.min_cell)
    np.random.seed(analysis_config.seed)

    required_columns = ["biomale", "religion"]
    df = pd.read_csv(csv_path, usecols=required_columns)
    df_clean = (
        df.dropna(subset=required_columns)
        .loc[lambda d: d["biomale"].isin([0, 1])]
        .loc[lambda d: d["religion"].isin(VALID_RELIGION_CODES)]
        .copy()
    )
    df_clean["biomale"] = df_clean["biomale"].astype(int)
    df_clean["religion"] = df_clean["religion"].astype(int)
    df_clean["any_practice"] = (df_clean["religion"] > 0).astype(int)

    group_records, grouped_lookup = compute_group_records(df_clean, analysis_config)
    difference_record = compute_difference_record(grouped_lookup, analysis_config)

    out_group_path.parent.mkdir(parents=True, exist_ok=True)
    out_diff_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.parent.mkdir(parents=True, exist_ok=True)

    group_df = pd.DataFrame(group_records)
    diff_df = pd.DataFrame([difference_record])

    group_df.to_csv(out_group_path, index=False)
    diff_df.to_csv(out_diff_path, index=False)

    manifest = {
        "analysis": "H1: Any active religion practice by biological sex",
        "seed": analysis_config.seed,
        "min_cell_size": analysis_config.min_cell_size,
        "dataset": str(csv_path),
        "config": str(config_path),
        "design": str(design_path) if design_path else None,
        "command": "python " + " ".join(sys.argv[0:]),
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "outputs": {
            "group_stats_csv": str(out_group_path),
            "difference_csv": str(out_diff_path),
        },
        "weight_variable": analysis_config.weight_variable,
        "variance_method": analysis_config.variance_method,
        "design_assumption": analysis_config.design_assumption,
    }
    with manifest_path.open("w", encoding="utf-8") as fh:
        json.dump(manifest, fh, indent=2, sort_keys=True)


if __name__ == "__main__":
    main()

