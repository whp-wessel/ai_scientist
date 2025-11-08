#!/usr/bin/env python3
"""Loop 012: Alternate anxiety outcomes for H4 (ordinal collapse + high-flag)."""

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

DIST_PATH = TABLES_DIR / "loop012_h4_alt_outcome_distribution.csv"
MODELS_PATH = TABLES_DIR / "loop012_h4_alt_models.csv"

ANXIETY_PRIMARY = "I tend to suffer from anxiety (npvfh98)-neg"
ANXIETY_SECONDARY = "I tend to suffer from anxiety -neg"

PREDICTORS = [
    "religion",
    "classchild",
    "classteen",
    "selfage",
    "gendermale",
    "education",
]


def add_aligned_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Attach aligned/z-scored Likert variables used throughout."""

    specs = get_likert_specs()
    ensure_columns(df, specs)
    aligned = align_likert(df, specs)
    for spec in specs:
        df[spec.aligned_column] = aligned[spec.aligned_column]
        df[spec.z_column] = zscore(aligned[spec.aligned_column])
    return df


def collapse_to_three_bins(series: pd.Series) -> pd.Series:
    """Map the 7-point aligned anxiety scale into 3 ordered categories."""

    shifted = (series + 3).round()
    collapsed = pd.Series(pd.NA, index=series.index, dtype="Int64")
    collapsed[(shifted >= 0) & (shifted <= 2)] = 0  # rare
    collapsed[(shifted >= 3) & (shifted <= 4)] = 1  # sometimes
    collapsed[(shifted >= 5) & (shifted <= 6)] = 2  # frequent
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
                "model_desc": model_desc,
                "model_type": model_type,
                "term": term,
                "estimate": beta,
                "std_err": se,
                "p_value": float(pvalues[term]),
                "ci_low": float(ci_low),
                "ci_high": float(ci_high),
                "n_obs": n_obs,
            }
        )
    return rows


def fit_ordered_logit(df: pd.DataFrame) -> list[dict[str, object]]:
    """Fit the 3-bin ordinal outcome using an ordered logit."""

    data = df[["anxiety_ord3", *PREDICTORS]].dropna()
    if data.empty:
        return []
    y = data["anxiety_ord3"].astype(int)
    X = data[PREDICTORS].astype(float)
    model = OrderedModel(y, X, distr="logit")
    result = model.fit(method="bfgs", disp=False, maxiter=500)
    threshold_terms = [idx for idx in result.params.index if idx.startswith("threshold") or "/" in idx]
    keep_terms = [idx for idx in result.params.index if idx not in threshold_terms]
    params = result.params[keep_terms]
    conf = result.conf_int().loc[keep_terms]
    return collect_terms(
        model_id="ordered_logit_anxiety3",
        model_desc="Ordered logit (3-bin anxiety) ~ religiosity + controls",
        model_type="ORDERED_LOGIT",
        params=params,
        bse=result.bse[params.index],
        pvalues=result.pvalues[params.index],
        conf_int=conf,
        terms=params.index,
        n_obs=int(result.nobs),
    )


def fit_logit(df: pd.DataFrame) -> list[dict[str, object]]:
    """Fit a binary logit for the high-anxiety flag."""

    data = df[["anxiety_high_flag", *PREDICTORS]].dropna()
    if data.empty:
        return []
    y = data["anxiety_high_flag"].astype(int)
    X = sm.add_constant(data[PREDICTORS].astype(float), has_constant="add")
    model = sm.Logit(y, X).fit(disp=False, maxiter=200)
    terms = [col for col in X.columns if col != "const"]
    return collect_terms(
        model_id="logit_high_anxiety",
        model_desc="Binary logit (high anxiety) ~ religiosity + controls",
        model_type="LOGIT",
        params=model.params,
        bse=model.bse,
        pvalues=model.pvalues,
        conf_int=model.conf_int(),
        terms=terms,
        n_obs=int(model.nobs),
    )


def fit_lpm(df: pd.DataFrame) -> list[dict[str, object]]:
    """Fit a linear probability model for the high-anxiety flag."""

    data = df[["anxiety_high_flag", *PREDICTORS]].dropna()
    if data.empty:
        return []
    y = data["anxiety_high_flag"].astype(float)
    X = sm.add_constant(data[PREDICTORS].astype(float), has_constant="add")
    model = sm.OLS(y, X).fit()
    terms = [col for col in X.columns if col != "const"]
    return collect_terms(
        model_id="lpm_high_anxiety",
        model_desc="Linear probability model (high anxiety) ~ religiosity + controls",
        model_type="OLS",
        params=model.params,
        bse=model.bse,
        pvalues=model.pvalues,
        conf_int=model.conf_int(),
        terms=terms,
        n_obs=int(model.nobs),
    )


def write_distribution_table(df: pd.DataFrame) -> None:
    """Summarize the new outcome codings for transparency."""

    rows: list[dict[str, object]] = []
    ord_series = df["anxiety_ord3"]
    ord_counts = ord_series.value_counts(dropna=False).sort_index()
    labels = {0: "rare (0-2)", 1: "sometimes (3-4)", 2: "frequent (5-6)"}
    total_ord = ord_series.notna().sum()
    for level, count in ord_counts.items():
        label = labels.get(level, "missing")
        rows.append(
            {
                "outcome": "anxiety_ord3",
                "level": level if pd.notna(level) else "NA",
                "label": label,
                "n": int(count),
                "share": float(count / total_ord) if pd.notna(level) and total_ord else float("nan"),
            }
        )

    bin_series = df["anxiety_high_flag"]
    bin_counts = bin_series.value_counts(dropna=False).sort_index()
    total_bin = bin_series.notna().sum()
    for level, count in bin_counts.items():
        label = "missing" if pd.isna(level) else ("high anxiety" if level == 1 else "not high anxiety")
        rows.append(
            {
                "outcome": "anxiety_high_flag",
                "level": level if pd.notna(level) else "NA",
                "label": label,
                "n": int(count),
                "share": float(count / total_bin) if pd.notna(level) and total_bin else float("nan"),
            }
        )

    pd.DataFrame(rows).to_csv(DIST_PATH, index=False)


def main() -> None:
    df = pd.read_csv(DATA_PATH, low_memory=False)
    add_aligned_columns(df)

    df["anxiety_ord3"] = collapse_to_three_bins(df["anxiety_aligned"])
    df["anxiety_high_flag"] = derive_high_flag(df)

    write_distribution_table(df)

    model_rows: list[dict[str, object]] = []
    model_rows.extend(fit_ordered_logit(df))
    model_rows.extend(fit_logit(df))
    model_rows.extend(fit_lpm(df))
    pd.DataFrame(model_rows).to_csv(MODELS_PATH, index=False)


if __name__ == "__main__":
    main()
