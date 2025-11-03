#!/usr/bin/env python3
"""
Align the project codebook with the observed dataset schema.

Outputs a JSON codebook enriched with storage metadata, value distributions,
and reproducibility notes so downstream analyses can validate assumptions.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
from pathlib import Path
from typing import Any, Dict, List, Optional

import pandas as pd
import yaml
import re


DEFAULT_VALUE_LABELS: Dict[str, Dict[str, str]] = {
    "classchild": {
        "0": "Lower class",
        "1": "Working class",
        "2": "Lower middle class",
        "3": "Middle class",
        "4": "Upper middle class",
        "5": "Upper class",
        "6": "Upper upper class",
    },
    "classcurrent": {
        "0": "Lower class",
        "1": "Working class",
        "2": "Lower middle class",
        "3": "Middle class",
        "4": "Upper middle class",
        "5": "Upper class",
        "6": "Upper upper class",
    },
    "I love myself (2l8994l)": {
        "-3": "Strongly disagree",
        "-2": "Disagree",
        "-1": "Somewhat disagree",
        "0": "Neutral",
        "1": "Somewhat agree",
        "2": "Agree",
        "3": "Strongly agree",
    },
    "I tend to suffer from depression (wz901dj)": {
        "-3": "Strongly disagree",
        "-2": "Disagree",
        "-1": "Somewhat disagree",
        "0": "Neutral",
        "1": "Somewhat agree",
        "2": "Agree",
        "3": "Strongly agree",
    },
    "I tend to suffer from anxiety (npvfh98)-neg": {
        "-3": "Strongly disagree",
        "-2": "Disagree",
        "-1": "Somewhat disagree",
        "0": "Neutral",
        "1": "Somewhat agree",
        "2": "Agree",
        "3": "Strongly agree",
    },
}


def load_config(path: Path) -> Dict[str, Any]:
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as fh:
        return yaml.safe_load(fh) or {}


def load_existing_codebook(path: Path) -> Dict[str, Any]:
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as fh:
        return json.load(fh)


def coerce_variable_list(
    args_vars: Optional[List[str]], existing: Dict[str, Any], observed: pd.DataFrame
) -> List[str]:
    if args_vars:
        return args_vars
    if "variables" in existing:
        return [entry["name"] for entry in existing["variables"]]
    return list(observed.columns)


def summarise_series(series: pd.Series) -> Dict[str, Any]:
    desc = series.dropna().describe()
    summary: Dict[str, Any] = {
        "count": float(desc["count"]) if "count" in desc else 0.0,
        "mean": float(desc["mean"]) if "mean" in desc else None,
        "std": float(desc["std"]) if "std" in desc else None,
        "min": float(desc["min"]) if "min" in desc else None,
        "q1": float(series.quantile(0.25)) if series.notna().any() else None,
        "median": float(series.median()) if series.notna().any() else None,
        "q3": float(series.quantile(0.75)) if series.notna().any() else None,
        "max": float(desc["max"]) if "max" in desc else None,
        "n_missing": int(series.isna().sum()),
        "unique": int(series.nunique(dropna=True)),
    }
    return summary


def infer_allowed_values(series: pd.Series) -> List[Any]:
    if series.dropna().empty:
        return []
    unique_sorted = sorted(series.dropna().unique())
    formatted: List[Any] = []
    for value in unique_sorted:
        if isinstance(value, float) and value.is_integer():
            formatted.append(int(value))
        else:
            formatted.append(value)
    return formatted


def build_variable_entry(
    name: str,
    label_lookup: Dict[str, Any],
    series: pd.Series,
    generated_at: str,
) -> Dict[str, Any]:
    existing_entry = next((entry for entry in label_lookup if entry.get("name") == name), {})
    label = existing_entry.get("label") or name
    analysis_role = existing_entry.get("analysis_role", "unspecified")
    variable_type = existing_entry.get("type", "unknown")
    notes = existing_entry.get("notes", existing_entry.get("values_note"))

    entry: Dict[str, Any] = {
        "name": name,
        "label": label,
        "question_text": existing_entry.get("question_text"),
        "analysis_role": analysis_role,
        "type": variable_type,
        "storage": str(series.dtype),
        "allowed_values": infer_allowed_values(series),
        "value_labels": existing_entry.get("value_labels")
        or DEFAULT_VALUE_LABELS.get(name),
        "missing_codes": existing_entry.get("missing_codes", []),
        "summary_stats": summarise_series(series),
    }
    if notes:
        notes = re.sub(
            r"Empirical alignment [0-9T:\-]+Z",
            f"Empirical alignment {generated_at}",
            notes,
        )
        if "Empirical alignment" not in notes:
            notes = f"{notes} | Empirical alignment {generated_at}"
        entry["notes"] = notes
    else:
        entry["notes"] = f"Empirical alignment {generated_at}; confirm instrument labels."
    return entry


def main() -> None:
    parser = argparse.ArgumentParser(description="Align codebook schema with observed dataset columns.")
    parser.add_argument("--dataset", required=True, help="Path to the source dataset.")
    parser.add_argument("--codebook-in", help="Existing codebook to update.")
    parser.add_argument("--codebook-out", required=True, help="Destination for the regenerated codebook.")
    parser.add_argument("--config", default="config/agent_config.yaml", help="Agent configuration file.")
    parser.add_argument("--variables", nargs="*", help="Optional subset of variables to document.")
    args = parser.parse_args()

    dataset_path = Path(args.dataset)
    codebook_in_path = Path(args.codebook_in) if args.codebook_in else Path(args.codebook_out)
    codebook_out_path = Path(args.codebook_out)
    config_path = Path(args.config)

    config = load_config(config_path)
    seed = config.get("seed", None)

    existing = load_existing_codebook(codebook_in_path)
    df = pd.read_csv(dataset_path, low_memory=False)

    variables_to_include = coerce_variable_list(args.variables, existing, df)

    existing_variables = existing.get("variables", [])
    label_lookup = existing_variables if isinstance(existing_variables, list) else []

    generated_at = dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")

    documented_variables: List[Dict[str, Any]] = []
    for name in variables_to_include:
        if name not in df.columns:
            continue
        entry = build_variable_entry(
            name,
            label_lookup,
            df[name],
            generated_at=generated_at,
        )
        documented_variables.append(entry)

    output: Dict[str, Any] = {
        "dataset": dataset_path.name,
        "generated_at": generated_at,
        "row_count": int(df.shape[0]),
        "column_count": int(df.shape[1]),
        "seed": seed,
        "variables": documented_variables,
        "weights_reference": existing.get("weights_reference"),
        "regeneration": {
            "command": (
                "python analysis/code/align_codebook_schema.py "
                f"--dataset {dataset_path} --codebook-in {codebook_in_path} --codebook-out {codebook_out_path}"
            ),
            "seed": seed,
            "created_by": "analysis/code/align_codebook_schema.py",
        },
        "notes": (
            f"Schema aligned with observed dataset on {generated_at}; verify value labels with source instrument."
        ),
    }

    codebook_out_path.parent.mkdir(parents=True, exist_ok=True)
    with codebook_out_path.open("w", encoding="utf-8") as fh:
        json.dump(output, fh, indent=2, ensure_ascii=True)


if __name__ == "__main__":
    main()
