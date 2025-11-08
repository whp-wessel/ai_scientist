#!/usr/bin/env python3
"""
Deterministic hot-deck multiple imputation + stacked export utility.

The procedure replicates across runs given the same seed and input data order.
Numeric and categorical variables are imputed separately using observed
 distributions (with replacement) to emulate predictive mean matching.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np
import pandas as pd
import yaml


def resolve_input_path(config_path: Path, explicit_input: str | None) -> Path:
    """Determine the dataset path using CLI input or config defaults."""
    if explicit_input:
        candidate = Path(explicit_input)
        if candidate.exists():
            return candidate
        # Fall back to data/raw/ if relative path missing
        alt = Path("data/raw") / explicit_input
        if alt.exists():
            return alt
        raise FileNotFoundError(f"Input file not found: {explicit_input}")

    config = yaml.safe_load(Path(config_path).read_text())
    raw_name = config.get("paths", {}).get("raw_data")
    if not raw_name:
        raise ValueError("Config missing paths.raw_data entry.")
    candidates = [Path(raw_name), Path("data/raw") / raw_name]
    for path in candidates:
        if path.exists():
            return path
    raise FileNotFoundError(f"Raw data not found using config hint: {raw_name}")


def load_frame(path: Path) -> pd.DataFrame:
    if path.suffix.lower() == ".parquet":
        return pd.read_parquet(path)
    return pd.read_csv(path)


def infer_types(df: pd.DataFrame) -> Tuple[List[str], List[str]]:
    numeric_cols = df.select_dtypes(include=["number"]).columns.tolist()
    categorical_cols = [col for col in df.columns if col not in numeric_cols]
    return numeric_cols, categorical_cols


def hot_deck_impute(df: pd.DataFrame, rng: np.random.Generator, numeric_cols: List[str], categorical_cols: List[str]) -> pd.DataFrame:
    imputed = df.copy()

    for col in numeric_cols:
        mask = imputed[col].isna()
        if not mask.any():
            continue
        candidates = imputed.loc[~mask, col].to_numpy()
        if candidates.size == 0:
            continue
        fill_values = rng.choice(candidates, size=mask.sum())
        imputed.loc[mask, col] = fill_values

    for col in categorical_cols:
        mask = imputed[col].isna()
        if not mask.any():
            continue
        candidates = imputed.loc[~mask, col].astype(str).to_numpy()
        if candidates.size == 0:
            continue
        fill_values = rng.choice(candidates, size=mask.sum())
        imputed.loc[mask, col] = fill_values

    return imputed


def impute_and_stack(df: pd.DataFrame, m: int, seed: int) -> Tuple[pd.DataFrame, Dict[str, Dict[str, int]]]:
    numeric_cols, categorical_cols = infer_types(df)
    stacked_frames = []
    imputed_missingness = {}

    for draw in range(1, m + 1):
        # advance generator deterministically for each draw
        draw_seed = seed + draw
        draw_rng = np.random.default_rng(draw_seed)
        imputed = hot_deck_impute(df, draw_rng, numeric_cols, categorical_cols)
        imputed["imputation_id"] = draw
        stacked_frames.append(imputed)
        imputed_missingness[f"imputation_{draw}"] = imputed.isna().sum().to_dict()

    stacked = pd.concat(stacked_frames, ignore_index=True)
    return stacked, imputed_missingness


def write_outputs(stacked: pd.DataFrame, stacked_path: Path, summary_path: Path, metadata: Dict[str, object]) -> None:
    stacked_path.parent.mkdir(parents=True, exist_ok=True)
    actual_path = stacked_path
    if stacked_path.suffix.lower() == ".parquet":
        try:
            stacked.to_parquet(stacked_path, index=False)
        except (ImportError, ValueError) as err:
            actual_path = stacked_path.with_suffix(".csv")
            stacked.to_csv(actual_path, index=False)
            metadata["parquet_fallback_reason"] = str(err)
    else:
        stacked.to_csv(stacked_path, index=False)

    metadata["stacked_output_actual"] = str(actual_path)
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    summary_path.write_text(json.dumps(metadata, indent=2))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Deterministic hot-deck multiple imputation.")
    parser.add_argument("--config", default="config/agent_config.yaml", type=Path, help="Config file with default paths.")
    parser.add_argument("--input", default=None, help="Optional explicit input dataset path.")
    parser.add_argument("--m", type=int, default=5, help="Number of imputations to draw.")
    parser.add_argument("--seed", type=int, default=None, help="Random seed; defaults to config seed.")
    parser.add_argument("--stacked-output", default="data/clean/childhood_imputed_stack.parquet", type=Path, help="Path for stacked imputed dataset (parquet or csv).")
    parser.add_argument("--summary-output", default="artifacts/imputation_summary.json", type=Path, help="Path for JSON summary diagnostics.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    config_seed = yaml.safe_load(Path(args.config).read_text()).get("seed")
    seed = args.seed if args.seed is not None else config_seed
    if seed is None:
        raise ValueError("Seed must be specified via --seed or config/agent_config.yaml.")

    input_path = resolve_input_path(Path(args.config), args.input)
    df = load_frame(input_path)
    stacked, imputed_missingness = impute_and_stack(df, args.m, seed)

    metadata = {
        "input_path": str(input_path),
        "stacked_output": str(args.stacked_output),
        "summary_output": str(args.summary_output),
        "seed": seed,
        "m": args.m,
        "rows_per_imputation": len(df),
        "missing_before": df.isna().sum().to_dict(),
        "missing_after_by_imputation": imputed_missingness,
    }

    write_outputs(stacked, args.stacked_output, args.summary_output, metadata)


if __name__ == "__main__":
    main()
