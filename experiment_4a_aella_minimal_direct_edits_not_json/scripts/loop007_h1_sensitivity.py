#!/usr/bin/env python3
"""Loop 007 sensitivity analyses for the H1 confirmatory family.

Outputs:
- tables/loop007_h1_sensitivity.csv — interaction coefficients under HC3 SEs
  and an expanded covariate set to assess robustness of the preregistered
  contrasts.
"""

from __future__ import annotations

from pathlib import Path
from typing import Dict, Iterable, List, Sequence

import numpy as np
import pandas as pd
import statsmodels.api as sm

from likert_utils import align_likert, ensure_columns, get_likert_specs, zscore

DATA_PATH = Path("childhoodbalancedpublic_original.csv")
TABLES_DIR = Path("tables")
TABLES_DIR.mkdir(parents=True, exist_ok=True)

OUTPUT_PATH = TABLES_DIR / "loop007_h1_sensitivity.csv"

BASE_CONTROLS: List[str] = [
    "classteen",
    "selfage",
    "gendermale",
    "education",
]

EXPANDED_CONTROLS: List[str] = [
    *BASE_CONTROLS,
    "classchild",
    "classcurrent",
    "religion",
    "externalreligion",
    "guidance_teen_z",
]


def add_aligned_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Attach aligned/z-scored Likert variables used across H1 models."""

    specs = get_likert_specs()
    ensure_columns(df, specs)
    aligned = align_likert(df, specs)
    for spec in specs:
        df[spec.aligned_column] = aligned[spec.aligned_column]
        df[spec.z_column] = zscore(aligned[spec.aligned_column])
    return df


def unique(seq: Sequence[str]) -> List[str]:
    seen: set[str] = set()
    ordered: List[str] = []
    for item in seq:
        if item not in seen:
            seen.add(item)
            ordered.append(item)
    return ordered


def fit_ols(
    df: pd.DataFrame,
    outcome: str,
    predictors: Sequence[str],
    cov_type: str | None = None,
) -> tuple[sm.regression.linear_model.RegressionResultsWrapper, int]:
    """Fit an OLS model and optionally return HCx-robust results."""

    predictors = unique(list(predictors))
    frame = df[[outcome, *predictors]].dropna()
    X = sm.add_constant(frame[predictors], has_constant="add")
    model = sm.OLS(frame[outcome], X).fit()
    if cov_type is not None:
        model = model.get_robustcov_results(cov_type=cov_type)
    return model, len(frame)


def collect_term(
    model_id: str,
    model_desc: str,
    sensitivity_id: str,
    sensitivity_desc: str,
    model,
    n_obs: int,
    term: str,
    cov_type: str | None,
    control_set: str,
) -> dict[str, object]:
    index = model.model.exog_names
    params = pd.Series(model.params, index=index)
    ses = pd.Series(model.bse, index=index)
    pvalues = pd.Series(model.pvalues, index=index)
    beta = params[term]
    se = ses[term]
    return {
        "sensitivity_id": sensitivity_id,
        "sensitivity_desc": sensitivity_desc,
        "model_id": model_id,
        "model_desc": model_desc,
        "term": term,
        "estimate": beta,
        "std_err": se,
        "ci_low": beta - 1.96 * se,
        "ci_high": beta + 1.96 * se,
        "p_value": pvalues[term],
        "cov_type": cov_type or "OLS",
        "control_set": control_set,
        "n_obs": n_obs,
    }


def bh_adjust(series: pd.Series) -> pd.Series:
    """Apply Benjamini–Hochberg (non-decreasing, m tests)."""

    values = series.to_numpy(dtype=float)
    order = np.argsort(values)
    m = len(values)
    q = np.empty_like(values)
    running = 1.0
    for idx in range(m - 1, -1, -1):
        rank = idx + 1
        adj = values[order[idx]] * m / rank
        running = min(running, adj)
        q[order[idx]] = running
    return pd.Series(q, index=series.index)


def main() -> None:
    df = pd.read_csv(DATA_PATH, low_memory=False)
    add_aligned_columns(df)

    df["abuse_child_guidance_int"] = df["abuse_child_z"] * df["guidance_child_z"]
    df["abuse_child_male_int"] = df["abuse_child_z"] * df["gendermale"]

    sensitivity_specs = [
        {
            "sensitivity_id": "hc3",
            "sensitivity_desc": "HC3 robust SEs with preregistered controls",
            "cov_type": "HC3",
            "control_set": "base",
        },
        {
            "sensitivity_id": "expanded_controls",
            "sensitivity_desc": "Adds childhood/current class, religion, teen guidance controls",
            "cov_type": None,
            "control_set": "expanded",
        },
    ]

    control_map: Dict[str, List[str]] = {
        "base": BASE_CONTROLS,
        "expanded": EXPANDED_CONTROLS,
    }

    model_templates = [
        {
            "model_id": "h1_guidance_interaction",
            "model_desc": "Guidance buffering contrast",
            "term": "abuse_child_guidance_int",
            "predictors": [
                "abuse_child_z",
                "abuse_teen_z",
                "guidance_child_z",
                "abuse_child_guidance_int",
            ],
        },
        {
            "model_id": "h1_gender_interaction",
            "model_desc": "Male vulnerability contrast",
            "term": "abuse_child_male_int",
            "predictors": [
                "abuse_child_z",
                "abuse_teen_z",
                "abuse_child_male_int",
                "gendermale",
            ],
        },
    ]

    rows: list[dict[str, object]] = []
    for spec in sensitivity_specs:
        controls = control_map[spec["control_set"]]
        cov_type = spec["cov_type"]
        for template in model_templates:
            predictors = [
                *template["predictors"],
                *controls,
            ]
            model, n_obs = fit_ols(
                df,
                outcome="depression_z",
                predictors=predictors,
                cov_type=cov_type,
            )
            rows.append(
                collect_term(
                    model_id=template["model_id"],
                    model_desc=template["model_desc"],
                    sensitivity_id=spec["sensitivity_id"],
                    sensitivity_desc=spec["sensitivity_desc"],
                    model=model,
                    n_obs=n_obs,
                    term=template["term"],
                    cov_type=cov_type,
                    control_set=spec["control_set"],
                )
            )

    result_df = pd.DataFrame(rows)
    for sensitivity_id, subset in result_df.groupby("sensitivity_id"):
        result_df.loc[subset.index, "q_value"] = bh_adjust(subset["p_value"])

    result_df.to_csv(OUTPUT_PATH, index=False)


if __name__ == "__main__":
    main()
