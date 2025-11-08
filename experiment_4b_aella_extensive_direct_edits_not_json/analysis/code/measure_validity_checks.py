#!/usr/bin/env python3
"""Compute measurement validity diagnostics (reliability + DIF checks)."""

from __future__ import annotations

import argparse
import importlib.util
import sys
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import statsmodels.api as sm

REPO_ROOT = Path(__file__).resolve().parents[2]
RUN_MODELS_PATH = REPO_ROOT / "analysis" / "code" / "run_models.py"


def load_run_models_module():
    spec = importlib.util.spec_from_file_location("run_models_module", RUN_MODELS_PATH)
    module = importlib.util.module_from_spec(spec)
    sys.modules["run_models_module"] = module
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Measurement validity checker.")
    parser.add_argument(
        "--config",
        default="config/agent_config.yaml",
        help="Path to the agent configuration YAML.",
    )
    parser.add_argument(
        "--output-md",
        default="qc/measures_validity.md",
        help="Path to write the Markdown table.",
    )
    parser.add_argument(
        "--output-json",
        default="artifacts/measurement_validity_loop003.json",
        help="Path to write the structured JSON summary.",
    )
    return parser.parse_args()


@dataclass
class MeasureSpec:
    measure_id: str
    column: str
    coding: str
    notes: str
    group_var: str = "biomale"


def compute_dif(df: pd.DataFrame, measure_col: str, group_col: str) -> dict[str, Any]:
    subset = df[[measure_col, group_col]].dropna()
    if subset.empty:
        return {"effect": None, "p_value": None, "n": 0}
    X = sm.add_constant(subset[group_col])
    model = sm.OLS(subset[measure_col], X)
    result = model.fit()
    effect = float(result.params[group_col])
    p_value = float(result.pvalues[group_col])
    return {"effect": effect, "p_value": p_value, "n": int(result.nobs)}


def main():
    args = parse_args()
    rm = load_run_models_module()
    config = rm.load_config(args.config)
    dataset_path = rm.resolve_dataset_path(config["paths"]["raw_data"])
    codebook_path = rm.resolve_repo_path(config["paths"]["codebook"])
    alias_map = rm.load_codebook_alias_map(codebook_path)
    df_raw = rm.load_analysis_frame(dataset_path, alias_map)
    prepared = rm.prepare_variables(df_raw)
    codebook = json.loads(codebook_path.read_text())
    codebook_lookup = {
        entry["name"]: entry for entry in codebook.get("variables", []) if entry.get("name")
    }

    specs = [
        MeasureSpec(
            "wz901dj",
            "wz901dj_score",
            "Likert -3..3 (higher = more depression)",
            "Outcome for H1.",
        ),
        MeasureSpec(
            "externalreligion",
            "externalreligion_ord",
            "Ordinal 0-4 (higher = stricter adherence)",
            "Predictor for H1; coded from numeric/text scale.",
        ),
        MeasureSpec(
            "pqo6jmj",
            "pqo6jmj_score",
            "Likert -3..3 (higher = more guidance)",
            "Predictor for H2.",
        ),
        MeasureSpec(
            "okq5xh8",
            "okq5xh8_ord",
            "Ordinal 0-4 (poor→excellent)",
            "Outcome for H2.",
        ),
        MeasureSpec(
            "mds78zu",
            "mds78zu_binary",
            "Binary indicator (1 = any reported abuse > neutral)",
            "Predictor for H3 (derived from Likert).",
        ),
        MeasureSpec(
            "2l8994l",
            "self_love_score",
            "Likert -3..3 (higher = more self-love)",
            "Outcome for H3.",
        ),
    ]

    rows: list[dict[str, Any]] = []
    for spec in specs:
        entry = codebook_lookup.get(spec.measure_id, {})
        wording = entry.get("label") or entry.get("original_question") or spec.measure_id
        series = prepared.get(spec.column)
        if series is None:
            raise KeyError(f"Prepared dataframe missing column '{spec.column}'.")
        dif_stats = compute_dif(prepared, spec.column, spec.group_var)
        reliability = "single_item"
        if dif_stats["effect"] is None:
            dif_text = "Insufficient data"
        else:
            dif_text = (
                f"Δ({spec.group_var}=1 minus 0) = {dif_stats['effect']:.3f} "
                f"(p = {dif_stats['p_value']:.3f}, n = {dif_stats['n']})"
            )
        rows.append(
            {
                "measure_id": spec.measure_id,
                "item_wording": wording,
                "coding": spec.coding,
                "reliability_alpha": reliability,
                "dif_check": dif_text,
                "notes": spec.notes,
            }
        )

    md_lines = [
        "# Measurement Validity Dossier (Loop 003)",
        "",
        f"_Command_: `python analysis/code/measure_validity_checks.py --config {args.config} "
        f"--output-md {args.output_md} --output-json {args.output_json}`",
        "",
        "measure_id | item_wording | coding | reliability_alpha | dif_check | notes",
        "--- | --- | --- | --- | --- | ---",
    ]
    for row in rows:
        md_lines.append(
            f"{row['measure_id']} | {row['item_wording']} | {row['coding']} | "
            f"{row['reliability_alpha']} | {row['dif_check']} | {row['notes']}"
        )

    md_path = Path(args.output_md)
    md_path.parent.mkdir(parents=True, exist_ok=True)
    md_path.write_text("\n".join(md_lines))

    json_path = Path(args.output_json)
    json_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(rows, indent=2))


if __name__ == "__main__":
    main()
