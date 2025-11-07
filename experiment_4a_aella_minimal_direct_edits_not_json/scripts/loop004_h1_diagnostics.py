#!/usr/bin/env python3
"""Loop 004 diagnostics for H1: sequential models + moderation scans."""

from __future__ import annotations

from pathlib import Path
from typing import Iterable, List, Sequence

import pandas as pd
import statsmodels.api as sm

from likert_utils import align_likert, ensure_columns, get_likert_specs, zscore

DATA_PATH = Path("childhoodbalancedpublic_original.csv")
TABLES_DIR = Path("tables")
TABLES_DIR.mkdir(parents=True, exist_ok=True)

COEFFICIENTS_PATH = TABLES_DIR / "loop004_h1_diagnostics.csv"
CORR_PATH = TABLES_DIR / "loop004_h1_correlations.csv"

CONTROL_COLUMNS: List[str] = [
    "classteen",
    "selfage",
    "gendermale",
    "education",
]


def add_aligned_columns(df: pd.DataFrame) -> pd.DataFrame:
    specs = get_likert_specs()
    ensure_columns(df, specs)
    aligned = align_likert(df, specs)
    for spec in specs:
        df[spec.aligned_column] = aligned[spec.aligned_column]
        df[spec.z_column] = zscore(aligned[spec.aligned_column])
    return df


def unique(seq: Sequence[str]) -> List[str]:
    """Return sequence order with duplicates removed."""

    seen: set[str] = set()
    result: List[str] = []
    for item in seq:
        if item not in seen:
            seen.add(item)
            result.append(item)
    return result


def fit_ols(df: pd.DataFrame, outcome: str, predictors: Sequence[str]) -> tuple[sm.regression.linear_model.RegressionResultsWrapper, int]:
    predictors = unique(list(predictors))
    data = df[[outcome, *predictors]].dropna()
    X = sm.add_constant(data[predictors], has_constant="add")
    model = sm.OLS(data[outcome], X).fit()
    return model, len(data)


def collect_terms(
    model_id: str,
    model_desc: str,
    model,
    n_obs: int,
    keep: Iterable[str],
) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for term in keep:
        if term not in model.params:
            continue
        beta = model.params[term]
        se = model.bse[term]
        rows.append(
            {
                "model_id": model_id,
                "model_desc": model_desc,
                "term": term,
                "estimate": beta,
                "std_err": se,
                "ci_low": beta - 1.96 * se,
                "ci_high": beta + 1.96 * se,
                "p_value": model.pvalues[term],
                "n_obs": n_obs,
            }
        )
    return rows


def main() -> None:
    df = pd.read_csv(DATA_PATH, low_memory=False)
    add_aligned_columns(df)

    df["abuse_child_guidance_int"] = df["abuse_child_z"] * df["guidance_child_z"]
    df["abuse_child_male_int"] = df["abuse_child_z"] * df["gendermale"]

    corr_vars = [
        "depression_z",
        "abuse_child_z",
        "abuse_teen_z",
        "guidance_child_z",
        "guidance_teen_z",
        "religion",
        "classteen",
        "gendermale",
    ]
    corr_df = df[corr_vars].dropna().corr()
    corr_df.to_csv(CORR_PATH)

    models_config = [
        {
            "model_id": "loop004_h1_bivariate",
            "desc": "Bivariate OLS (no covariates)",
            "predictors": ["abuse_child_z"],
            "keep": ["abuse_child_z"],
        },
        {
            "model_id": "loop004_h1_dual_abuse",
            "desc": "Add teen abuse to isolate childhood-specific effect",
            "predictors": ["abuse_child_z", "abuse_teen_z"],
            "keep": ["abuse_child_z", "abuse_teen_z"],
        },
        {
            "model_id": "loop004_h1_full_controls",
            "desc": "Add demographic controls",
            "predictors": ["abuse_child_z", "abuse_teen_z", *CONTROL_COLUMNS],
            "keep": ["abuse_child_z", "abuse_teen_z"],
        },
        {
            "model_id": "loop004_h1_guidance_interaction",
            "desc": "Add guidance main effect + abuse × guidance interaction",
            "predictors": [
                "abuse_child_z",
                "abuse_teen_z",
                "guidance_child_z",
                "abuse_child_guidance_int",
                *CONTROL_COLUMNS,
            ],
            "keep": ["abuse_child_z", "abuse_child_guidance_int", "guidance_child_z"],
        },
        {
            "model_id": "loop004_h1_gender_interaction",
            "desc": "Add abuse × male interaction",
            "predictors": [
                "abuse_child_z",
                "abuse_teen_z",
                "abuse_child_male_int",
                *CONTROL_COLUMNS,
                "gendermale",
            ],
            "keep": ["abuse_child_z", "abuse_child_male_int", "gendermale"],
        },
    ]

    rows: list[dict[str, object]] = []
    for cfg in models_config:
        model, n_obs = fit_ols(df, "depression_z", cfg["predictors"])
        rows.extend(collect_terms(cfg["model_id"], cfg["desc"], model, n_obs, cfg["keep"]))

    pd.DataFrame(rows).to_csv(COEFFICIENTS_PATH, index=False)


if __name__ == "__main__":
    main()
