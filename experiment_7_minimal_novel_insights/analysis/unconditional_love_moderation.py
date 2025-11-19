#!/usr/bin/env python3
"""Assess whether unconditional parental love buffers purity-culture recall effects."""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any, Dict, Iterable, List

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import statsmodels.api as sm

ROOT = Path(__file__).resolve().parents[1]
TABLES_DIR = ROOT / "tables"
FIGURES_DIR = ROOT / "figures"
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


def slope_summary(
    result: sm.regression.linear_model.RegressionResultsWrapper,
    base_term: str,
    interaction_term: str,
    moderator_values: Iterable[float],
) -> Dict[str, Dict[str, float]]:
    return {
        str(value): simple_slope(result, base_term, interaction_term, value)
        for value in moderator_values
    }


def run_unconditional_models(module: Any, df: pd.DataFrame) -> Dict[str, Any]:
    df = df.dropna(subset=["unconditional_love_13_z"]).copy()
    df["purity13_unconditional"] = df["purity13_z"] * df["unconditional_love_13_z"]
    covariates = [f"{col}_c" for col in module.CENTER_COLUMNS]
    gender_dummies = [col for col in df.columns if col.startswith("gender_cat_")]
    base_features = ["purity0_z", *covariates, *gender_dummies]
    features = ["purity13_z", "unconditional_love_13_z", "purity13_unconditional", *base_features]

    results: List[Dict[str, float]] = []
    slopes: Dict[str, Dict[str, Any]] = {}
    for outcome in ["self_love", "romantic_satisfaction", "anxiety"]:
        result = module.run_ols(outcome, features, df)
        results.extend(
            module.summarize_model(
                result,
                outcome,
                "Hyp3_unconditional_love",
                ["purity13_z", "unconditional_love_13_z", "purity13_unconditional", "purity0_z"],
                df,
            )
        )
        slopes[outcome] = {
            "purity_at_low_love": simple_slope(result, "purity13_z", "purity13_unconditional", -1.0),
            "purity_at_high_love": simple_slope(result, "purity13_z", "purity13_unconditional", 1.0),
            "love_at_low_purity": simple_slope(result, "unconditional_love_13_z", "purity13_unconditional", -1.0),
            "love_at_high_purity": simple_slope(result, "unconditional_love_13_z", "purity13_unconditional", 1.0),
        }
    summary = {
        "nobs": int(df.shape[0]),
        "results": results,
        "slopes": slopes,
    }
    return summary


def plot_unconditional_margins(
    module: Any,
    df: pd.DataFrame,
    result: sm.regression.linear_model.RegressionResultsWrapper,
    features: List[str],
) -> None:
    purity_seq = np.linspace(df["purity13_z"].quantile(0.05), df["purity13_z"].quantile(0.95), 100)
    love_levels = {"Low unconditional love": -1.0, "High unconditional love": 1.0}
    covariate_defaults = {f"{col}_c": 0.0 for col in module.CENTER_COLUMNS}
    gender_dummies = [col for col in df.columns if col.startswith("gender_cat_")]
    for name in gender_dummies:
        covariate_defaults[name] = 0.0
    fig, ax = plt.subplots(figsize=(6, 4))
    for label, love_value in love_levels.items():
        data = pd.DataFrame(
            {
                "purity13_z": purity_seq,
                "unconditional_love_13_z": love_value,
                "purity13_unconditional": purity_seq * love_value,
                "purity0_z": 0.0,
                **covariate_defaults,
            }
        )
        X = sm.add_constant(data[features], has_constant="add")
        preds = result.get_prediction(X)
        frame = preds.summary_frame(alpha=0.05)
        ax.plot(purity_seq, frame["mean"], label=label)
        ax.fill_between(purity_seq, frame["mean_ci_lower"], frame["mean_ci_upper"], alpha=0.2)
    ax.set_xlabel("Purity messaging (z)")
    ax.set_ylabel("Predicted self-love")
    ax.set_title("Unconditional love buffers purity culture costs")
    ax.legend()
    fig.tight_layout()
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    fig.savefig(FIGURES_DIR / "marginal_unconditional_love_self_love.png", dpi=300)
    plt.close(fig)


def main() -> None:
    module = load_pipeline_module()
    df = module.prepare_analytic_sample()
    summary = run_unconditional_models(module, df)
    TABLES_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(summary["results"]).to_csv(
        TABLES_DIR / "regression_results_unconditional_love.csv", index=False
    )
    (TABLES_DIR / "simple_slopes_unconditional_love.json").write_text(
        json.dumps(summary["slopes"], indent=2), encoding="utf-8"
    )
    outputs = {
        "nobs": summary["nobs"],
        "notes": "Purity × unconditional love interactions saved in regression output and in slopes JSON.",
    }
    (OUTPUT_DIR / "unconditional_love_summary.json").write_text(
        json.dumps(outputs, indent=2), encoding="utf-8"
    )

    # Plot self-love margins with unconditional love at ±1 SD
    df_plot = df.dropna(subset=["unconditional_love_13_z", "purity13_z"]).copy()
    df_plot["purity13_unconditional"] = df_plot["purity13_z"] * df_plot["unconditional_love_13_z"]
    features = [
        "purity13_z",
        "unconditional_love_13_z",
        "purity13_unconditional",
        "purity0_z",
        *[f"{col}_c" for col in module.CENTER_COLUMNS],
        *[col for col in df_plot.columns if col.startswith("gender_cat_")],
    ]
    result_sl = module.run_ols("self_love", features, df_plot)
    plot_unconditional_margins(module, df_plot, result_sl, features)
    print("[analysis] Unconditional love moderation complete.")


if __name__ == "__main__":
    main()
