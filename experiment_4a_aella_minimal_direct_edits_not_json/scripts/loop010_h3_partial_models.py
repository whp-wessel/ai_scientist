#!/usr/bin/env python3
"""Loop 010 models that relax the H3 proportional-odds assumption.

We approximate a partial proportional-odds (PPO) specification by stacking the
net-worth outcome across cumulative logits and allowing the childhood class
terms to vary by cutpoint while keeping the control set parallel. The script
exports coefficient tables plus threshold-specific marginal effects so the
ordered-logit diagnostics from Loop 008 can be benchmarked against this more
flexible alternative.
"""

from __future__ import annotations

from pathlib import Path
from typing import Iterable, List

import numpy as np
import pandas as pd
import statsmodels.api as sm

DATA_PATH = Path("childhoodbalancedpublic_original.csv")
TABLES_DIR = Path("tables")
TABLES_DIR.mkdir(parents=True, exist_ok=True)

COEFF_PATH = TABLES_DIR / "loop010_h3_partial_params.csv"
THRESHOLD_PATH = TABLES_DIR / "loop010_h3_threshold_effects.csv"
FIT_PATH = TABLES_DIR / "loop010_h3_partial_fit.csv"

PROP_TERMS = ["classteen", "selfage", "gendermale", "education"]
NON_PROP_TERMS = ["classchild", "classchild_male_int"]


def prepare_base_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """Return the core dataframe with required columns and no missing data."""

    keep_cols = [
        "networth",
        "classchild",
        "classteen",
        "selfage",
        "gendermale",
        "education",
    ]
    missing_cols = [col for col in keep_cols if col not in df.columns]
    if missing_cols:
        raise KeyError(f"Missing expected columns: {missing_cols}")

    subset = df[keep_cols].copy()
    subset["networth_ord"] = subset["networth"].astype(int)
    subset["classchild_male_int"] = subset["classchild"] * subset["gendermale"]
    subset = subset.dropna()
    return subset


def build_long_format(df: pd.DataFrame) -> tuple[pd.DataFrame, List[int]]:
    """Stack the ordinal outcome into cumulative logits for PPO fitting."""

    thresholds = sorted(df["networth_ord"].unique())
    long_frames: list[pd.DataFrame] = []
    for cut in thresholds[1:]:
        tmp = df.copy()
        tmp["ge_cut"] = (tmp["networth_ord"] >= cut).astype(int)
        tmp["cutpoint"] = int(cut)
        long_frames.append(tmp)
    long_df = pd.concat(long_frames, ignore_index=True)
    long_df["cutpoint"] = long_df["cutpoint"].astype(int)
    return long_df, thresholds[1:]


def add_cutpoint_dummies(long_df: pd.DataFrame) -> tuple[pd.DataFrame, List[str], int]:
    """Attach cutpoint dummies (minus the baseline) for intercept shifts."""

    cut_dummies = pd.get_dummies(long_df["cutpoint"], prefix="cut", drop_first=True, dtype=int)
    long_df = pd.concat([long_df, cut_dummies], axis=1)
    base_cut = long_df["cutpoint"].min()
    return long_df, list(cut_dummies.columns), base_cut


def fit_partial_model(long_df: pd.DataFrame, cut_cols: Iterable[str]) -> sm.discrete.discrete_model.BinaryResultsWrapper:
    """Fit the stacked logit allowing the childhood class terms to vary by cut."""

    predictors: list[str] = [*PROP_TERMS, *NON_PROP_TERMS, *cut_cols]
    for term in NON_PROP_TERMS:
        for cut_col in cut_cols:
            interaction = f"{term}_x_{cut_col}"
            long_df[interaction] = long_df[term] * long_df[cut_col]
            predictors.append(interaction)

    X = sm.add_constant(long_df[predictors], has_constant="add")
    model = sm.Logit(long_df["ge_cut"], X)
    return model.fit(disp=False, maxiter=200)


def export_coefficients(result: sm.discrete.discrete_model.BinaryResultsWrapper) -> None:
    """Persist raw coefficient table for full transparency."""

    rows: list[dict[str, object]] = []
    for term in result.params.index:
        rows.append(
            {
                "term": term,
                "estimate": float(result.params[term]),
                "std_err": float(result.bse[term]),
                "z_value": float(result.tvalues[term]),
                "p_value": float(result.pvalues[term]),
            }
        )
    pd.DataFrame(rows).to_csv(COEFF_PATH, index=False)


def export_threshold_effects(
    result: sm.discrete.discrete_model.BinaryResultsWrapper,
    cut_values: Iterable[int],
    cut_cols: Iterable[str],
    base_cut: int,
) -> None:
    """Recover threshold-specific effects for the non-parallel terms."""

    param_index = {name: idx for idx, name in enumerate(result.params.index)}
    rows: list[dict[str, object]] = []

    def column_for_cut(cut: int) -> str | None:
        for col in cut_cols:
            suffix = col.split("cut_", 1)[-1]
            try:
                col_cut = int(suffix)
            except ValueError:
                col_cut = float(suffix)
            if col_cut == cut:
                return col
        return None

    for term in NON_PROP_TERMS:
        for cut in cut_values:
            vec = np.zeros(len(result.params))
            vec[param_index[term]] = 1.0

            if cut != base_cut:
                interaction_column = column_for_cut(cut)
                if interaction_column is None:
                    raise KeyError(f"Missing dummy column for cutpoint {cut}")
                interaction_name = f"{term}_x_{interaction_column}"
                if interaction_name not in param_index:
                    raise KeyError(f"Missing interaction parameter {interaction_name}")
                vec[param_index[interaction_name]] = 1.0

            test = result.t_test(vec)
            effect = float(np.atleast_1d(test.effect).squeeze())
            std_err = float(np.atleast_1d(test.sd).squeeze())
            z_value = float(effect / std_err) if std_err > 0 else float("nan")
            p_value = float(np.atleast_1d(test.pvalue).squeeze())

            rows.append(
                {
                    "term": term,
                    "cutpoint": int(cut),
                    "effect": effect,
                    "std_err": std_err,
                    "z_value": z_value,
                    "p_value": p_value,
                    "ci_low": effect - 1.96 * std_err,
                    "ci_high": effect + 1.96 * std_err,
                }
            )

    pd.DataFrame(rows).to_csv(THRESHOLD_PATH, index=False)


def export_fit_stats(
    result: sm.discrete.discrete_model.BinaryResultsWrapper,
    n_individuals: int,
) -> None:
    """Record high-level fit diagnostics."""

    metrics = [
        {"metric": "n_long_rows", "value": int(result.nobs)},
        {"metric": "n_individuals", "value": n_individuals},
        {"metric": "log_likelihood", "value": float(result.llf)},
        {"metric": "aic", "value": float(result.aic)},
        {"metric": "bic", "value": float(result.bic)},
        {"metric": "pseudo_r2_mcfadden", "value": float(result.prsquared)},
    ]
    pd.DataFrame(metrics).to_csv(FIT_PATH, index=False)


def main() -> None:
    df = pd.read_csv(DATA_PATH, low_memory=False)
    base_df = prepare_base_dataframe(df)
    long_df, cut_values = build_long_format(base_df)
    long_df, cut_cols, base_cut = add_cutpoint_dummies(long_df)

    result = fit_partial_model(long_df, cut_cols)
    export_coefficients(result)
    export_threshold_effects(result, cut_values, cut_cols, base_cut)
    export_fit_stats(result, n_individuals=len(base_df))


if __name__ == "__main__":
    main()
