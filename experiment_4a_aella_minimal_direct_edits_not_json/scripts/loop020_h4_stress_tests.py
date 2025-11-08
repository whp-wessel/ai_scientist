#!/usr/bin/env python3
"""Loop 020: Ridge + outcome robustness stress tests for H4 religiosity × class interactions."""

from __future__ import annotations

from pathlib import Path
from typing import Dict, Iterable, List, Tuple

import numpy as np
import pandas as pd
import statsmodels.api as sm
from scipy import stats
from statsmodels.miscmodels.ordinal_model import OrderedModel, OrderedResults

from likert_utils import align_likert, ensure_columns, get_likert_specs, zscore

DATA_PATH = Path("childhoodbalancedpublic_original.csv")
TABLES_DIR = Path("tables")
TABLES_DIR.mkdir(parents=True, exist_ok=True)

COEFF_OUTPUT = TABLES_DIR / "loop020_h4_stress_test_coeffs.csv"
LOGIT_GRID_OUTPUT = TABLES_DIR / "loop020_h4_highflag_predicted_grid.csv"
LOGIT_DELTA_OUTPUT = TABLES_DIR / "loop020_h4_highflag_prob_deltas.csv"
RIDGE_GRID_OUTPUT = TABLES_DIR / "loop020_h4_ridge_probabilities.csv"
RIDGE_DELTA_OUTPUT = TABLES_DIR / "loop020_h4_ridge_prob_deltas.csv"
ORDINAL_GRID_OUTPUT = TABLES_DIR / "loop020_h4_ord3_predicted_grid.csv"
ORDINAL_DELTA_OUTPUT = TABLES_DIR / "loop020_h4_ord3_prob_deltas.csv"

ANXIETY_PRIMARY = "I tend to suffer from anxiety (npvfh98)-neg"
ANXIETY_SECONDARY = "I tend to suffer from anxiety -neg"

RELIGION_LEVELS = {
    0.0: "none",
    1.0: "slight",
    2.0: "moderate",
    3.0: "serious",
}
RELIGION_DUMMIES = {
    1.0: "religion_slight",
    2.0: "religion_moderate",
    3.0: "religion_serious",
}

BASE_CONTROLS = [
    "classchild",
    "classcurrent",
    "classteen",
    "selfage",
    "gendermale",
    "education",
]

RIDGE_ALPHA = 5.0
CLASS_LOW = 0.0
CLASS_HIGH = 6.0
CLASS_GRID = np.linspace(CLASS_LOW, CLASS_HIGH, num=25)


def add_aligned_columns(df: pd.DataFrame) -> None:
    """Attach aligned + z-scored Likert items referenced downstream."""

    specs = get_likert_specs()
    ensure_columns(df, specs)
    aligned = align_likert(df, specs)
    for spec in specs:
        df[spec.aligned_column] = aligned[spec.aligned_column]
        df[spec.z_column] = zscore(aligned[spec.aligned_column])


def collapse_to_three_bins(series: pd.Series) -> pd.Series:
    """Map 7-point aligned anxiety scores onto three ordered bins."""

    shifted = (series + 3).round()
    collapsed = pd.Series(pd.NA, index=series.index, dtype="Int64")
    collapsed[(shifted >= 0) & (shifted <= 2)] = 0
    collapsed[(shifted >= 3) & (shifted <= 4)] = 1
    collapsed[(shifted >= 5) & (shifted <= 6)] = 2
    return collapsed


def derive_high_flag(df: pd.DataFrame) -> pd.Series:
    """Create a ≥5 high-anxiety flag that mirrors the confirmatory spec."""

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


def add_religion_dummies(df: pd.DataFrame) -> None:
    """Create religiosity dummies (reference = none) and class interactions."""

    df["religion"] = df["religion"].astype(float)
    for level, col in RELIGION_DUMMIES.items():
        df[col] = (df["religion"] == level).astype(float)
        df[f"{col}_classchild_int"] = df[col] * df["classchild"]


def collect_rows(
    model_id: str,
    outcome: str,
    estimator: str,
    penalty: float,
    params: pd.Series,
    bse: pd.Series,
    pvalues: pd.Series,
    conf_int: pd.DataFrame,
    terms: Iterable[str],
    n_obs: int,
    notes: str,
) -> list[dict[str, object]]:
    """Convert coefficient vectors to tidy rows."""

    rows: list[dict[str, object]] = []
    for term in terms:
        if term not in params.index:
            continue
        rows.append(
            {
                "model_id": model_id,
                "outcome": outcome,
                "estimator": estimator,
                "penalty_alpha": penalty,
                "term": term,
                "estimate": float(params[term]),
                "std_err": float(bse[term]),
                "ci_low": float(conf_int.loc[term, 0]),
                "ci_high": float(conf_int.loc[term, 1]),
                "p_value": float(pvalues[term]),
                "n_obs": int(n_obs),
                "notes": notes,
            }
        )
    return rows


def fit_logit_model(
    df: pd.DataFrame,
    predictors: list[str],
    terms: list[str],
) -> Tuple[list[dict[str, object]], sm.discrete.discrete_model.BinaryResultsWrapper]:
    """Run the baseline (unpenalized) logistic interaction model."""

    data = df[["anxiety_high_flag", *predictors]].dropna()
    y = data["anxiety_high_flag"].astype(int)
    X = sm.add_constant(data[predictors].astype(float), has_constant="add")
    model = sm.Logit(y, X)
    result = model.fit(disp=False, maxiter=500)
    rows = collect_rows(
        model_id="loop020_h4_highflag_logit",
        outcome="high_anxiety_flag",
        estimator="Logit",
        penalty=0.0,
        params=result.params,
        bse=result.bse,
        pvalues=result.pvalues,
        conf_int=result.conf_int(),
        terms=terms,
        n_obs=result.nobs,
        notes="Baseline confirmatory specification",
    )
    return rows, result


def ridge_standard_errors(
    X: pd.DataFrame,
    params: pd.Series,
    alpha: float,
    pen_weight: np.ndarray,
) -> Tuple[pd.Series, pd.DataFrame]:
    """Approximate ridge-penalized standard errors via (X'WX + αI)^{-1}."""

    linear = X.values @ params.values
    probs = 1.0 / (1.0 + np.exp(-linear))
    weights = probs * (1 - probs)
    XtWX = X.T.values @ (weights[:, None] * X.values)
    penalty_matrix = np.diag(alpha * pen_weight)
    information = XtWX + penalty_matrix
    try:
        cov = np.linalg.inv(information)
    except np.linalg.LinAlgError:
        cov = np.linalg.pinv(information)
    se = np.sqrt(np.diag(cov))
    return pd.Series(se, index=X.columns), pd.DataFrame(cov, index=X.columns, columns=X.columns)


def fit_ridge_logit(
    df: pd.DataFrame,
    predictors: list[str],
    terms: list[str],
    alpha: float,
) -> Tuple[list[dict[str, object]], pd.Series]:
    """Run an L2-penalized logistic regression to shrink wide coefficients."""

    data = df[["anxiety_high_flag", *predictors]].dropna()
    y = data["anxiety_high_flag"].astype(int)
    X = sm.add_constant(data[predictors].astype(float), has_constant="add")
    pen_weight = np.ones(X.shape[1])
    const_idx = list(X.columns).index("const")
    pen_weight[const_idx] = 0.0
    model = sm.Logit(y, X)
    result = model.fit_regularized(
        alpha=alpha,
        L1_wt=0.0,
        pen_weight=pen_weight,
        maxiter=1000,
        trim_mode="off",
        disp=False,
    )
    params = pd.Series(result.params, index=X.columns)
    se, _ = ridge_standard_errors(X, params, alpha, pen_weight)
    z_scores = params / se
    pvalues = pd.Series(2 * (1 - stats.norm.cdf(np.abs(z_scores))), index=X.columns)
    ci_low = params - 1.96 * se
    ci_high = params + 1.96 * se
    conf_int = pd.DataFrame({0: ci_low, 1: ci_high})
    rows = collect_rows(
        model_id="loop020_h4_highflag_ridge",
        outcome="high_anxiety_flag",
        estimator="Logit",
        penalty=alpha,
        params=params,
        bse=se,
        pvalues=pvalues,
        conf_int=conf_int,
        terms=terms,
        n_obs=len(y),
        notes="Ridge penalty applied to shrink imprecise interactions",
    )
    return rows, params


def fit_ordered_model(
    df: pd.DataFrame,
    predictors: list[str],
    terms: list[str],
) -> Tuple[list[dict[str, object]], OrderedResults | None]:
    """Estimate the 3-bin ordinal anxiety specification with interactions."""

    data = df[["anxiety_ord3", *predictors]].dropna()
    if data.empty:
        return [], None
    y = data["anxiety_ord3"].astype(int)
    X = data[predictors].astype(float)
    model = OrderedModel(y, X, distr="logit")
    result = model.fit(method="bfgs", disp=False, maxiter=500)
    threshold_terms = [idx for idx in result.params.index if idx.startswith("threshold") or "/" in idx]
    keep = [idx for idx in result.params.index if idx not in threshold_terms]
    params = result.params.loc[keep]
    conf = result.conf_int().loc[keep]
    rows = collect_rows(
        model_id="loop020_h4_ord3_logit",
        outcome="anxiety_ord3",
        estimator="Ordered logit",
        penalty=0.0,
        params=params,
        bse=result.bse[keep],
        pvalues=result.pvalues[keep],
        conf_int=conf,
        terms=terms,
        n_obs=result.nobs,
        notes="3-bin ordinal anxiety robustness check",
    )
    return rows, result


def build_logit_grid(
    params: pd.Series,
    predictors: list[str],
    df: pd.DataFrame,
    class_values: Iterable[float],
) -> pd.DataFrame:
    """Generate predicted high-anxiety probabilities for logistic models."""

    means = df[predictors].mean(numeric_only=True).to_dict()
    rows: list[dict[str, object]] = []
    for rel_level, rel_label in RELIGION_LEVELS.items():
        for class_value in class_values:
            design: Dict[str, float] = {col: float(means.get(col, 0.0)) for col in predictors}
            design["classchild"] = class_value
            for level, dummy in RELIGION_DUMMIES.items():
                value = 1.0 if rel_level == level else 0.0
                design[dummy] = value
                design[f"{dummy}_classchild_int"] = value * class_value
            linear = params.get("const", 0.0)
            linear += sum(params.get(col, 0.0) * val for col, val in design.items())
            prob = 1.0 / (1.0 + np.exp(-linear))
            rows.append(
                {
                    "classchild": class_value,
                    "religion_level": rel_label,
                    "predicted_prob": prob,
                }
            )
    return pd.DataFrame(rows)


def summarize_probability_deltas(grid: pd.DataFrame, value_col: str) -> pd.DataFrame:
    """Compute Δ(classchild 6 − 0) within each religiosity level."""

    low = grid[np.isclose(grid["classchild"], CLASS_LOW)].set_index("religion_level")[value_col]
    high = grid[np.isclose(grid["classchild"], CLASS_HIGH)].set_index("religion_level")[value_col]
    deltas = pd.DataFrame(
        {
            "religion_level": low.index,
            f"{value_col}_classchild_low": low.values,
            f"{value_col}_classchild_high": high.loc[low.index].values,
        }
    )
    deltas["delta_pp_within_level"] = deltas[f"{value_col}_classchild_high"] - deltas[f"{value_col}_classchild_low"]
    baseline = deltas.loc[deltas["religion_level"] == "none", "delta_pp_within_level"].iloc[0]
    deltas["delta_pp_vs_none"] = deltas["delta_pp_within_level"] - baseline
    return deltas


def build_ordinal_grid(
    result: OrderedResults,
    df: pd.DataFrame,
    predictors: list[str],
    class_values: Iterable[float],
) -> pd.DataFrame:
    """Generate predictions for the highest anxiety bin under the ordinal model."""

    means = df[predictors].mean(numeric_only=True).to_dict()
    rows: list[dict[str, object]] = []
    design_rows: list[dict[str, float]] = []
    for rel_level, rel_label in RELIGION_LEVELS.items():
        for class_value in class_values:
            design: Dict[str, float] = {col: float(means.get(col, 0.0)) for col in predictors}
            design["classchild"] = class_value
            for level, dummy in RELIGION_DUMMIES.items():
                value = 1.0 if rel_level == level else 0.0
                design[dummy] = value
                design[f"{dummy}_classchild_int"] = value * class_value
            rows.append({"classchild": class_value, "religion_level": rel_label})
            design_rows.append(design)
    design_df = pd.DataFrame(design_rows, columns=predictors).astype(float)
    probs = result.model.predict(result.params, exog=design_df, which="prob")
    if probs.ndim != 2:
        raise RuntimeError("Unexpected ordinal prediction output shape")
    top_probs = probs[:, -1]
    grid = pd.DataFrame(rows)
    grid["predicted_prob_top"] = top_probs
    return grid


def main() -> None:
    df = pd.read_csv(DATA_PATH, low_memory=False)
    add_aligned_columns(df)
    add_religion_dummies(df)
    df["anxiety_ord3"] = collapse_to_three_bins(df["anxiety_aligned"])
    df["anxiety_high_flag"] = derive_high_flag(df)

    interaction_terms = [f"{col}_classchild_int" for col in RELIGION_DUMMIES.values()]
    predictors = [*BASE_CONTROLS, *RELIGION_DUMMIES.values(), *interaction_terms]
    report_terms = [*interaction_terms]

    rows: list[dict[str, object]] = []

    logit_rows, logit_result = fit_logit_model(df, predictors, report_terms)
    rows.extend(logit_rows)
    if logit_result is not None:
        logit_grid = build_logit_grid(logit_result.params, predictors, df, CLASS_GRID)
        logit_grid.to_csv(LOGIT_GRID_OUTPUT, index=False)
        summarize_probability_deltas(logit_grid, "predicted_prob").to_csv(LOGIT_DELTA_OUTPUT, index=False)

    ridge_rows, ridge_params = fit_ridge_logit(df, predictors, report_terms, RIDGE_ALPHA)
    rows.extend(ridge_rows)
    if ridge_rows:
        ridge_grid = build_logit_grid(ridge_params, predictors, df, CLASS_GRID)
        ridge_grid.to_csv(RIDGE_GRID_OUTPUT, index=False)
        summarize_probability_deltas(ridge_grid, "predicted_prob").to_csv(RIDGE_DELTA_OUTPUT, index=False)

    ordered_rows, ordered_result = fit_ordered_model(df, predictors, report_terms)
    rows.extend(ordered_rows)
    if ordered_result is not None:
        ordinal_grid = build_ordinal_grid(ordered_result, df, predictors, CLASS_GRID)
        ordinal_grid.to_csv(ORDINAL_GRID_OUTPUT, index=False)
        summarize_probability_deltas(ordinal_grid, "predicted_prob_top").to_csv(ORDINAL_DELTA_OUTPUT, index=False)

    pd.DataFrame(rows).to_csv(COEFF_OUTPUT, index=False)


if __name__ == "__main__":
    main()
