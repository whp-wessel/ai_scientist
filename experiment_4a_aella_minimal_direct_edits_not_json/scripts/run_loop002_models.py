#!/usr/bin/env python3
"""Prototype OLS and logit models for Loop 002 and log reverse-code checks."""

from __future__ import annotations

from pathlib import Path
from typing import Iterable

import pandas as pd
import statsmodels.api as sm

DATA_PATH = Path("childhoodbalancedpublic_original.csv")
TABLES_DIR = Path("tables")
TABLES_DIR.mkdir(parents=True, exist_ok=True)

COLS = {
    "abuse_child": "during ages *0-12*: your parents verbally or emotionally abused you (mds78zu)",
    "abuse_teen": "during ages *13-18*: your parents verbally or emotionally abused you (v1k988q)",
    "guidance_child": "during ages *0-12*: Your parents gave useful guidance (pqo6jmj)",
    "guidance_teen": "during ages *13-18*: Your parents gave useful guidance (dcrx5ab)",
    "depression": "I tend to suffer from depression (wz901dj)",
    "selflove": "I love myself (2l8994l)",
    "networth": "Your CURRENT net worth is closest to (nhoz8ia)",
    "classchild": "classchild",
    "classteen": "classteen",
    "selfage": "selfage",
    "gendermale": "gendermale",
    "education": "education",
    "anxiety_neg": "I tend to suffer from anxiety (npvfh98)-neg",
}

VAR_IDS = {
    COLS["abuse_child"]: "mds78zu",
    COLS["abuse_teen"]: "v1k988q",
    COLS["guidance_child"]: "pqo6jmj",
    COLS["guidance_teen"]: "dcrx5ab",
    COLS["depression"]: "wz901dj",
    COLS["selflove"]: "2l8994l",
    COLS["networth"]: "nhoz8ia",
    COLS["classchild"]: "classchild",
    COLS["classteen"]: "classteen",
    COLS["selfage"]: "selfage",
    COLS["gendermale"]: "gendermale",
    COLS["education"]: "education",
    COLS["anxiety_neg"]: "npvfh98_neg",
}

TOP_NETWORTH_CATS = {
    "$1,000,000",
    "$10,000,000",
    "$100,000,000 or more",
}


def _ensure_columns(df: pd.DataFrame, columns: Iterable[str]) -> None:
    missing = [c for c in columns if c not in df.columns]
    if missing:
        raise KeyError(f"Missing expected columns: {missing}")


def run_ols(
    df: pd.DataFrame,
    outcome_col: str,
    predictor_cols: list[str],
) -> tuple[sm.regression.linear_model.RegressionResultsWrapper, int]:
    data = df[[outcome_col] + predictor_cols].dropna()
    y = data[outcome_col]
    X = sm.add_constant(data[predictor_cols], has_constant="add")
    model = sm.OLS(y, X).fit()
    return model, len(data)


def run_logit(
    df: pd.DataFrame,
    outcome_col: str,
    predictor_cols: list[str],
) -> tuple[sm.discrete.discrete_model.BinaryResultsWrapper, int]:
    data = df[[outcome_col] + predictor_cols].dropna()
    y = data[outcome_col]
    X = sm.add_constant(data[predictor_cols], has_constant="add")
    model = sm.Logit(y, X).fit(disp=False, maxiter=200)
    return model, len(data)


def main() -> None:
    df = pd.read_csv(DATA_PATH, low_memory=False)
    _ensure_columns(df, COLS.values())

    # Prepare derived fields.
    df["high_networth"] = df[COLS["networth"]].isin(TOP_NETWORTH_CATS).astype(int)

    model_specs = [
        {
            "model_id": "loop002_h1_ols",
            "model_type": "OLS",
            "outcome": COLS["depression"],
            "predictors": [
                COLS["abuse_child"],
                COLS["abuse_teen"],
                COLS["classteen"],
                COLS["selfage"],
                COLS["gendermale"],
                COLS["education"],
            ],
        },
        {
            "model_id": "loop002_h2_ols",
            "model_type": "OLS",
            "outcome": COLS["selflove"],
            "predictors": [
                COLS["guidance_child"],
                COLS["guidance_teen"],
                COLS["classteen"],
                COLS["selfage"],
                COLS["gendermale"],
                COLS["education"],
            ],
        },
        {
            "model_id": "loop002_h3_logit",
            "model_type": "LOGIT",
            "outcome": "high_networth",
            "predictors": [
                COLS["classchild"],
                COLS["classteen"],
                COLS["selfage"],
                COLS["gendermale"],
                COLS["education"],
            ],
        },
    ]

    est_rows: list[dict[str, object]] = []
    for spec in model_specs:
        predictors = spec["predictors"]
        if spec["model_type"] == "OLS":
            model, n_obs = run_ols(df, spec["outcome"], predictors)
            stat_type = "t"
        else:
            model, n_obs = run_logit(df, spec["outcome"], predictors)
            stat_type = "z"
        for term in ["const"] + predictors:
            if term == "const":
                continue
            coef = model.params[term]
            se = model.bse[term]
            stat_value = model.tvalues[term]
            est_rows.append(
                {
                    "model_id": spec["model_id"],
                    "model_type": spec["model_type"],
                    "outcome": spec["outcome"],
                    "term": term,
                    "term_id": VAR_IDS.get(term, term),
                    "estimate": coef,
                    "std_err": se,
                    "stat": stat_value,
                    "stat_type": stat_type,
                    "p_value": model.pvalues[term],
                    "ci_low": coef - 1.96 * se,
                    "ci_high": coef + 1.96 * se,
                    "n_obs": n_obs,
                }
            )

    est_df = pd.DataFrame(est_rows)
    est_df.to_csv(TABLES_DIR / "loop002_model_estimates.csv", index=False)

    # Reverse-code check: anxiety (-neg) vs depression correlation.
    reverse_df = df[[COLS["anxiety_neg"], COLS["depression"]]].dropna()
    corr = reverse_df.corr().iloc[0, 1]
    reverse_rows = [
        {
            "item_id": VAR_IDS[COLS["anxiety_neg"]],
            "check": "pearson_corr_with_depression",
            "value": corr,
            "n_obs": len(reverse_df),
            "interpretation": "Positive correlation implies higher values reflect worse anxiety; no additional flip needed.",
        }
    ]
    pd.DataFrame(reverse_rows).to_csv(TABLES_DIR / "loop002_reverse_code_check.csv", index=False)


if __name__ == "__main__":
    main()
