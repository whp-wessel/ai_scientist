#!/usr/bin/env python3
"""
Profile missingness for hypothesis-relevant variables with small-cell suppression.

Regeneration example:
python analysis/code/profile_missingness.py \
    --dataset childhoodbalancedpublic_original.csv \
    --codebook docs/codebook.json \
    --hypotheses analysis/hypotheses.csv \
    --config config/agent_config.yaml \
    --out-csv tables/missingness_profile.csv \
    --out-patterns tables/missingness_patterns.csv
"""

from __future__ import annotations

import argparse
import json
import random
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Sequence, Tuple

import numpy as np
import pandas as pd
import yaml


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Profile missingness across hypothesis-relevant variables."
    )
    parser.add_argument("--dataset", required=True, help="Path to CSV dataset.")
    parser.add_argument("--codebook", required=True, help="Path to codebook.json.")
    parser.add_argument("--hypotheses", required=True, help="Path to hypotheses.csv.")
    parser.add_argument("--config", required=True, help="Path to agent_config.yaml.")
    parser.add_argument(
        "--out-csv",
        required=True,
        help="Destination CSV for variable-level missingness summary.",
    )
    parser.add_argument(
        "--out-patterns",
        required=True,
        help="Destination CSV for aggregate missingness patterns.",
    )
    return parser.parse_args()


def load_config(path: Path) -> Tuple[int, int]:
    config = yaml.safe_load(path.read_text())
    seed = int(config.get("seed", 0))
    threshold = int(config.get("small_cell_threshold", 10))
    return seed, threshold


def normalise_split(field: str) -> List[str]:
    if field is None:
        return []
    field = str(field).strip()
    if not field or field.upper() in {"NA", "N/A", "NONE"}:
        return []
    parts = [part.strip() for part in field.replace("|", ";").split(";")]
    return [part for part in parts if part]


def load_hypothesis_variables(path: Path) -> List[str]:
    df = pd.read_csv(path)
    ordered_vars: List[str] = []
    seen = set()

    def maybe_add(value: str) -> None:
        if value and value not in seen:
            ordered_vars.append(value)
            seen.add(value)

    for _, row in df.iterrows():
        maybe_add(row.get("outcome_var"))
        for field in ("predictors", "controls"):
            for candidate in normalise_split(row.get(field, "")):
                maybe_add(candidate)
    return ordered_vars


def load_codebook(path: Path) -> Dict[str, Dict]:
    raw = json.loads(path.read_text())
    variables = raw.get("variables", [])
    return {entry.get("name"): entry for entry in variables}


def suppress_count(value: int, threshold: int, n_total: int) -> Tuple[str, str, str]:
    if value is None:
        return "N/A", "N/A", "not_found"
    if value == 0 or value >= threshold:
        percent = f"{(value / n_total) * 100:.2f}%"
        return str(value), percent, "ok"
    upper_pct = (threshold / n_total) * 100
    return f"<{threshold}", f"<{upper_pct:.2f}%", "suppressed"


def main() -> None:
    args = parse_args()

    dataset_path = Path(args.dataset)
    codebook_path = Path(args.codebook)
    hypotheses_path = Path(args.hypotheses)
    config_path = Path(args.config)
    out_csv_path = Path(args.out_csv)
    out_patterns_path = Path(args.out_patterns)

    seed, threshold = load_config(config_path)
    random.seed(seed)
    np.random.seed(seed)

    key_variables = load_hypothesis_variables(hypotheses_path)
    codebook_map = load_codebook(codebook_path)

    dataset_columns = pd.read_csv(dataset_path, nrows=0).columns.tolist()
    present_variables = [var for var in key_variables if var in dataset_columns]
    missing_variables = [var for var in key_variables if var not in dataset_columns]

    if present_variables:
        df = pd.read_csv(
            dataset_path,
            usecols=present_variables,
            low_memory=False,
        )
        df = df[present_variables]
        n_total = int(df.shape[0])
    else:
        # Fallback: determine total rows without loading entire wide dataset.
        fallback_col = dataset_columns[0]
        n_total = int(
            pd.read_csv(dataset_path, usecols=[fallback_col], low_memory=False).shape[0]
        )
        df = pd.DataFrame()

    records = []
    for variable in key_variables:
        metadata = codebook_map.get(variable, {})
        label = metadata.get("label", "")
        role = metadata.get("analysis_role", "")
        notes = metadata.get("notes", "")

        if variable in present_variables and not df.empty:
            missing_count_raw = int(df[variable].isna().sum())
            nonmissing_count = n_total - missing_count_raw
            missing_display, missing_percent, status = suppress_count(
                missing_count_raw, threshold, n_total
            )
            record = {
                "variable": variable,
                "label": label,
                "role": role,
                "n_total": n_total,
                "missing_count": missing_display,
                "missing_percent": missing_percent,
                "nonmissing_count": nonmissing_count,
                "status": status,
                "notes": notes,
            }
        else:
            record = {
                "variable": variable,
                "label": label,
                "role": role,
                "n_total": n_total,
                "missing_count": "N/A",
                "missing_percent": "N/A",
                "nonmissing_count": "N/A",
                "status": "not_found",
                "notes": (
                    notes
                    if notes
                    else "Variable referenced in hypotheses but not present in dataset."
                ),
            }
        records.append(record)

    out_df = pd.DataFrame(records)
    out_df.to_csv(out_csv_path, index=False)

    pattern_records = []
    if present_variables and not df.empty:
        complete_cases = int((~df.isna().any(axis=1)).sum())
        missing_any = n_total - complete_cases
        complete_percent = f"{(complete_cases / n_total) * 100:.2f}%"
        missing_display, missing_percent, status = suppress_count(
            missing_any, threshold, n_total
        )
        pattern_records.append(
            {
                "pattern": "Complete cases across key variables",
                "count": complete_cases,
                "percent": complete_percent,
                "status": "ok",
                "notes": "",
            }
        )
        pattern_records.append(
            {
                "pattern": "Missing in ≥1 key variable",
                "count": missing_display,
                "percent": missing_percent,
                "status": status,
                "notes": "Suppressed if below disclosure threshold.",
            }
        )
    else:
        pattern_records.append(
            {
                "pattern": "No hypothesis variables present in dataset",
                "count": "N/A",
                "percent": "N/A",
                "status": "not_found",
                "notes": "Verify hypotheses.csv against dataset schema.",
            }
        )

    patterns_df = pd.DataFrame(pattern_records)
    patterns_df.to_csv(out_patterns_path, index=False)

    metadata = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "seed": seed,
        "dataset": str(dataset_path),
        "variables_profiled": key_variables,
        "outputs": {
            "variable_summary": str(out_csv_path),
            "pattern_summary": str(out_patterns_path),
        },
        "threshold": threshold,
    }
    meta_path = out_csv_path.with_suffix(".meta.json")
    meta_path.write_text(json.dumps(metadata, indent=2))


if __name__ == "__main__":
    main()
