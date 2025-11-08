#!/usr/bin/env python3
"""Loop 016: Confirmatory-ready tables for the H4 religiosity × class interaction."""

from __future__ import annotations

from pathlib import Path
from typing import Dict

import pandas as pd

COEFF_PATH = Path("tables/loop015_h4_interactions_rich.csv")
GRID_PATH = Path("tables/loop015_h4_predicted_grid.csv")
OUTPUT_PATH = Path("tables/loop016_h4_confirmatory.csv")

INTERACTIONS: Dict[str, dict[str, str]] = {
    "religion_moderate_classchild_int": {
        "contrast_id": "H4_moderate_classchild",
        "estimand": "Moderate practice × childhood class interaction on log-odds of high anxiety",
        "religion_level": "moderate",
    },
    "religion_serious_classchild_int": {
        "contrast_id": "H4_serious_classchild",
        "estimand": "Serious practice × childhood class interaction on log-odds of high anxiety",
        "religion_level": "serious",
    },
}

CLASS_LOW = 0.0
CLASS_HIGH = 6.0


def lookup_probability(grid: pd.DataFrame, religion_level: str, class_value: float) -> float:
    """Return the predicted probability for the requested class/religion pair."""

    mask = (grid["religion_level"] == religion_level) & (grid["classchild"].sub(class_value).abs() < 1e-9)
    subset = grid.loc[mask, "predicted_prob"]
    if subset.empty:
        raise KeyError(f"Missing grid row for {religion_level=} at classchild={class_value}")
    return float(subset.iloc[0])


def main() -> None:
    coeffs = pd.read_csv(COEFF_PATH)
    grid = pd.read_csv(GRID_PATH)

    none_low = lookup_probability(grid, "none", CLASS_LOW)
    none_high = lookup_probability(grid, "none", CLASS_HIGH)
    none_delta = none_high - none_low

    rows: list[dict[str, object]] = []
    for term, meta in INTERACTIONS.items():
        subset = coeffs[(coeffs["model_id"] == "loop015_h4_highflag_rich") & (coeffs["term"] == term)]
        if subset.empty:
            raise RuntimeError(f"Missing coefficient for {term}")
        row = subset.iloc[0]
        level = meta["religion_level"]
        prob_low = lookup_probability(grid, level, CLASS_LOW)
        prob_high = lookup_probability(grid, level, CLASS_HIGH)
        delta = prob_high - prob_low
        rows.append(
            {
                "contrast_id": meta["contrast_id"],
                "estimand": meta["estimand"],
                "model": row["model_desc"],
                "n_obs": int(row["n_obs"]),
                "estimate_log_odds": float(row["estimate"]),
                "std_err": float(row["std_err"]),
                "ci_low": float(row["ci_low"]),
                "ci_high": float(row["ci_high"]),
                "p_value": float(row["p_value"]),
                "religion_level": level,
                "prob_classchild_low": prob_low,
                "prob_classchild_high": prob_high,
                "delta_pp_within_level": delta,
                "delta_pp_vs_none": delta - none_delta,
                "script": "PYTHONHASHSEED=20251016 python scripts/loop015_h4_rich_interactions.py",
                "notes": "Coefficients from tables/loop015_h4_interactions_rich.csv; predicted probabilities from tables/loop015_h4_predicted_grid.csv.",
            }
        )

    pd.DataFrame(rows).to_csv(OUTPUT_PATH, index=False)


if __name__ == "__main__":
    main()
