#!/usr/bin/env python3
"""Compute simple slopes for the registered moderation tests."""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any, Dict, Iterable

import statsmodels.api as sm

ROOT = Path(__file__).resolve().parents[1]
OUTPUT_PATH = ROOT / "tables" / "simple_slopes.json"
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


def slope_summary(
    result: sm.regression.linear_model.RegressionResultsWrapper,
    base_term: str,
    interaction_term: str,
    moderator_values: Iterable[float],
) -> Dict[str, Dict[str, float]]:
    return {
        str(value): {**simple_slope(result, base_term, interaction_term, value)}
        for value in moderator_values
    }


def slope_and_diff(
    result: sm.regression.linear_model.RegressionResultsWrapper,
    base_term: str,
    interaction_term: str,
) -> Dict[str, Dict[str, float]]:
    params = result.params
    cov = result.cov_params()
    cis_slope = float(params[base_term])
    gender_slope = float(params[base_term] + params[interaction_term])
    cov_base_inter = float(cov.loc[base_term, interaction_term])
    var_base = float(cov.loc[base_term, base_term])
    var_inter = float(cov.loc[interaction_term, interaction_term])
    var_gender = var_base + var_inter + 2 * cov_base_inter
    se_cis = math.sqrt(max(var_base, 0.0))
    se_gender = math.sqrt(max(var_gender, 0.0))
    diff = float(params[interaction_term])
    se_diff = math.sqrt(max(var_inter, 0.0))
    return {
        "cis": {"slope": cis_slope, "se": se_cis},
        "gender_minority": {"slope": gender_slope, "se": se_gender},
        "difference": {"slope": diff, "se": se_diff},
    }


def run_hyp1_summary(module: Any, df: pd.DataFrame) -> Dict[str, Any]:
    configs = module.hyp1_model_configs(df)
    label, features, _ = configs[0]
    result = module.run_ols("self_love", features, df)
    return {
        "model": label,
        "nobs": int(result.nobs),
        "purity_slopes": slope_summary(result, "purity13_z", "purity13_support", [-1.0, 1.0]),
        "support_slopes": slope_summary(result, "parent_support_z", "purity13_support", [-1.0, 1.0]),
    }


def run_hyp2_summary(module: Any, df: pd.DataFrame) -> Dict[str, Any]:
    outcomes = ["self_love", "romantic_satisfaction", "anxiety"]
    exposure_pairs = [
        ("purity13_z", "purity13_x_gender_minority", "Hyp2_gender_purity13"),
        ("purity0_z", "purity0_x_gender_minority", "Hyp2_gender_purity0"),
    ]
    summaries: Dict[str, Any] = {}
    for outcome in outcomes:
        summaries[outcome] = {}
        for base, interaction, name in exposure_pairs:
            features = module.hyp2_base_features(df) + [interaction]
            result = module.run_ols(outcome, features, df)
            summaries[outcome][name] = {
                "nobs": int(result.nobs),
                "slopes": slope_and_diff(result, base, interaction),
            }
    return summaries


def main() -> None:
    module = load_pipeline_module()
    df = module.prepare_analytic_sample()
    summary = {
        "hyp1": run_hyp1_summary(module, df),
        "hyp2": run_hyp2_summary(module, df),
    }
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as fh:
        json.dump(summary, fh, indent=2)
    print(f"Simple slope summary saved to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
