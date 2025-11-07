#!/usr/bin/env python3
"""Compute simple slopes for the H1 moderation candidates."""

from __future__ import annotations

from pathlib import Path
from typing import Iterable, List

import numpy as np
import pandas as pd
import statsmodels.api as sm

from likert_utils import align_likert, ensure_columns, get_likert_specs, zscore

DATA_PATH = Path("childhoodbalancedpublic_original.csv")
TABLES_DIR = Path("tables")
TABLES_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_PATH = TABLES_DIR / "loop005_h1_simple_slopes.csv"

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


def fit_ols(df: pd.DataFrame, outcome: str, predictors: Iterable[str]):
    cols = [outcome, *predictors]
    data = df[cols].dropna()
    X = sm.add_constant(data[predictors], has_constant="add")
    model = sm.OLS(data[outcome], X).fit()
    return model, list(X.columns), len(data)


def simple_slope_row(
    model,
    exog_names: List[str],
    main_term: str,
    interaction_term: str | None,
    moderator_label: str,
    moderator_value: float,
    context: str,
    n_obs: int,
) -> dict[str, object]:
    index_map = {name: i for i, name in enumerate(exog_names)}
    L = np.zeros((1, len(exog_names)))
    L[0, index_map[main_term]] = 1.0
    if interaction_term is not None:
        L[0, index_map[interaction_term]] = moderator_value
    test = model.t_test(L)
    effect = float(np.atleast_1d(test.effect).squeeze())
    se = float(np.atleast_1d(test.sd).squeeze())
    t_value = float(np.atleast_1d(test.tvalue).squeeze())
    p_value = float(np.atleast_1d(test.pvalue).squeeze())
    ci = np.atleast_2d(test.conf_int(alpha=0.05)).squeeze()
    ci_low = float(ci[0])
    ci_high = float(ci[1])
    return {
        "context": context,
        "moderator": moderator_label,
        "moderator_value": moderator_value,
        "slope": effect,
        "std_err": se,
        "t_value": t_value,
        "p_value": p_value,
        "ci_low": ci_low,
        "ci_high": ci_high,
        "n_obs": n_obs,
    }


def main() -> None:
    df = pd.read_csv(DATA_PATH, low_memory=False)
    add_aligned_columns(df)

    df["abuse_child_guidance_int"] = df["abuse_child_z"] * df["guidance_child_z"]
    df["abuse_child_male_int"] = df["abuse_child_z"] * df["gendermale"]

    rows: list[dict[str, object]] = []

    guidance_predictors = [
        "abuse_child_z",
        "abuse_teen_z",
        "guidance_child_z",
        "abuse_child_guidance_int",
        *CONTROL_COLUMNS,
    ]
    guidance_model, guidance_exog, guidance_n = fit_ols(df, "depression_z", guidance_predictors)

    for value, label in [(-1.0, "-1 SD"), (0.0, "mean"), (1.0, "+1 SD")]:
        rows.append(
            simple_slope_row(
                guidance_model,
                guidance_exog,
                "abuse_child_z",
                "abuse_child_guidance_int",
                moderator_label="guidance_child_z",
                moderator_value=value,
                context=f"Abuse slope at childhood guidance {label}",
                n_obs=guidance_n,
            )
        )

    gender_predictors = [
        "abuse_child_z",
        "abuse_teen_z",
        "abuse_child_male_int",
        *CONTROL_COLUMNS,
    ]
    gender_model, gender_exog, gender_n = fit_ols(df, "depression_z", gender_predictors)

    for value, label in [(0.0, "female (0)"), (1.0, "male (1)")]:
        rows.append(
            simple_slope_row(
                gender_model,
                gender_exog,
                "abuse_child_z",
                "abuse_child_male_int",
                moderator_label="gendermale",
                moderator_value=value,
                context=f"Abuse slope for {label}",
                n_obs=gender_n,
            )
        )

    pd.DataFrame(rows).to_csv(OUTPUT_PATH, index=False)


if __name__ == "__main__":
    main()
