#!/usr/bin/env python3
"""Loop 011 benchmark: multinomial net-worth model versus PPO baseline."""

from __future__ import annotations

from pathlib import Path
from typing import List

import numpy as np
import pandas as pd
import statsmodels.api as sm

from loop010_h3_partial_models import prepare_base_dataframe

DATA_PATH = Path("childhoodbalancedpublic_original.csv")
TABLES_DIR = Path("tables")
TABLES_DIR.mkdir(parents=True, exist_ok=True)

MULTI_PARAM_PATH = TABLES_DIR / "loop011_h3_multinomial_params.csv"
MULTI_FIT_PATH = TABLES_DIR / "loop011_h3_multinomial_fit.csv"
MARGINAL_PATH = TABLES_DIR / "loop011_h3_multinomial_marginals.csv"
COMPARISON_PATH = TABLES_DIR / "loop011_h3_model_comparison.csv"
PPO_FIT_PATH = TABLES_DIR / "loop010_h3_partial_fit.csv"

PREDICTORS = [
    "classchild",
    "classteen",
    "selfage",
    "gendermale",
    "education",
    "classchild_male_int",
]


def fit_multinomial(df: pd.DataFrame) -> sm.discrete.discrete_model.MNLogitResults:
    """Fit the multinomial logit on the ordinal net-worth outcome."""

    subset = df.dropna(subset=["networth_ord", *PREDICTORS]).copy()
    y = subset["networth_ord"].astype(int)
    X = sm.add_constant(subset[PREDICTORS], has_constant="add")
    model = sm.MNLogit(y, X)
    return model.fit(disp=False, maxiter=300)


def export_params(result: sm.discrete.discrete_model.MNLogitResults) -> None:
    """Persist coefficient table in tidy long form."""

    rows: List[dict[str, object]] = []
    params = result.params
    for outcome in params.columns:
        outcome_level = int(outcome)
        for term in params.index:
            estimate = float(params.loc[term, outcome])
            se = float(result.bse.loc[term, outcome])
            z_value = float(estimate / se) if se > 0 else float("nan")
            p_value = float(result.pvalues.loc[term, outcome])
            rows.append(
                {
                    "outcome_level": outcome_level,
                    "term": term,
                    "estimate": estimate,
                    "std_err": se,
                    "z_value": z_value,
                    "p_value": p_value,
                }
            )
    pd.DataFrame(rows).to_csv(MULTI_PARAM_PATH, index=False)


def export_marginals(result: sm.discrete.discrete_model.MNLogitResults) -> None:
    """Store marginal effects for all predictors."""

    margeff = result.get_margeff(at="overall", method="dydx")
    frame = margeff.summary_frame()
    rows: list[dict[str, object]] = []
    for (outcome_label, term), row in frame.iterrows():
        outcome_level = int(outcome_label.split("=")[-1])
        rows.append(
            {
                "outcome_level": outcome_level,
                "term": term,
                "dy_dx": float(row["dy/dx"]),
                "std_err": float(row["Std. Err."]),
                "z_value": float(row["z"]),
                "p_value": float(row["Pr(>|z|)"]),
                "ci_low": float(row["Conf. Int. Low"]),
                "ci_high": float(row["Cont. Int. Hi."]),
            }
        )
    pd.DataFrame(rows).to_csv(MARGINAL_PATH, index=False)


def export_fit_stats(
    result: sm.discrete.discrete_model.MNLogitResults,
    n_individuals: int,
) -> None:
    """Record key fit statistics for the multinomial specification."""

    metrics = [
        {"metric": "n_individuals", "value": int(n_individuals)},
        {"metric": "log_likelihood", "value": float(result.llf)},
        {"metric": "aic", "value": float(result.aic)},
        {"metric": "bic", "value": float(result.bic)},
        {"metric": "pseudo_r2_mcfadden", "value": float(result.prsquared)},
        {"metric": "df_model", "value": int(result.df_model)},
    ]
    pd.DataFrame(metrics).to_csv(MULTI_FIT_PATH, index=False)


def build_comparison_table(multi_fit: pd.DataFrame) -> None:
    """Combine multinomial fit with the PPO metrics if available."""

    rows: list[dict[str, object]] = []

    def extract_metric(df: pd.DataFrame, name: str) -> float | None:
        match = df.loc[df["metric"] == name, "value"]
        return float(match.iloc[0]) if not match.empty else None

    multi_summary = {
        "model": "multinomial_logit",
        "log_likelihood": extract_metric(multi_fit, "log_likelihood"),
        "aic": extract_metric(multi_fit, "aic"),
        "bic": extract_metric(multi_fit, "bic"),
        "pseudo_r2": extract_metric(multi_fit, "pseudo_r2_mcfadden"),
        "n_effective_obs": extract_metric(multi_fit, "n_individuals"),
    }
    if multi_summary["log_likelihood"] is not None and multi_summary["n_effective_obs"]:
        per_obs = multi_summary["log_likelihood"] / multi_summary["n_effective_obs"]
        multi_summary["loglik_per_effective_obs"] = per_obs
        multi_summary["loglik_per_person"] = per_obs
    rows.append(multi_summary)

    if PPO_FIT_PATH.exists():
        ppo_fit = pd.read_csv(PPO_FIT_PATH)
        ppo_summary = {
            "model": "partial_proportional_odds",
            "log_likelihood": extract_metric(ppo_fit, "log_likelihood"),
            "aic": extract_metric(ppo_fit, "aic"),
            "bic": extract_metric(ppo_fit, "bic"),
            "pseudo_r2": extract_metric(ppo_fit, "pseudo_r2_mcfadden"),
            "n_effective_obs": extract_metric(ppo_fit, "n_long_rows"),
        }
        if ppo_summary["log_likelihood"] is not None and ppo_summary["n_effective_obs"]:
            ppo_summary["loglik_per_effective_obs"] = ppo_summary["log_likelihood"] / ppo_summary["n_effective_obs"]
        n_people = extract_metric(ppo_fit, "n_individuals")
        if ppo_summary["log_likelihood"] is not None and n_people:
            ppo_summary["loglik_per_person"] = ppo_summary["log_likelihood"] / n_people
        rows.append(ppo_summary)

    pd.DataFrame(rows).to_csv(COMPARISON_PATH, index=False)


def main() -> None:
    np.random.seed(20251016)
    df = pd.read_csv(DATA_PATH, low_memory=False)
    base_df = prepare_base_dataframe(df)

    result = fit_multinomial(base_df)
    export_params(result)
    export_marginals(result)
    export_fit_stats(result, n_individuals=len(base_df))

    multi_fit = pd.read_csv(MULTI_FIT_PATH)
    build_comparison_table(multi_fit)


if __name__ == "__main__":
    main()
