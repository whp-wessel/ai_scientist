#!/usr/bin/env python3
"""Loop 020: Confirmatory-ready tables for the H4 religiosity × class interaction."""

from __future__ import annotations

from pathlib import Path
from typing import Dict, List

import pandas as pd

COEFF_PATH = Path("tables/loop020_h4_stress_test_coeffs.csv")
OUTPUT_PATH = Path("tables/loop016_h4_confirmatory.csv")
SCRIPT_CMD = "PYTHONHASHSEED=20251016 python scripts/loop020_h4_stress_tests.py"

INTERACTIONS: Dict[str, dict[str, str]] = {
    "religion_moderate_classchild_int": {
        "contrast_id": "H4_moderate_classchild",
        "estimand": "Moderate practice × childhood class interaction",
        "religion_level": "moderate",
    },
    "religion_serious_classchild_int": {
        "contrast_id": "H4_serious_classchild",
        "estimand": "Serious practice × childhood class interaction",
        "religion_level": "serious",
    },
}

OUTCOMES: List[dict[str, object]] = [
    {
        "outcome_id": "highflag",
        "model_id": "loop020_h4_highflag_logit",
        "label": "Binary high-anxiety flag (≥5 on either anxiety item)",
        "estimand_suffix": "log-odds of high anxiety (binary ≥5)",
        "prob_path": Path("tables/loop020_h4_highflag_prob_deltas.csv"),
        "prob_low_col": "predicted_prob_classchild_low",
        "prob_high_col": "predicted_prob_classchild_high",
        "delta_col": "delta_pp_within_level",
        "delta_vs_none_col": "delta_pp_vs_none",
        "contrast_suffix": "",
        "notes": "Predicted probabilities equal P(high anxiety ≥5).",
    },
    {
        "outcome_id": "ord3_top",
        "model_id": "loop020_h4_ord3_logit",
        "label": "Probability of being in the top 3-bin anxiety category",
        "estimand_suffix": "log-odds of occupying the highest ordinal anxiety bin",
        "prob_path": Path("tables/loop020_h4_ord3_prob_deltas.csv"),
        "prob_low_col": "predicted_prob_top_classchild_low",
        "prob_high_col": "predicted_prob_top_classchild_high",
        "delta_col": "delta_pp_within_level",
        "delta_vs_none_col": "delta_pp_vs_none",
        "contrast_suffix": "_ord3",
        "notes": "Probabilities equal P(anxiety_ord3 = 2).",
    },
]


def main() -> None:
    coeffs = pd.read_csv(COEFF_PATH)
    prob_tables = {
        outcome["outcome_id"]: pd.read_csv(outcome["prob_path"]).set_index("religion_level")
        for outcome in OUTCOMES
    }

    rows: list[dict[str, object]] = []
    for term, meta in INTERACTIONS.items():
        for outcome in OUTCOMES:
            prob_path = outcome["prob_path"]
            subset = coeffs[(coeffs["model_id"] == outcome["model_id"]) & (coeffs["term"] == term)]
            if subset.empty:
                continue
            row = subset.iloc[0]
            level = meta["religion_level"]
            prob_table = prob_tables[outcome["outcome_id"]]
            if level not in prob_table.index:
                raise KeyError(f"Missing probability row for {level} in {prob_path}")
            prob_low = float(prob_table.loc[level, outcome["prob_low_col"]])
            prob_high = float(prob_table.loc[level, outcome["prob_high_col"]])
            delta = float(prob_table.loc[level, outcome["delta_col"]])
            delta_vs_none = float(prob_table.loc[level, outcome["delta_vs_none_col"]])
            contrast_id = f"{meta['contrast_id']}{outcome['contrast_suffix']}"
            estimand = f"{meta['estimand']} — {outcome['estimand_suffix']}"
            model_desc = row.get(
                "model_desc",
                f"{row.get('estimator', 'model')} ({row.get('outcome', outcome['label'])}); penalty α={row.get('penalty_alpha', 0.0)}",
            )
            rows.append(
                {
                    "contrast_id": contrast_id,
                    "estimand": estimand,
                    "outcome_label": outcome["label"],
                    "model": model_desc,
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
                    "delta_pp_vs_none": delta_vs_none,
                    "script": SCRIPT_CMD,
                    "notes": f"Coefficients from {COEFF_PATH.name}; probabilities from {prob_path.name}. {outcome['notes']}",
                }
            )

    pd.DataFrame(rows).to_csv(OUTPUT_PATH, index=False)


if __name__ == "__main__":
    main()
