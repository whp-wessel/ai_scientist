#!/usr/bin/env python3
"""Loop 014: Religiosity × class/gender interactions for H4 alternate outcomes."""

from __future__ import annotations

from pathlib import Path
from typing import Iterable, List

import numpy as np
import pandas as pd
import statsmodels.api as sm
from statsmodels.miscmodels.ordinal_model import OrderedModel

from likert_utils import align_likert, ensure_columns, get_likert_specs, zscore

DATA_PATH = Path("childhoodbalancedpublic_original.csv")
TABLES_DIR = Path("tables")
TABLES_DIR.mkdir(parents=True, exist_ok=True)

OUTPUT_PATH = TABLES_DIR / "loop014_h4_interactions.csv"

ANXIETY_PRIMARY = "I tend to suffer from anxiety (npvfh98)-neg"
ANXIETY_SECONDARY = "I tend to suffer from anxiety -neg"

BASE_CONTROLS = [
    "classchild",
    "classteen",
    "selfage",
    "gendermale",
    "education",
]


def add_aligned_columns(df: pd.DataFrame) -> None:
    """Attach aligned and z-scored Likert variables used downstream."""

    specs = get_likert_specs()
    ensure_columns(df, specs)
    aligned = align_likert(df, specs)
    for spec in specs:
        df[spec.aligned_column] = aligned[spec.aligned_column]
        df[spec.z_column] = zscore(aligned[spec.aligned_column])


def collapse_to_three_bins(series: pd.Series) -> pd.Series:
    """Map the 7-point aligned anxiety scale into 3 ordered categories."""

    shifted = (series + 3).round()
    collapsed = pd.Series(pd.NA, index=series.index, dtype="Int64")
    collapsed[(shifted >= 0) & (shifted <= 2)] = 0
    collapsed[(shifted >= 3) & (shifted <= 4)] = 1
    collapsed[(shifted >= 5) & (shifted <= 6)] = 2
    return collapsed


def derive_high_flag(df: pd.DataFrame) -> pd.Series:
    """Create a binary high-anxiety flag based on either survey item."""

    aligned_candidates: List[pd.Series] = []
    for col in (ANXIETY_PRIMARY, ANXIETY_SECONDARY):
        if col in df.columns:
            aligned_candidates.append(-df[col])
    if not aligned_candidates:
        aligned_candidates.append(df["anxiety_aligned"])
    stack = pd.concat(aligned_candidates, axis=1)
    valid = stack.notna().any(axis=1)
    max_aligned = stack.max(axis=1)
    flag = pd.Series(pd.NA, index=df.index, dtype="Int64")
    flag[valid] = (max_aligned[valid] >= 2).astype("Int64")
    return flag


def collect_terms(
    model_id: str,
    model_desc: str,
    model_type: str,
    params: pd.Series,
    bse: pd.Series,
    pvalues: pd.Series,
    conf_int: pd.DataFrame,
    terms: Iterable[str],
    n_obs: int,
) -> list[dict[str, object]]:
    """Return tidy coefficient rows for the requested terms."""

    rows: list[dict[str, object]] = []
    for term in terms:
        if term not in params:
            continue
        beta = float(params[term])
        se = float(bse[term])
        ci_low, ci_high = conf_int.loc[term]
        rows.append(
            {
                "model_id": model_id,
                "model_type": model_type,
                "model_desc": model_desc,
                "term": term,
                "estimate": beta,
                "std_err": se,
                "ci_low": float(ci_low),
                "ci_high": float(ci_high),
                "p_value": float(pvalues[term]),
                "n_obs": int(n_obs),
            }
        )
    return rows


def fit_ordered_model(df: pd.DataFrame) -> list[dict[str, object]]:
    """Fit the religiosity × class/gender model for the 3-bin ordinal anxiety outcome."""

    predictors = [
        "religion",
        *BASE_CONTROLS,
        "religion_classchild_int",
        "religion_gendermale_int",
    ]
    data = df[["anxiety_ord3", *predictors]].dropna()
    if data.empty:
        return []
    y = data["anxiety_ord3"].astype(int)
    X = data[predictors].astype(float)
    model = OrderedModel(y, X, distr="logit")
    result = model.fit(method="bfgs", disp=False, maxiter=500)
    threshold_terms = [idx for idx in result.params.index if idx.startswith("threshold") or "/" in idx]
    keep = [idx for idx in result.params.index if idx not in threshold_terms]
    params = result.params[keep]
    conf = result.conf_int().loc[keep]
    return collect_terms(
        model_id="loop014_h4_ord3_interactions",
        model_desc="Ordered logit: anxiety_ord3 ~ religion × (classchild, gender) + controls",
        model_type="ORDERED_LOGIT",
        params=params,
        bse=result.bse[keep],
        pvalues=result.pvalues[keep],
        conf_int=conf,
        terms=["religion", "religion_classchild_int", "religion_gendermale_int"],
        n_obs=result.nobs,
    )


def fit_logit_model(df: pd.DataFrame) -> list[dict[str, object]]:
    """Fit the religiosity × class/gender model for the ≥5 high-anxiety binary outcome."""

    predictors = [
        "religion",
        *BASE_CONTROLS,
        "religion_classchild_int",
        "religion_gendermale_int",
    ]
    data = df[["anxiety_high_flag", *predictors]].dropna()
    if data.empty:
        return []
    y = data["anxiety_high_flag"].astype(int)
    X = sm.add_constant(data[predictors].astype(float), has_constant="add")
    result = sm.Logit(y, X).fit(disp=False, maxiter=200)
    terms = ["religion", "religion_classchild_int", "religion_gendermale_int"]
    conf = result.conf_int().loc[["const", *terms]].drop(index="const", errors="ignore")
    return collect_terms(
        model_id="loop014_h4_highflag_interactions",
        model_desc="Logit: anxiety_high_flag ~ religion × (classchild, gender) + controls",
        model_type="LOGIT",
        params=result.params,
        bse=result.bse,
        pvalues=result.pvalues,
        conf_int=result.conf_int(),
        terms=terms,
        n_obs=result.nobs,
    )


def main() -> None:
    df = pd.read_csv(DATA_PATH, low_memory=False)
    add_aligned_columns(df)

    df["anxiety_ord3"] = collapse_to_three_bins(df["anxiety_aligned"])
    df["anxiety_high_flag"] = derive_high_flag(df)
    df["religion"] = df["religion"].astype(float)
    df["religion_classchild_int"] = df["religion"] * df["classchild"]
    df["religion_gendermale_int"] = df["religion"] * df["gendermale"]

    rows: list[dict[str, object]] = []
    rows.extend(fit_ordered_model(df))
    rows.extend(fit_logit_model(df))
    pd.DataFrame(rows).to_csv(OUTPUT_PATH, index=False)


if __name__ == "__main__":
    main()
