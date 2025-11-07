#!/usr/bin/env python3
"""Deterministic analysis for Hypothesis H3: Net worth vs. work satisfaction.

This script summarises current work/career satisfaction across ordered net worth
brackets under a simple random sampling (SRS) assumption. It outputs group-level
statistics alongside differences in mean satisfaction relative to the lowest
net worth bracket while enforcing the configured minimum cell size for privacy.

All calculations are deterministic; random seeds from the configuration are
recorded for reproducibility even though no stochastic procedures are used.
"""

from __future__ import annotations

import argparse
import json
import math
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

import shlex

import numpy as np
import pandas as pd
import yaml


NETWORTH_CODE_COLUMN = "networth"
NETWORTH_LABEL_COLUMN = "Your CURRENT net worth is closest to (nhoz8ia)"
SATISFACTION_COLUMN = "I am satisfied with my work/career life (or lack thereof) (z0mhd63)"


@dataclass(frozen=True)
class AnalysisConfig:
    seed: int
    min_cell_size: int
    weight_variable: Optional[str]
    variance_method: str
    design_assumption: str


def load_yaml(path: Path) -> Dict[str, Any]:
    if not path:
        return {}
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle) or {}


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
    variance_method = str(analysis_defaults.get("variance_method", "taylor"))
    design_assumption = str(
        design_cfg.get(
            "design_assumption",
            "Simple random sample treated as equal weights.",
        )
    )

    return AnalysisConfig(
        seed=seed,
        min_cell_size=min_cell,
        weight_variable=weight_variable,
        variance_method=variance_method,
        design_assumption=design_assumption,
    )


def build_networth_labels(df: pd.DataFrame) -> Dict[int, str]:
    """Map numeric net worth codes to modal text labels from the survey prompt."""
    mapping: Dict[int, str] = {}
    grouped = df.groupby(NETWORTH_CODE_COLUMN)[NETWORTH_LABEL_COLUMN]
    for code, series in grouped:
        if pd.isna(code):
            continue
        clean_code = int(round(float(code)))
        label = series.mode()
        mapping[clean_code] = str(label.iat[0]) if not label.empty else f"Bracket {clean_code}"
    return mapping


def compute_group_statistics(
    df: pd.DataFrame,
    config: AnalysisConfig,
    labels: Dict[int, str],
) -> Tuple[List[Dict[str, Any]], Dict[int, Dict[str, Any]]]:
    records: List[Dict[str, Any]] = []
    cache: Dict[int, Dict[str, Any]] = {}

    for code in sorted(df[NETWORTH_CODE_COLUMN].unique()):
        group = df.loc[df[NETWORTH_CODE_COLUMN] == code]
        n_total = int(group.shape[0])
        label = labels.get(code, f"Bracket {code}")
        base_record: Dict[str, Any] = {
            "networth_code": int(code),
            "networth_label": label,
            "n_total": n_total if n_total >= config.min_cell_size else "suppressed_lt_10",
            "seed": config.seed,
            "min_cell_size": config.min_cell_size,
            "weight_variable": config.weight_variable,
            "variance_method": config.variance_method,
            "design_assumption": config.design_assumption,
        }

        if n_total < config.min_cell_size:
            base_record.update(
                {
                    "mean_satisfaction": "suppressed_lt_10",
                    "std_satisfaction": "suppressed_lt_10",
                    "se_satisfaction": "suppressed_lt_10",
                    "ci_lower_95": "suppressed_lt_10",
                    "ci_upper_95": "suppressed_lt_10",
                }
            )
            cache[code] = {"suppressed": True}
            records.append(base_record)
            continue

        satisfaction = group[SATISFACTION_COLUMN]
        mean_val = float(satisfaction.mean())
        variance = float(satisfaction.var(ddof=1)) if n_total > 1 else 0.0
        std_val = math.sqrt(variance)
        se_val = std_val / math.sqrt(n_total) if n_total > 0 else float("nan")
        ci_margin = 1.96 * se_val

        base_record.update(
            {
                "mean_satisfaction": round(mean_val, 6),
                "std_satisfaction": round(std_val, 6),
                "se_satisfaction": round(se_val, 6),
                "ci_lower_95": round(mean_val - ci_margin, 6),
                "ci_upper_95": round(mean_val + ci_margin, 6),
            }
        )
        cache[code] = {
            "suppressed": False,
            "n": n_total,
            "mean": mean_val,
            "variance": variance,
            "label": label,
        }
        records.append(base_record)

    return records, cache


def compute_differences(
    codes: Sequence[int],
    cache: Dict[int, Dict[str, Any]],
    baseline_code: int,
    config: AnalysisConfig,
) -> List[Dict[str, Any]]:
    results: List[Dict[str, Any]] = []
    base_stats = cache.get(baseline_code)
    for code in codes:
        stats = cache.get(code)
        label = stats.get("label") if stats else f"Bracket {code}"
        record: Dict[str, Any] = {
            "networth_code": int(code),
            "networth_label": label,
            "baseline_code": int(baseline_code),
            "baseline_label": base_stats.get("label") if base_stats else f"Bracket {baseline_code}",
            "seed": config.seed,
            "min_cell_size": config.min_cell_size,
            "weight_variable": config.weight_variable,
            "variance_method": config.variance_method,
            "design_assumption": config.design_assumption,
        }

        suppressed = (
            base_stats is None
            or stats is None
            or base_stats.get("suppressed")
            or stats.get("suppressed")
        )
        if suppressed:
            record.update(
                {
                    "mean_diff": "suppressed_lt_10",
                    "se_diff": "suppressed_lt_10",
                    "ci_lower_95": "suppressed_lt_10",
                    "ci_upper_95": "suppressed_lt_10",
                    "n_group": "suppressed_lt_10",
                    "n_baseline": "suppressed_lt_10",
                }
            )
            results.append(record)
            continue

        n_group = stats["n"]
        n_base = base_stats["n"]
        if code == baseline_code:
            se = 0.0
            diff = 0.0
        else:
            variance = stats["variance"] / n_group + base_stats["variance"] / n_base
            se = math.sqrt(variance)
            diff = stats["mean"] - base_stats["mean"]
        ci_margin = 1.96 * se

        record.update(
            {
                "n_group": int(n_group),
                "n_baseline": int(n_base),
                "mean_diff": round(diff, 6),
                "se_diff": round(se, 6),
                "ci_lower_95": round(diff - ci_margin, 6),
                "ci_upper_95": round(diff + ci_margin, 6),
            }
        )
        results.append(record)

    return results


def parse_args(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Deterministic H3 analysis: net worth vs. work satisfaction."
    )
    parser.add_argument("--csv", required=True, type=Path, help="Input CSV dataset.")
    parser.add_argument("--config", required=True, type=Path, help="Agent configuration YAML.")
    parser.add_argument("--design", required=False, type=Path, help="Survey design YAML.")
    parser.add_argument("--out", required=True, type=Path, help="Output CSV for group summaries.")
    parser.add_argument(
        "--diff-out",
        required=True,
        type=Path,
        help="Output CSV for differences relative to the lowest net worth bracket.",
    )
    parser.add_argument(
        "--manifest", required=True, type=Path, help="Manifest JSON capturing reproducibility metadata."
    )
    parser.add_argument(
        "--min-cell-size",
        required=False,
        type=int,
        default=None,
        help="Override minimum cell size (defaults to config.privacy.min_cell_size).",
    )
    return parser.parse_args(argv)


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = parse_args(argv)

    config = resolve_analysis_config(args.config, args.design, args.min_cell_size)

    usecols = [
        NETWORTH_CODE_COLUMN,
        NETWORTH_LABEL_COLUMN,
        SATISFACTION_COLUMN,
    ]
    df = pd.read_csv(args.csv, usecols=usecols, low_memory=False)
    df = df.copy()
    df[NETWORTH_CODE_COLUMN] = pd.to_numeric(df[NETWORTH_CODE_COLUMN], errors="coerce").astype("float")
    df[SATISFACTION_COLUMN] = pd.to_numeric(df[SATISFACTION_COLUMN], errors="coerce")
    df = df.dropna(subset=[NETWORTH_CODE_COLUMN, SATISFACTION_COLUMN])
    df[NETWORTH_CODE_COLUMN] = df[NETWORTH_CODE_COLUMN].round().astype(int)

    labels = build_networth_labels(df)

    group_records, cache = compute_group_statistics(df, config, labels)
    codes = sorted(cache.keys())
    if not codes:
        raise ValueError("No valid net worth groups found after filtering for non-missing values.")
    baseline_code = min(codes)
    diff_records = compute_differences(codes, cache, baseline_code, config)

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.diff_out.parent.mkdir(parents=True, exist_ok=True)
    args.manifest.parent.mkdir(parents=True, exist_ok=True)

    pd.DataFrame.from_records(group_records).to_csv(args.out, index=False)
    pd.DataFrame.from_records(diff_records).to_csv(args.diff_out, index=False)

    spearman = float(
        df[NETWORTH_CODE_COLUMN].corr(df[SATISFACTION_COLUMN], method="spearman")
    )
    pearson = float(df[NETWORTH_CODE_COLUMN].corr(df[SATISFACTION_COLUMN], method="pearson"))

    script_path = Path(__file__).resolve()
    cwd = Path.cwd().resolve()
    try:
        script_path = script_path.relative_to(cwd)
    except ValueError:
        pass

    command_parts = [
        "python",
        script_path.as_posix(),
        "--csv",
        str(args.csv),
        "--config",
        str(args.config),
    ]
    if args.design:
        command_parts.extend(["--design", str(args.design)])
    command_parts.extend(
        [
            "--out",
            str(args.out),
            "--diff-out",
            str(args.diff_out),
            "--manifest",
            str(args.manifest),
        ]
    )
    if args.min_cell_size is not None:
        command_parts.extend(["--min-cell-size", str(args.min_cell_size)])

    manifest_payload = {
        "analysis": "H3: Net worth vs. work satisfaction",
        "command": shlex.join(command_parts),
        "config": str(args.config),
        "dataset": str(args.csv),
        "design": str(args.design) if args.design else None,
        "design_assumption": config.design_assumption,
        "min_cell_size": config.min_cell_size,
        "outputs": {
            "group_stats_csv": str(args.out),
            "difference_csv": str(args.diff_out),
        },
        "seed": config.seed,
        "timestamp_utc": datetime.now(tz=timezone.utc).isoformat(),
        "variance_method": config.variance_method,
        "weight_variable": config.weight_variable,
        "networth_labels": {int(k): v for k, v in labels.items()},
        "row_counts": {
            "total_rows": int(df.shape[0]),
            "unique_networth_groups": len(codes),
        },
        "correlations": {
            "spearman_r": round(spearman, 6),
            "pearson_r": round(pearson, 6),
        },
        "baseline_code": int(baseline_code),
        "baseline_label": labels.get(baseline_code, f"Bracket {baseline_code}"),
    }

    with args.manifest.open("w", encoding="utf-8") as handle:
        json.dump(manifest_payload, handle, indent=2)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
