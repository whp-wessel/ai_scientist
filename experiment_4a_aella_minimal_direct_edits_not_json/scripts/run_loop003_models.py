#!/usr/bin/env python3
"""Loop 003 modeling pipeline: aligned Likerts + ordered logit + anxiety models."""

from __future__ import annotations

from pathlib import Path
from typing import Callable, Iterable, List

import numpy as np
import pandas as pd
import statsmodels.api as sm
from statsmodels.discrete.discrete_model import BinaryResultsWrapper
from statsmodels.miscmodels.ordinal_model import OrderedModel
from statsmodels.regression.linear_model import RegressionResultsWrapper

from likert_utils import align_likert, ensure_columns, get_likert_specs, zscore

DATA_PATH = Path("childhoodbalancedpublic_original.csv")
TABLES_DIR = Path("tables")
TABLES_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_PATH = TABLES_DIR / "loop003_model_estimates.csv"

CONTROL_COLUMNS = [
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


def run_ols(df: pd.DataFrame, outcome: str, predictors: List[str]) -> tuple[RegressionResultsWrapper, int]:
    data = df[[outcome] + predictors].dropna()
    y = data[outcome]
    X = sm.add_constant(data[predictors], has_constant="add")
    model = sm.OLS(y, X).fit()
    return model, len(data)


def run_logit(df: pd.DataFrame, outcome: str, predictors: List[str]) -> tuple[BinaryResultsWrapper, int]:
    data = df[[outcome] + predictors].dropna()
    y = data[outcome]
    X = sm.add_constant(data[predictors], has_constant="add")
    model = sm.Logit(y, X).fit(disp=False, maxiter=200)
    return model, len(data)


def run_ordered_logit(df: pd.DataFrame, outcome: str, predictors: List[str]) -> tuple[OrderedModel, int, object]:
    data = df[[outcome] + predictors].dropna()
    y = data[outcome].astype(int)
    X = data[predictors]
    model = OrderedModel(y, X, distr="logit")
    res = model.fit(method="bfgs", maxiter=200, disp=False)
    return res, len(data), model


def collect_rows(
    model_id: str,
    model_type: str,
    outcome: str,
    predictors: Iterable[str],
    params: pd.Series,
    bse: pd.Series,
    stat_values: pd.Series,
    pvalues: pd.Series,
    n_obs: int,
    extra_filter: Callable[[str], bool] | None = None,
) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for term in params.index:
        if term == "const":
            continue
        if extra_filter and not extra_filter(term):
            continue
        rows.append(
            {
                "model_id": model_id,
                "model_type": model_type,
                "outcome": outcome,
                "term": term,
                "estimate": params[term],
                "std_err": bse[term],
                "stat": stat_values[term],
                "p_value": pvalues[term],
                "ci_low": params[term] - 1.96 * bse[term],
                "ci_high": params[term] + 1.96 * bse[term],
                "n_obs": n_obs,
            }
        )
    return rows


def main() -> None:
    df = pd.read_csv(DATA_PATH, low_memory=False)
    add_aligned_columns(df)

    df["networth_ord"] = df["networth"]
    df["high_networth"] = df["networth_ord"] >= 4
    df["high_networth"] = df["high_networth"].astype(int)
    df["high_anxiety"] = (df["anxiety_aligned"] >= 2).astype(int)

    model_rows: list[dict[str, object]] = []

    # H1 OLS
    h1_predictors = [
        "abuse_child_z",
        "abuse_teen_z",
        *CONTROL_COLUMNS,
    ]
    h1_model, h1_n = run_ols(df, "depression_z", h1_predictors)
    model_rows.extend(
        collect_rows(
            model_id="loop003_h1_ols",
            model_type="OLS",
            outcome="depression_z",
            predictors=h1_predictors,
            params=h1_model.params,
            bse=h1_model.bse,
            stat_values=h1_model.tvalues,
            pvalues=h1_model.pvalues,
            n_obs=h1_n,
        )
    )

    # H2 OLS
    h2_predictors = [
        "guidance_child_z",
        "guidance_teen_z",
        *CONTROL_COLUMNS,
    ]
    h2_model, h2_n = run_ols(df, "selflove_z", h2_predictors)
    model_rows.extend(
        collect_rows(
            model_id="loop003_h2_ols",
            model_type="OLS",
            outcome="selflove_z",
            predictors=h2_predictors,
            params=h2_model.params,
            bse=h2_model.bse,
            stat_values=h2_model.tvalues,
            pvalues=h2_model.pvalues,
            n_obs=h2_n,
        )
    )

    # H3 Ordered logit for full net worth brackets
    h3_predictors = [
        "classchild",
        "classteen",
        "selfage",
        "gendermale",
        "education",
    ]
    h3_res, h3_n, _ = run_ordered_logit(df, "networth_ord", h3_predictors)
    model_rows.extend(
        collect_rows(
            model_id="loop003_h3_ordered_logit",
            model_type="ORDERED_LOGIT",
            outcome="networth_ord",
            predictors=h3_predictors,
            params=h3_res.params,
            bse=h3_res.bse,
            stat_values=h3_res.tvalues,
            pvalues=h3_res.pvalues,
            n_obs=h3_n,
            extra_filter=lambda term: "/" not in term,
        )
    )

    # H3 binary logit for >= $1M net worth
    h3_logit_predictors = h3_predictors
    h3_logit_model, h3_logit_n = run_logit(df, "high_networth", h3_logit_predictors)
    model_rows.extend(
        collect_rows(
            model_id="loop003_h3_binary_logit",
            model_type="LOGIT",
            outcome="high_networth",
            predictors=h3_logit_predictors,
            params=h3_logit_model.params,
            bse=h3_logit_model.bse,
            stat_values=h3_logit_model.tvalues,
            pvalues=h3_logit_model.pvalues,
            n_obs=h3_logit_n,
        )
    )

    # H4 OLS for anxiety z-score
    h4_predictors = [
        "religion",
        "classchild",
        *CONTROL_COLUMNS,
    ]
    h4_model, h4_n = run_ols(df, "anxiety_z", h4_predictors)
    model_rows.extend(
        collect_rows(
            model_id="loop003_h4_ols",
            model_type="OLS",
            outcome="anxiety_z",
            predictors=h4_predictors,
            params=h4_model.params,
            bse=h4_model.bse,
            stat_values=h4_model.tvalues,
            pvalues=h4_model.pvalues,
            n_obs=h4_n,
        )
    )

    # H4 logistic for high anxiety indicator
    h4_logit_predictors = h4_predictors
    h4_logit_model, h4_logit_n = run_logit(df, "high_anxiety", h4_logit_predictors)
    model_rows.extend(
        collect_rows(
            model_id="loop003_h4_logit",
            model_type="LOGIT",
            outcome="high_anxiety",
            predictors=h4_logit_predictors,
            params=h4_logit_model.params,
            bse=h4_logit_model.bse,
            stat_values=h4_logit_model.tvalues,
            pvalues=h4_logit_model.pvalues,
            n_obs=h4_logit_n,
        )
    )

    pd.DataFrame(model_rows).to_csv(OUTPUT_PATH, index=False)


if __name__ == "__main__":
    main()
