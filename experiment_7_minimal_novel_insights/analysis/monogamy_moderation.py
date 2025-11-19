#!/usr/bin/env python3
"""Estimate the purity × nonmonogamy moderation and archive the margins data."""

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
MARGINAL_DATA = ROOT / "analysis" / "marginal_nonmonogamy_data.csv"


def load_pipeline_module() -> Any:
    import importlib.util

    module_path = ROOT / "analysis" / "analysis_pipeline.py"
    spec = importlib.util.spec_from_file_location("analysis_pipeline", module_path)
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


def run_models(module: Any, df: pd.DataFrame) -> Dict[str, Any]:
    df = df.dropna(subset=["monogamy"]).copy()
    df["monogamy"] = df["monogamy"].astype(float)
    df["nonmon_pref"] = (df["monogamy"] <= -1.0).astype(int)
    df["purity13_nonmon"] = df["purity13_z"] * df["nonmon_pref"]

    covariates = [f"{col}_c" for col in module.CENTER_COLUMNS]
    gender_dummies = [col for col in df.columns if col.startswith("gender_cat_")]
    base_features = ["purity0_z", *covariates, *gender_dummies]
    features = ["purity13_z", "nonmon_pref", "purity13_nonmon", "parent_support_z", *base_features]

    results: List[Dict[str, float]] = []
    slopes: Dict[str, Dict[str, Dict[str, float]]] = {}
    for outcome in ["self_love", "romantic_satisfaction", "anxiety"]:
        result = module.run_ols(outcome, features, df)
        results.extend(
            module.summarize_model(
                result,
                outcome,
                "Hyp3_nonmonogamy",
                ["purity13_z", "nonmon_pref", "purity13_nonmon", "purity0_z"],
                df,
            )
        )
        slopes[outcome] = {
            "purity_at_monogamy": simple_slope(result, "purity13_z", "purity13_nonmon", 0.0),
            "purity_at_nonmonogamy": simple_slope(result, "purity13_z", "purity13_nonmon", 1.0),
            "nonmon_pref_at_low_purity": simple_slope(result, "nonmon_pref", "purity13_nonmon", -1.0),
            "nonmon_pref_at_high_purity": simple_slope(result, "nonmon_pref", "purity13_nonmon", 1.0),
        }
    summary = {
        "nobs": int(df.shape[0]),
        "nonmon_pref_n": int(df["nonmon_pref"].sum()),
        "nonmon_pref_pct": float(df["nonmon_pref"].mean()) * 100,
        "results": results,
        "slopes": slopes,
    }
    return summary, df, features


def make_margin_data(
    module: Any,
    df: pd.DataFrame,
    features: List[str],
    result: sm.regression.linear_model.RegressionResultsWrapper,
) -> pd.DataFrame:
    purity_seq = np.linspace(df["purity13_z"].quantile(0.05), df["purity13_z"].quantile(0.95), 100)
    covariate_defaults = {f"{col}_c": 0.0 for col in module.CENTER_COLUMNS}
    gender_dummies = [col for col in df.columns if col.startswith("gender_cat_")]
    for name in gender_dummies:
        covariate_defaults[name] = 0.0

    records: List[Dict[str, float]] = []
    for label, nonmon_value in [("Monogamous", 0.0), ("Nonmonogamous", 1.0)]:
        for purity in purity_seq:
            row = {
                "purity13_z": purity,
                "nonmon_pref": nonmon_value,
                "purity13_nonmon": purity * nonmon_value,
                "parent_support_z": 0.0,
                "purity0_z": 0.0,
                "group": label,
            }
            row.update(covariate_defaults)
            records.append(row)
    margin_df = pd.DataFrame(records)
    X = sm.add_constant(margin_df[features], has_constant="add")
    preds = result.get_prediction(X)
    frame = preds.summary_frame(alpha=0.05)
    margin_df["mean"] = frame["mean"]
    margin_df["ci_lower"] = frame["mean_ci_lower"]
    margin_df["ci_upper"] = frame["mean_ci_upper"]
    margin_df["purity"] = margin_df["purity13_z"]
    return margin_df


def plot_margins(margin_df: pd.DataFrame) -> None:
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(figsize=(6, 4))
    for label, group in margin_df.groupby("group"):
        ax.plot(group["purity"], group["mean"], label=label, linewidth=2)
        ax.fill_between(group["purity"], group["ci_lower"], group["ci_upper"], alpha=0.2)
    ax.set_xlabel("Adolescent purity messaging (z)")
    ax.set_ylabel("Predicted self-love")
    ax.set_title("Purity costs by monogamy preference")
    ax.legend()
    ax.grid(True, linestyle=":", color="gray", alpha=0.5)
    fig.tight_layout()
    fig.savefig(FIGURES_DIR / "marginal_nonmonogamy_self_love.png", dpi=300)
    plt.close(fig)


def main() -> None:
    module = load_pipeline_module()
    summary, df, features = run_models(module, module.prepare_analytic_sample())
    TABLES_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(summary["results"]).to_csv(
        TABLES_DIR / "regression_results_monogamy.csv", index=False
    )
    (TABLES_DIR / "simple_slopes_monogamy.json").write_text(
        json.dumps(summary["slopes"], indent=2), encoding="utf-8"
    )
    (OUTPUT_DIR / "monogamy_summary.json").write_text(
        json.dumps(
            {
                "nobs": summary["nobs"],
                "nonmon_pref_n": summary["nonmon_pref_n"],
                "nonmon_pref_pct": summary["nonmon_pref_pct"],
                "notes": "Nonmonogamy moderation for adolescent purity in tables/regression_results_monogamy.csv.",
            },
            indent=2,
        ),
        encoding="utf-8",
    )

    self_love_result = module.run_ols("self_love", features, df)
    margin_df = make_margin_data(module, df, features, self_love_result)
    margin_df.to_csv(MARGINAL_DATA, index=False)
    plot_margins(margin_df)
    print("Nonmonogamy moderation complete. Tables, slopes, and margins saved.")


if __name__ == "__main__":
    main()
