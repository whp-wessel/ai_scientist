#!/usr/bin/env python3
"""Deterministic exploratory summaries for key survey outcomes.

Reads the primary survey CSV, computes unweighted summaries for priority
variables, and writes a manifest-friendly CSV table. All operations are
deterministic and respect the configured minimum cell size to avoid
revealing small-N cells.
"""

from __future__ import annotations

import argparse
import json
import math
import random
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

import numpy as np
import pandas as pd
import yaml


@dataclass(frozen=True)
class VariableSpec:
    alias: str
    column: str
    var_type: str
    note: str = ""


KEY_VARIABLES: List[VariableSpec] = [
    VariableSpec(
        alias="selfage",
        column="selfage",
        var_type="numeric",
        note="Respondent age in years.",
    ),
    VariableSpec(
        alias="biomale",
        column="biomale",
        var_type="binary",
        note="1=Biologically male; 0=otherwise. Confirm coding in codebook.",
    ),
    VariableSpec(
        alias="religion_current",
        column="religion",
        var_type="binary",
        note="1=Currently practices a religion; 0=otherwise.",
    ),
    VariableSpec(
        alias="externalreligion_importance",
        column="externalreligion",
        var_type="ordinal",
        note="Importance of childhood religious adherence. Treated as ordered numeric scale.",
    ),
    VariableSpec(
        alias="networth_bracket",
        column="networth",
        var_type="ordinal",
        note="Current net worth bracket codes (higher=greater net worth).",
    ),
    VariableSpec(
        alias="h33e6gg_adult_vs_child_happiness",
        column="On average, I am happier as an adult than I was in childhood (h33e6gg)",
        var_type="ordinal",
        note="Higher values indicate greater adult vs childhood happiness; verify scale direction.",
    ),
]


def load_yaml_config(path: Path) -> Dict[str, Any]:
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as fh:
        data = yaml.safe_load(fh)
    return data or {}


def resolve_min_cell_size(config: Dict[str, Any], override: Optional[int]) -> int:
    if override is not None:
        return int(override)
    try:
        return int(config.get("privacy", {}).get("min_cell_size", 10))
    except (TypeError, ValueError):
        return 10


def resolve_seed(config: Dict[str, Any], default_seed: int = 20251016) -> int:
    value = config.get("seed", default_seed)
    try:
        return int(value)
    except (TypeError, ValueError):
        return default_seed


def suppress_value(note: str) -> Dict[str, Any]:
    return {
        "value": "suppressed_lt_10",
        "note": note,
    }


def summarise_numeric(series: pd.Series, min_cell: int) -> List[Dict[str, Any]]:
    clean = series.dropna()
    n = int(clean.shape[0])
    if n < min_cell:
        return [
            {
                "statistic": "all_stats",
                "value": "suppressed_lt_10",
                "unweighted_n": n,
                "detail": "Suppressed: non-missing N below privacy threshold.",
            }
        ]

    quantiles = clean.quantile([0.25, 0.5, 0.75])
    stats = {
        "mean": clean.mean(),
        "std": clean.std(ddof=1) if n > 1 else float("nan"),
        "min": clean.min(),
        "q1": quantiles.loc[0.25],
        "median": quantiles.loc[0.5],
        "q3": quantiles.loc[0.75],
        "max": clean.max(),
    }
    rows: List[Dict[str, Any]] = []
    for key, value in stats.items():
        val = "" if value is None or (isinstance(value, float) and math.isnan(value)) else round(float(value), 4)
        rows.append({"statistic": key, "value": val, "unweighted_n": n})

    missing_fraction = 1.0 - (n / series.shape[0])
    rows.append(
        {
            "statistic": "missing_fraction",
            "value": round(float(missing_fraction), 4),
            "unweighted_n": series.shape[0],
        }
    )
    return rows


def summarise_binary(series: pd.Series, min_cell: int) -> List[Dict[str, Any]]:
    clean = series.dropna()
    n = int(clean.shape[0])
    if n < min_cell:
        return [
            {
                "statistic": "all_stats",
                "value": "suppressed_lt_10",
                "unweighted_n": n,
                "detail": "Suppressed: non-missing N below privacy threshold.",
            }
        ]

    counts = clean.value_counts()
    count1 = int(counts.get(1, 0))
    count0 = int(counts.get(0, 0))
    rows: List[Dict[str, Any]] = []

    if count1 < min_cell or count0 < min_cell:
        rows.append(
            {
                "statistic": "prop_1",
                "value": "suppressed_lt_10",
                "unweighted_n": n,
                "detail": "Suppressed: category count below privacy threshold.",
            }
        )
    else:
        prop = clean.mean()
        rows.append(
            {
                "statistic": "prop_1",
                "value": round(float(prop), 4),
                "unweighted_n": n,
            }
        )
        rows.append(
            {
                "statistic": "count_1",
                "value": count1,
                "unweighted_n": n,
            }
        )
        rows.append(
            {
                "statistic": "count_0",
                "value": count0,
                "unweighted_n": n,
            }
        )

    missing_fraction = 1.0 - (n / series.shape[0])
    rows.append(
        {
            "statistic": "missing_fraction",
            "value": round(float(missing_fraction), 4),
            "unweighted_n": series.shape[0],
        }
    )
    return rows


def build_summary(
    df: pd.DataFrame,
    variables: List[VariableSpec],
    min_cell: int,
) -> List[Dict[str, Any]]:
    results: List[Dict[str, Any]] = []
    total_records = df.shape[0]

    for spec in variables:
        if spec.column not in df.columns:
            results.append(
                {
                    "variable_id": spec.alias,
                    "source_column": spec.column,
                    "statistic": "status",
                    "value": "missing_column",
                    "unweighted_n": 0,
                    "note": f"{spec.column} not found in dataset.",
                }
            )
            continue

        series = df[spec.column]
        if spec.var_type == "numeric" or spec.var_type == "ordinal":
            rows = summarise_numeric(series, min_cell)
        elif spec.var_type == "binary":
            rows = summarise_binary(series, min_cell)
        else:
            rows = [
                {
                    "statistic": "status",
                    "value": "unsupported_type",
                    "unweighted_n": int(series.dropna().shape[0]),
                    "detail": f"Unsupported var_type={spec.var_type}",
                }
            ]

        for row in rows:
            enriched = {
                "variable_id": spec.alias,
                "source_column": spec.column,
                "variable_type": spec.var_type,
                "statistic": row.get("statistic"),
                "value": row.get("value"),
                "unweighted_n": row.get("unweighted_n"),
                "detail": row.get("detail", ""),
                "note": spec.note,
                "total_records": total_records,
            }
            results.append(enriched)

    return results


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate deterministic exploratory summaries for key survey outcomes."
    )
    parser.add_argument("--csv", required=True, help="Path to the survey CSV file.")
    parser.add_argument(
        "--config",
        default="config/agent_config.yaml",
        help="Path to the analysis agent configuration YAML.",
    )
    parser.add_argument(
        "--out",
        default="tables/summary_key_outcomes.csv",
        help="Destination CSV for summary table.",
    )
    parser.add_argument(
        "--min-cell-size",
        type=int,
        default=None,
        help="Override minimum cell size for suppression (defaults to config value).",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    config_path = Path(args.config)
    config = load_yaml_config(config_path)
    min_cell_size = resolve_min_cell_size(config, args.min_cell_size)
    seed = resolve_seed(config)

    random.seed(seed)
    np.random.seed(seed)

    csv_path = Path(args.csv)
    if not csv_path.exists():
        raise FileNotFoundError(f"CSV not found: {csv_path}")

    df = pd.read_csv(csv_path, low_memory=False)

    summary_rows = build_summary(df, KEY_VARIABLES, min_cell_size)
    output_df = pd.DataFrame(summary_rows)

    output_path = Path(args.out)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_df.to_csv(output_path, index=False)

    script_path = Path(__file__).resolve()
    try:
        script_ref = script_path.relative_to(Path.cwd().resolve())
    except ValueError:
        script_ref = script_path

    manifest = {
        "seed": seed,
        "min_cell_size": min_cell_size,
        "records": df.shape[0],
        "variables_summarised": [spec.alias for spec in KEY_VARIABLES],
        "command": f"python {script_ref} --csv {args.csv} --config {args.config} --out {args.out}",
    }
    manifest_path = output_path.with_suffix(".json")
    with manifest_path.open("w", encoding="utf-8") as fh:
        json.dump(manifest, fh, indent=2)

    print(f"Saved summary table to {output_path} and manifest to {manifest_path}")


if __name__ == "__main__":
    main()
