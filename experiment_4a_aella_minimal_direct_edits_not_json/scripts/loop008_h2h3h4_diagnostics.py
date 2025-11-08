#!/usr/bin/env python3
"""Loop 008 diagnostics for H2–H4 (measurement, proportional odds, religiosity)."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List

import numpy as np
import pandas as pd
import statsmodels.api as sm
from scipy.stats import chi2

from likert_utils import align_likert, ensure_columns, get_likert_specs, zscore

DATA_PATH = Path("childhoodbalancedpublic_original.csv")
TABLES_DIR = Path("tables")
TABLES_DIR.mkdir(parents=True, exist_ok=True)

H2_DISTRIBUTION_PATH = TABLES_DIR / "loop008_h2_distribution.csv"
H2_MEASUREMENT_PATH = TABLES_DIR / "loop008_h2_measurement.csv"
H3_THRESHOLD_PATH = TABLES_DIR / "loop008_h3_po_thresholds.csv"
H3_SUMMARY_PATH = TABLES_DIR / "loop008_h3_po_summary.csv"
H4_MODELS_PATH = TABLES_DIR / "loop008_h4_religiosity_models.csv"
H4_TESTS_PATH = TABLES_DIR / "loop008_h4_religiosity_tests.csv"

H3_PREDICTORS = [
    "classchild",
    "classteen",
    "selfage",
    "gendermale",
    "education",
    "classchild_male_int",
]

H4_CONTROLS = [
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


def cronbach_alpha(values: np.ndarray) -> float:
    """Compute Cronbach's alpha for a 2+ item matrix."""

    k = values.shape[1]
    if k < 2:
        return float("nan")
    item_var = values.var(axis=0, ddof=1)
    total_var = values.sum(axis=1).var(ddof=1)
    if total_var == 0:
        return float("nan")
    return float((k / (k - 1.0)) * (1 - item_var.sum() / total_var))


def describe_h2_measurement(df: pd.DataFrame) -> None:
    """Summarize self-love measurement diagnostics (H2)."""

    df = df.copy()
    df["selfwar_inverted"] = -df["selfwar_z"]

    variables = ["selflove_z", "selfwar_z", "depression_z", "anxiety_z"]
    rows: list[dict[str, object]] = []
    for var in variables:
        series = df[var].dropna()
        rows.append(
            {
                "variable": var,
                "n_obs": int(series.shape[0]),
                "mean": float(series.mean()),
                "std": float(series.std(ddof=0)),
                "skew": float(series.skew()),
                "kurtosis": float(series.kurtosis()),
                "min": float(series.min()),
                "max": float(series.max()),
            }
        )
    pd.DataFrame(rows).to_csv(H2_DISTRIBUTION_PATH, index=False)

    metrics: list[dict[str, object]] = []
    duo = df[["selflove_z", "selfwar_z"]].dropna().copy()
    duo["selfwar_inverted"] = -duo["selfwar_z"]
    alpha = cronbach_alpha(duo[["selflove_z", "selfwar_inverted"]].to_numpy())
    metrics.append(
        {
            "metric": "cronbach_alpha_selflove_duo",
            "value": alpha,
            "n_obs": int(len(duo)),
            "interpretation": "Two-item scale (self-love + inverted self-war).",
        }
    )

    def corr_metric(x: str, y: str, label: str, note: str) -> None:
        subset = df[[x, y]].dropna()
        if subset.empty:
            value = float("nan")
            n_obs = 0
        else:
            value = float(subset[x].corr(subset[y]))
            n_obs = int(len(subset))
        metrics.append(
            {
                "metric": label,
                "value": value,
                "n_obs": n_obs,
                "interpretation": note,
            }
        )

    corr_metric("selflove_z", "selfwar_inverted", "pearson_selflove_vs_inverse_war", "Internal consistency check (expect >0).")
    corr_metric("selflove_z", "depression_z", "pearson_selflove_vs_depression", "Association between self-love and depression (expect negative if constructs diverge).")
    corr_metric("selflove_z", "anxiety_z", "pearson_selflove_vs_anxiety", "Association between self-love and anxiety (expect negative if constructs diverge).")
    corr_metric("selflove_z", "guidance_child_z", "pearson_selflove_vs_guidance", "Construct validity: higher parental guidance associates with higher self-love.")

    pd.DataFrame(metrics).to_csv(H2_MEASUREMENT_PATH, index=False)


def run_h3_threshold_logits(df: pd.DataFrame) -> None:
    """Approximate proportional-odds diagnostics via stacked binary logits."""

    df = df.dropna(subset=["networth_ord", *H3_PREDICTORS]).copy()
    thresholds = sorted(df["networth_ord"].unique())
    rows: list[dict[str, object]] = []
    for cutpoint in thresholds[1:]:
        df["ge_cut"] = (df["networth_ord"] >= cutpoint).astype(int)
        data = df[["ge_cut", *H3_PREDICTORS]].dropna()
        X = sm.add_constant(data[H3_PREDICTORS], has_constant="add")
        model = sm.Logit(data["ge_cut"], X).fit(disp=False, maxiter=200)
        for term in model.params.index:
            if term == "const":
                continue
            rows.append(
                {
                    "cutpoint": cutpoint,
                    "term": term,
                    "estimate": float(model.params[term]),
                    "std_err": float(model.bse[term]),
                    "p_value": float(model.pvalues[term]),
                    "n_obs": int(model.nobs),
                }
            )
    coef_df = pd.DataFrame(rows)
    coef_df.to_csv(H3_THRESHOLD_PATH, index=False)

    summary_rows: list[dict[str, object]] = []
    for term, group in coef_df.groupby("term"):
        summary_rows.append(
            {
                "term": term,
                "mean_beta": float(group["estimate"].mean()),
                "std_beta": float(group["estimate"].std(ddof=0)),
                "min_beta": float(group["estimate"].min()),
                "max_beta": float(group["estimate"].max()),
                "range_beta": float(group["estimate"].max() - group["estimate"].min()),
                "abs_range_beta": float((group["estimate"].max() - group["estimate"].min()).__abs__()),
                "max_p_value": float(group["p_value"].max()),
                "n_thresholds": int(group["cutpoint"].nunique()),
            }
        )
    pd.DataFrame(summary_rows).to_csv(H3_SUMMARY_PATH, index=False)


def run_h4_religiosity_diagnostics(df: pd.DataFrame) -> None:
    """Compare ordinal vs categorical religiosity specifications for H4."""

    df = df.copy()
    df["religion_ord"] = df["religion"]
    df["high_anxiety"] = (df["anxiety_aligned"] >= 2).astype(int)

    cat = pd.get_dummies(df["religion_ord"].round().astype(int), prefix="religion_level", drop_first=True)
    df = pd.concat([df, cat], axis=1)
    cat_terms = [col for col in cat.columns if col.startswith("religion_level_")]

    def fit_ols(predictors: List[str]) -> sm.regression.linear_model.RegressionResultsWrapper:
        data = df[["anxiety_z", *predictors]].dropna()
        X = sm.add_constant(data[predictors].astype(float), has_constant="add")
        return sm.OLS(data["anxiety_z"], X).fit()

    def fit_logit(predictors: List[str]) -> sm.discrete.discrete_model.BinaryResultsWrapper:
        data = df[["high_anxiety", *predictors]].dropna()
        X = sm.add_constant(data[predictors].astype(float), has_constant="add")
        return sm.Logit(data["high_anxiety"], X).fit(disp=False, maxiter=200)

    ord_predictors = ["religion_ord", *H4_CONTROLS]
    cat_predictors = [*cat_terms, *H4_CONTROLS]

    ols_ord = fit_ols(ord_predictors)
    ols_cat = fit_ols(cat_predictors)
    logit_ord = fit_logit(ord_predictors)
    logit_cat = fit_logit(cat_predictors)

    def collect_terms(model_id: str, model_desc: str, model, terms: Iterable[str], model_type: str) -> list[dict[str, object]]:
        rows: list[dict[str, object]] = []
        for term in terms:
            if term not in model.params:
                continue
            beta = model.params[term]
            se = model.bse[term]
            rows.append(
                {
                    "model_id": model_id,
                    "model_type": model_type,
                    "model_desc": model_desc,
                    "term": term,
                    "estimate": float(beta),
                    "std_err": float(se),
                    "p_value": float(model.pvalues[term]),
                    "ci_low": float(beta - 1.96 * se),
                    "ci_high": float(beta + 1.96 * se),
                    "n_obs": int(model.nobs),
                }
            )
        return rows

    model_rows: list[dict[str, object]] = []
    model_rows.extend(
        collect_terms(
            model_id="ols_ordinal",
            model_desc="OLS anxiety_z ~ ordinal religiosity + controls",
            model=ols_ord,
            terms=["religion_ord"],
            model_type="OLS",
        )
    )
    model_rows.extend(
        collect_terms(
            model_id="ols_categorical",
            model_desc="OLS anxiety_z ~ religiosity dummies + controls",
            model=ols_cat,
            terms=cat_terms,
            model_type="OLS",
        )
    )
    model_rows.extend(
        collect_terms(
            model_id="logit_ordinal",
            model_desc="Logit high_anxiety ~ ordinal religiosity + controls",
            model=logit_ord,
            terms=["religion_ord"],
            model_type="LOGIT",
        )
    )
    model_rows.extend(
        collect_terms(
            model_id="logit_categorical",
            model_desc="Logit high_anxiety ~ religiosity dummies + controls",
            model=logit_cat,
            terms=cat_terms,
            model_type="LOGIT",
        )
    )
    pd.DataFrame(model_rows).to_csv(H4_MODELS_PATH, index=False)

    tests: list[dict[str, object]] = []
    f_stat, f_pvalue, df_diff = ols_cat.compare_f_test(ols_ord)
    tests.append(
        {
            "test_id": "ols_cat_vs_ord",
            "model_type": "OLS",
            "statistic": float(f_stat),
            "df_diff": float(df_diff),
            "p_value": float(f_pvalue),
            "interpretation": "F-test for whether categorical religiosity improves fit over ordinal coding.",
        }
    )

    lr_stat = 2 * (logit_cat.llf - logit_ord.llf)
    df_diff_logit = max(len(cat_terms) - 1, 1)
    lr_pvalue = float(chi2.sf(lr_stat, df_diff_logit))
    tests.append(
        {
            "test_id": "logit_cat_vs_ord",
            "model_type": "LOGIT",
            "statistic": float(lr_stat),
            "df_diff": float(df_diff_logit),
            "p_value": lr_pvalue,
            "interpretation": "Likelihood-ratio test for categorical vs ordinal religiosity.",
        }
    )

    pd.DataFrame(tests).to_csv(H4_TESTS_PATH, index=False)


def main() -> None:
    df = pd.read_csv(DATA_PATH, low_memory=False)
    add_aligned_columns(df)

    df["networth_ord"] = df["networth"]
    df["classchild_male_int"] = df["classchild"] * df["gendermale"]

    describe_h2_measurement(df)
    run_h3_threshold_logits(df)
    run_h4_religiosity_diagnostics(df)


if __name__ == "__main__":
    main()
