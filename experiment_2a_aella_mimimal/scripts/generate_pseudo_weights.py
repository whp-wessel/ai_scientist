#!/usr/bin/env python3
"""
Generate deterministic pseudo-weights by calibrating sample margins to
external targets defined in docs/calibration_targets.yaml (or similar).

The script performs iterative proportional fitting (a.k.a. raking) using
uniform baseline weights and enforces reproducibility by:
  - reading the shared seed from config/agent_config.yaml (overridable);
  - logging the calibration tolerance, iteration count, and achieved errors;
  - ensuring category-level respondent counts stay above the privacy guardrail.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import math
import shlex
import sys
from pathlib import Path
from typing import Any, Dict, List, Tuple

import numpy as np
import pandas as pd
import yaml


PRIVACY_MIN_COUNT = 10


def load_yaml(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def build_dimension_columns(
    df: pd.DataFrame, targets_cfg: Dict[str, Any]
) -> List[Dict[str, Any]]:
    """Return dimension metadata including column names and target shares."""
    dimensions: List[Dict[str, Any]] = []
    for dim in targets_cfg.get("dimensions", []):
        name = dim["name"]
        dtype = dim.get("type", "categorical")
        dataset_column = dim["dataset_column"]
        column_name = dataset_column
        target_map: Dict[Any, float] = {}

        if dtype == "categorical":
            if dataset_column not in df.columns:
                raise KeyError(f"Column '{dataset_column}' missing for dimension '{name}'.")
            for cat in dim.get("categories", []):
                target_map[cat["value"]] = float(cat["target_share"])
        elif dtype == "numeric_binned":
            if dataset_column not in df.columns:
                raise KeyError(f"Column '{dataset_column}' missing for dimension '{name}'.")
            column_name = f"calib_{name}"
            bins = []
            labels = []
            shares = []
            for bin_cfg in dim.get("bins", []):
                bins.append((bin_cfg["min_inclusive"], bin_cfg["max_inclusive"]))
                labels.append(bin_cfg["label"])
                shares.append(float(bin_cfg["target_share"]))
            # Assign deterministic bins; values outside ranges become NaN -> handled via validation.
            df[column_name] = pd.Categorical(["__missing__"] * len(df), categories=labels)
            col_values = df[column_name].to_numpy().copy()
            data = df[dataset_column]
            for idx, (lower, upper) in enumerate(bins):
                label = labels[idx]
                mask = (data >= lower) & (data <= upper)
                col_values[mask.to_numpy()] = label
            df[column_name] = pd.Categorical(col_values, categories=labels, ordered=True)
            for label, share in zip(labels, shares):
                target_map[label] = share
        else:
            raise ValueError(f"Unsupported dimension type '{dtype}' for '{name}'.")

        total_share = sum(target_map.values())
        if not math.isclose(total_share, 1.0, abs_tol=1e-6):
            raise ValueError(f"Target shares for dimension '{name}' sum to {total_share}, not 1.0.")

        dimensions.append(
            {
                "name": name,
                "column": column_name,
                "targets": target_map,
                "type": dtype,
            }
        )
    return dimensions


def validate_min_counts(df: pd.DataFrame, dimensions: List[Dict[str, Any]]) -> None:
    for dim in dimensions:
        column = dim["column"]
        counts = df[column].value_counts(dropna=False)
        for category, _share in dim["targets"].items():
            count = int(counts.get(category, 0))
            if count < PRIVACY_MIN_COUNT:
                raise ValueError(
                    f"Dimension '{dim['name']}' category '{category}' has count {count} < {PRIVACY_MIN_COUNT}."
                )


def rake_weights(
    df: pd.DataFrame,
    dimensions: List[Dict[str, Any]],
    *,
    max_iter: int,
    tol: float,
) -> Tuple[np.ndarray, Dict[str, Any]]:
    weights = np.ones(len(df), dtype=float)
    total_weight = float(weights.sum())
    history: List[float] = []
    converged = False

    for iteration in range(1, max_iter + 1):
        for dim in dimensions:
            column = dim["column"]
            targets = dim["targets"]
            for category, target_share in targets.items():
                mask = (df[column] == category).to_numpy()
                current_total = weights[mask].sum()
                desired_total = target_share * total_weight
                if current_total <= 0:
                    raise ValueError(
                        f"Encountered zero weight for category '{category}' in dimension '{dim['name']}'."
                    )
                adjust_factor = desired_total / current_total
                weights[mask] *= adjust_factor
            # Maintain constant total weight after finishing one dimension.
            weight_sum = weights.sum()
            if weight_sum <= 0:
                raise ValueError("Weights collapsed to zero during raking.")
            weights *= total_weight / weight_sum
        max_error = 0.0
        for dim in dimensions:
            column = dim["column"]
            targets = dim["targets"]
            for category, target_share in targets.items():
                mask = (df[column] == category).to_numpy()
                current_share = weights[mask].sum() / total_weight
                max_error = max(max_error, abs(current_share - target_share))
        history.append(max_error)
        if max_error <= tol:
            converged = True
            break

    diagnostics = {
        "iterations": iteration,
        "converged": converged,
        "tolerance": tol,
        "max_abs_error": history[-1] if history else None,
        "error_history": history,
    }
    return weights, diagnostics


def compute_dimension_summaries(
    df: pd.DataFrame,
    weights: np.ndarray,
    dimensions: List[Dict[str, Any]],
) -> Dict[str, Dict[str, float]]:
    total_weight = weights.sum()
    summaries: Dict[str, Dict[str, float]] = {}
    for dim in dimensions:
        column = dim["column"]
        weighted_totals = (
            df.assign(__w=weights)
            .groupby(column, observed=True)["__w"]
            .sum()
        )
        summaries[dim["name"]] = {
            str(category): round(float(weighted_totals.get(category, 0.0) / total_weight), 6)
            for category in dim["targets"].keys()
        }
    return summaries


def main(argv: List[str]) -> None:
    parser = argparse.ArgumentParser(description="Generate deterministic pseudo-weights via raking.")
    parser.add_argument("--csv", required=True, help="Path to input CSV dataset.")
    parser.add_argument("--config", required=True, help="Path to YAML config with shared seed.")
    parser.add_argument("--targets", required=True, help="Path to YAML file with calibration targets.")
    parser.add_argument("--out", required=True, help="Path to write pseudo-weight CSV.")
    parser.add_argument("--manifest", required=True, help="Path to write manifest JSON.")
    parser.add_argument("--max-iter", type=int, default=50, help="Maximum raking iterations (default: 50).")
    parser.add_argument("--tol", type=float, default=1e-6, help="Convergence tolerance for marginal shares.")
    args = parser.parse_args(argv)

    csv_path = Path(args.csv)
    config_path = Path(args.config)
    targets_path = Path(args.targets)
    out_path = Path(args.out)
    manifest_path = Path(args.manifest)

    config = load_yaml(config_path)
    seed = int(config.get("seed", 20251016))
    np.random.seed(seed)

    targets_cfg = load_yaml(targets_path)
    df = pd.read_csv(csv_path, low_memory=False)

    dimensions = build_dimension_columns(df, targets_cfg)
    validate_min_counts(df, dimensions)

    weights, diagnostics = rake_weights(
        df,
        dimensions,
        max_iter=args.max_iter,
        tol=args.tol,
    )

    # Attach weights and export.
    output_df = pd.DataFrame({
        "record_id": df.index,
        "pseudo_weight": weights,
    })
    for dim in dimensions:
        output_df[dim["column"]] = df[dim["column"]]

    out_path.parent.mkdir(parents=True, exist_ok=True)
    output_df.to_csv(out_path, index=False)

    dimension_summaries = compute_dimension_summaries(df, weights, dimensions)

    manifest = {
        "analysis": "Scenario 1 proxy weight calibration",
        "command": shlex.join(["python", Path(__file__).as_posix(), *sys.argv[1:]]),
        "dataset": str(csv_path),
        "config": str(config_path),
        "targets": str(targets_path),
        "seed": seed,
        "timestamp_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
        "max_iter": args.max_iter,
        "tolerance": args.tol,
        "diagnostics": diagnostics,
        "dimension_targets": targets_cfg.get("dimensions", []),
        "achieved_shares": dimension_summaries,
        "privacy_guardrail": f"All calibration categories >= {PRIVACY_MIN_COUNT} respondents.",
        "outputs": {
            "pseudo_weights_csv": str(out_path),
        },
    }

    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    with manifest_path.open("w", encoding="utf-8") as handle:
        json.dump(manifest, handle, indent=2)


if __name__ == "__main__":
    main(sys.argv[1:])
