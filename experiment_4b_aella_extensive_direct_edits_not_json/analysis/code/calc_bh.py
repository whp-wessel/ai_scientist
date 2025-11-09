#!/usr/bin/env python3
"""
Benjamini-Hochberg (BH) q-value calculator scoped by hypothesis family.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Dict

import pandas as pd
import yaml


REQUIRED_COLUMNS = ["hypothesis_id", "family", "targeted", "p_value"]


def load_config(config_path: Path) -> Dict:
    if not config_path.exists():
        return {}
    return yaml.safe_load(config_path.read_text())


def validate_columns(df: pd.DataFrame) -> None:
    missing = [col for col in REQUIRED_COLUMNS if col not in df.columns]
    if missing:
        raise ValueError(f"Input CSV missing required columns: {missing}")


def compute_bh_for_family(family_df: pd.DataFrame) -> Dict[str, float]:
    targeted_mask = family_df["targeted"].astype(str).str.upper() == "Y"
    targeted = family_df[targeted_mask]
    if targeted.empty:
        return {}

    ordered = targeted["p_value"].astype(float).sort_values()
    m = len(ordered)
    bh_values = (ordered * m / pd.Series(range(1, m + 1), index=ordered.index)).clip(upper=1.0)
    adjusted = bh_values.iloc[::-1].cummin().iloc[::-1]
    return adjusted.to_dict()


def apply_bh(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    if "q_value" not in df.columns:
        df["q_value"] = ""
    if "bh_in_scope" not in df.columns:
        df["bh_in_scope"] = ""
    df["bh_in_scope"] = df["bh_in_scope"].astype(str)

    for family, fam_df in df.groupby("family"):
        q_values = compute_bh_for_family(fam_df)
        targeted_ids = fam_df.loc[fam_df["targeted"].astype(str).str.upper() == "Y", "hypothesis_id"].tolist()
        scope_str = "|".join(targeted_ids)
        df.loc[fam_df.index, "bh_in_scope"] = scope_str
        for idx, q_val in q_values.items():
            df.at[idx, "q_value"] = float(q_val)

    return df


def summarize(df: pd.DataFrame, alpha: float) -> Dict:
    summary = {"alpha": alpha, "families": []}
    for family, fam_df in df.groupby("family"):
        targeted_ids = fam_df.loc[fam_df["targeted"].astype(str).str.upper() == "Y", "hypothesis_id"].tolist()
        summary["families"].append(
            {
                "family": family,
                "targeted_ids": targeted_ids,
                "bh_in_scope": "|".join(targeted_ids),
            }
        )
    return summary


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Apply BH q-values within each hypothesis family.")
    parser.add_argument("--config", default="config/agent_config.yaml", type=Path, help="Config file (for default q threshold).")
    parser.add_argument("--input-csv", default="analysis/results_pre_bh.csv", type=Path, help="Input CSV with hypothesis-level p-values.")
    parser.add_argument("--output-csv", default="analysis/results.csv", type=Path, help="Output CSV with q-values.")
    parser.add_argument("--summary-json", default="artifacts/bh_summary.json", type=Path, help="Summary JSON path.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    df = pd.read_csv(args.input_csv)
    validate_columns(df)

    config = load_config(args.config)
    alpha = config.get("fdr", {}).get("q", 0.05)

    df_with_q = apply_bh(df)

    args.output_csv.parent.mkdir(parents=True, exist_ok=True)
    df_with_q.to_csv(args.output_csv, index=False)

    summary = summarize(df_with_q, alpha)
    summary_path = args.summary_json
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    summary_path.write_text(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
