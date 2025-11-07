#!/usr/bin/env python3
"""Deterministic analysis for Hypothesis H2: Childhood religious strictness vs. adult happiness change.

This script bins the ordinal childhood religious strictness scale (`externalreligion`)
into three deterministic terciles based on empirical distribution and reports simple
random sample (SRS) means of the adult-versus-childhood happiness change item
(`On average, I am happier as an adult than I was in childhood (h33e6gg)`).

It outputs group-level summaries and pairwise mean differences across terciles with
Bonferroni-adjusted confidence intervals while enforcing the configured minimum
cell size for privacy.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from statistics import NormalDist
from typing import Any, Dict, List, Optional, Sequence, Tuple

import numpy as np
import pandas as pd
import yaml


HAPPINESS_COLUMN = "On average, I am happier as an adult than I was in childhood (h33e6gg)"


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


def compute_value_to_tercile_map(values: pd.Series) -> Dict[int, int]:
    """Assign each observed externalreligion integer value to a tercile index."""
    value_counts = values.value_counts(dropna=False).sort_index()
    total = int(value_counts.sum())
    if total == 0:
        return {}

    thresholds = [total / 3.0, 2.0 * total / 3.0]
    value_to_group: Dict[int, int] = {}
    cumulative = 0
    group = 0

    for raw_value, count in value_counts.items():
        if pd.isna(raw_value):
            continue
        value = int(round(float(raw_value)))
        value_to_group[value] = min(group, 2)
        cumulative += int(count)
        if group < 2 and cumulative >= thresholds[group]:
            group += 1

    return value_to_group


def build_tercile_labels(mapping: Dict[int, int]) -> Dict[int, str]:
    grouped_values: Dict[int, List[int]] = {0: [], 1: [], 2: []}
    for value, tercile in mapping.items():
        grouped_values.setdefault(tercile, []).append(value)

    labels: Dict[int, str] = {}
    for idx in (0, 1, 2):
        values = sorted(set(grouped_values.get(idx, [])))
        if not values:
            labels[idx] = f"Tercile {idx + 1} (no assigned levels)"
        elif values[0] == values[-1]:
            labels[idx] = f"Tercile {idx + 1} (externalreligion = {values[0]})"
        else:
            labels[idx] = (
                f"Tercile {idx + 1} (externalreligion in [{values[0]}, {values[-1]}])"
            )
    return labels


def compute_group_statistics(
    df: pd.DataFrame,
    labels: Dict[int, str],
    config: AnalysisConfig,
) -> Tuple[List[Dict[str, Any]], Dict[int, Dict[str, Any]]]:
    records: List[Dict[str, Any]] = []
    lookup: Dict[int, Dict[str, Any]] = {}

    for tercile in (0, 1, 2):
        group_df = df.loc[df["strictness_tercile"] == tercile]
        n_total = int(group_df.shape[0])
        base_record: Dict[str, Any] = {
            "tercile_index": int(tercile),
            "tercile_label": labels.get(int(tercile), f"Tercile {tercile + 1}"),
            "n_total": n_total if n_total >= config.min_cell_size else "suppressed_lt_10",
            "seed": config.seed,
            "min_cell_size": config.min_cell_size,
            "weight_variable": config.weight_variable,
            "variance_method": config.variance_method,
            "design_assumption": config.design_assumption,
        }

        suppressed = n_total < config.min_cell_size
        if suppressed:
            base_record.update(
                {
                    "mean_happiness": "suppressed_lt_10",
                    "std_happiness": "suppressed_lt_10",
                    "se_happiness": "suppressed_lt_10",
                    "ci_lower_95": "suppressed_lt_10",
                    "ci_upper_95": "suppressed_lt_10",
                }
            )
            lookup[int(tercile)] = {"suppressed": True}
            records.append(base_record)
            continue

        happiness = group_df["happiness"]
        mean_val = float(happiness.mean())
        variance = float(happiness.var(ddof=1)) if n_total > 1 else 0.0
        std = math.sqrt(variance)
        se = std / math.sqrt(n_total) if n_total > 0 else float("nan")
        ci_margin = 1.96 * se

        base_record.update(
            {
                "mean_happiness": round(mean_val, 6),
                "std_happiness": round(std, 6),
                "se_happiness": round(se, 6),
                "ci_lower_95": round(mean_val - ci_margin, 6),
                "ci_upper_95": round(mean_val + ci_margin, 6),
            }
        )
        records.append(base_record)
        lookup[int(tercile)] = {
            "suppressed": False,
            "n": n_total,
            "mean": mean_val,
            "variance": variance,
            "label": labels.get(int(tercile), f"Tercile {tercile + 1}"),
        }

    return records, lookup


def compute_pairwise_differences(
    lookup: Dict[int, Dict[str, Any]],
    config: AnalysisConfig,
) -> List[Dict[str, Any]]:
    comparisons = [
        (0, 1, "Tercile 2 minus Tercile 1"),
        (0, 2, "Tercile 3 minus Tercile 1"),
        (1, 2, "Tercile 3 minus Tercile 2"),
    ]
    results: List[Dict[str, Any]] = []
    alpha = 0.05 / max(len(comparisons), 1)
    z_crit = NormalDist().inv_cdf(1 - alpha / 2.0)

    for lower, upper, label in comparisons:
        record: Dict[str, Any] = {
            "comparison": label,
            "group_low_index": lower,
            "group_high_index": upper,
            "seed": config.seed,
            "min_cell_size": config.min_cell_size,
            "weight_variable": config.weight_variable,
            "variance_method": config.variance_method,
            "design_assumption": config.design_assumption,
            "bonferroni_alpha": round(alpha, 6),
            "z_critical": round(z_crit, 6),
        }

        group_low = lookup.get(lower)
        group_high = lookup.get(upper)

        if not group_low or not group_high:
            record.update(
                {
                    "estimate": "insufficient_group",
                    "standard_error": "insufficient_group",
                    "ci_lower": "insufficient_group",
                    "ci_upper": "insufficient_group",
                }
            )
            results.append(record)
            continue

        if group_low.get("suppressed") or group_high.get("suppressed"):
            record.update(
                {
                    "estimate": "suppressed_lt_10",
                    "standard_error": "suppressed_lt_10",
                    "ci_lower": "suppressed_lt_10",
                    "ci_upper": "suppressed_lt_10",
                }
            )
            results.append(record)
            continue

        mean_diff = group_high["mean"] - group_low["mean"]
        n_low = group_low["n"]
        n_high = group_high["n"]
        var_low = group_low["variance"]
        var_high = group_high["variance"]
        se = math.sqrt((var_low / n_low) + (var_high / n_high))
        ci_margin = z_crit * se

        record.update(
            {
                "estimate": round(mean_diff, 6),
                "standard_error": round(se, 6),
                "ci_lower": round(mean_diff - ci_margin, 6),
                "ci_upper": round(mean_diff + ci_margin, 6),
                "group_low_label": group_low.get("label"),
                "group_high_label": group_high.get("label"),
                "n_group_low": n_low,
                "n_group_high": n_high,
            }
        )
        results.append(record)

    return results


def parse_args(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Compute deterministic SRS means for Hypothesis H2 (religious strictness terciles vs happiness change)."
    )
    parser.add_argument("--csv", required=True, help="Path to the survey CSV file.")
    parser.add_argument("--config", required=True, help="Path to the agent configuration YAML.")
    parser.add_argument(
        "--design",
        required=False,
        help="Optional path to survey design YAML for metadata inclusion.",
    )
    parser.add_argument("--out", required=True, help="Output CSV path for tercile-level statistics.")
    parser.add_argument(
        "--diff-out",
        required=True,
        help="Output CSV path for pairwise mean differences across terciles.",
    )
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
    out_path = Path(args.out)
    diff_path = Path(args.diff_out)
    manifest_path = Path(args.manifest)

    analysis_config = resolve_analysis_config(config_path, design_path, args.min_cell)
    np.random.seed(analysis_config.seed)

    required_columns = ["externalreligion", HAPPINESS_COLUMN]
    df = pd.read_csv(csv_path, usecols=required_columns)
    df_clean = df.dropna(subset=required_columns).copy()
    df_clean["externalreligion"] = df_clean["externalreligion"].astype(int)
    df_clean["happiness"] = df_clean[HAPPINESS_COLUMN].astype(float)

    value_map = compute_value_to_tercile_map(df_clean["externalreligion"])
    if len(value_map) == 0:
        raise ValueError("No observed values for externalreligion to form terciles.")
    labels = build_tercile_labels(value_map)

    df_clean["strictness_tercile"] = df_clean["externalreligion"].map(value_map)
    raw_counts = df_clean["strictness_tercile"].value_counts().to_dict()
    tercile_counts = {idx: int(raw_counts.get(idx, 0)) for idx in (0, 1, 2)}

    out_path.parent.mkdir(parents=True, exist_ok=True)
    diff_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.parent.mkdir(parents=True, exist_ok=True)

    group_records, lookup = compute_group_statistics(df_clean, labels, analysis_config)
    group_df = pd.DataFrame(group_records)
    group_df.to_csv(out_path, index=False)

    diff_records = compute_pairwise_differences(lookup, analysis_config)
    diff_df = pd.DataFrame(diff_records)
    diff_df.to_csv(diff_path, index=False)

    manifest = {
        "analysis": "H2: Childhood religious strictness vs adult happiness change",
        "seed": analysis_config.seed,
        "min_cell_size": analysis_config.min_cell_size,
        "dataset": str(csv_path),
        "config": str(config_path),
        "design": str(design_path) if design_path else None,
        "command": "python " + " ".join(sys.argv[0:]),
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "outputs": {
            "tercile_stats_csv": str(out_path),
            "differences_csv": str(diff_path),
        },
        "weight_variable": analysis_config.weight_variable,
        "variance_method": analysis_config.variance_method,
        "design_assumption": analysis_config.design_assumption,
        "tercile_value_map": value_map,
        "tercile_labels": labels,
        "tercile_counts": {int(k): int(v) for k, v in tercile_counts.items()},
        "happiness_column": HAPPINESS_COLUMN,
    }
    with manifest_path.open("w", encoding="utf-8") as fh:
        json.dump(manifest, fh, indent=2, sort_keys=True)


if __name__ == "__main__":
    main()
