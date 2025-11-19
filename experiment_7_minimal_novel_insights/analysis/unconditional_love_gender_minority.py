#!/usr/bin/env python3
"""Analyze whether the purity × unconditional-love interaction differs by gender-minority status."""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any, Dict, Iterable, List

import pandas as pd
import statsmodels.api as sm

ROOT = Path(__file__).resolve().parents[1]
TABLES_DIR = ROOT / "tables"
OUTPUT_DIR = ROOT / "outputs"
PIPELINE_PATH = ROOT / "analysis" / "analysis_pipeline.py"


def load_pipeline_module() -> Any:
    import importlib.util

    spec = importlib.util.spec_from_file_location("analysis_pipeline", PIPELINE_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def simple_slope(
    result: sm.regression.linear_model.RegressionResultsWrapper,
    base_term: str,
    interaction_term: str,
    moderator_value: float,
) -> Dict[str, float]:
    params = result.params
    cov = result.cov_params()
    slope = float(params[base_term] + params[interaction_term] * moderator_value)
    var_base = float(cov.loc[base_term, base_term])
    var_inter = float(cov.loc[interaction_term, interaction_term])
    cov_base_inter = float(cov.loc[base_term, interaction_term])
    var = var_base + moderator_value**2 * var_inter + 2 * moderator_value * cov_base_inter
    se = math.sqrt(max(var, 0.0))
    return {"slope": slope, "se": se}


def run_group_models(module: Any, subset: pd.DataFrame) -> Dict[str, Any]:
    subset = subset.dropna(subset=["unconditional_love_13_z"]).copy()
    subset["purity13_unconditional"] = subset["purity13_z"] * subset["unconditional_love_13_z"]
    covariates = [f"{col}_c" for col in module.CENTER_COLUMNS]
    features = ["purity13_z", "unconditional_love_13_z", "purity13_unconditional", "purity0_z", *covariates]

    results: List[Dict[str, float]] = []
    slopes: Dict[str, Dict[str, Dict[str, float]]] = {}
    for outcome in ["self_love", "romantic_satisfaction", "anxiety"]:
        result = module.run_ols(
            outcome,
            features,
            subset,
        )
        results.extend(
            module.summarize_model(
                result,
                outcome,
                "Hyp3_unconditional_love",
                ["purity13_z", "unconditional_love_13_z", "purity13_unconditional", "purity0_z"],
                subset,
            )
        )
        slopes[outcome] = {
            "purity_at_low_love": simple_slope(result, "purity13_z", "purity13_unconditional", -1.0),
            "purity_at_high_love": simple_slope(result, "purity13_z", "purity13_unconditional", 1.0),
            "love_at_low_purity": simple_slope(result, "unconditional_love_13_z", "purity13_unconditional", -1.0),
            "love_at_high_purity": simple_slope(result, "unconditional_love_13_z", "purity13_unconditional", 1.0),
        }
    return {"results": results, "slopes": slopes, "nobs": int(subset.shape[0])}


def main() -> None:
    module = load_pipeline_module()
    df = module.prepare_analytic_sample()

    cis_categories = {"Woman (cis)", "Man (cis)"}
    gender_minority_cats = set(module.GENDER_MINORITY_CATEGORIES)
    groups: Dict[str, Iterable[str]] = {
        "cisgender": cis_categories,
        "gender_minority": gender_minority_cats,
    }

    all_records: List[Dict[str, Any]] = []
    all_slopes: Dict[str, Any] = {}
    sample_info: Dict[str, Any] = {}

    for label, categories in groups.items():
        subset = df[df["gender_category"].isin(categories)].copy()
        if subset.empty:
            continue
        summary = run_group_models(module, subset)
        for record in summary["results"]:
            record["group"] = label
        all_records.extend(summary["results"])
        all_slopes[label] = summary["slopes"]
        sample_info[f"{label}_n"] = summary["nobs"]

    TABLES_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    if all_records:
        pd.DataFrame(all_records).to_csv(
            TABLES_DIR / "regression_results_unconditional_love_gender_groups.csv",
            index=False,
        )
    (TABLES_DIR / "simple_slopes_unconditional_love_gender_groups.json").write_text(
        json.dumps(all_slopes, indent=2),
        encoding="utf-8",
    )

    overview = {
        **sample_info,
        "notes": (
            "Purity × unconditional-love interactions estimated separately within "
            "cisgender and gender-minority respondents."
        ),
    }
    (OUTPUT_DIR / "unconditional_love_gender_groups_summary.json").write_text(
        json.dumps(overview, indent=2), encoding="utf-8"
    )
    print("[analysis] Gender-group unconditional-love moderation complete.")


if __name__ == "__main__":
    main()
