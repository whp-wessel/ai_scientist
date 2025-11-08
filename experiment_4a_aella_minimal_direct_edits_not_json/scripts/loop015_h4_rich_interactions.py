#!/usr/bin/env python3
"""Loop 015: H4 religiosity × class interactions with richer covariates."""

from __future__ import annotations

from pathlib import Path
from typing import Iterable, List

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import statsmodels.api as sm
from statsmodels.miscmodels.ordinal_model import OrderedModel

from likert_utils import align_likert, ensure_columns, get_likert_specs, zscore

DATA_PATH = Path("childhoodbalancedpublic_original.csv")
TABLES_DIR = Path("tables")
FIGURES_DIR = Path("figures")
TABLES_DIR.mkdir(parents=True, exist_ok=True)
FIGURES_DIR.mkdir(parents=True, exist_ok=True)

COEFF_PATH = TABLES_DIR / "loop015_h4_interactions_rich.csv"
GRID_PATH = TABLES_DIR / "loop015_h4_predicted_grid.csv"
FIGURE_PATH = FIGURES_DIR / "loop015_h4_classinteraction.png"

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


def add_religion_dummies(df: pd.DataFrame) -> None:
    """Create religiosity dummies (reference = none) and their class interactions."""

    df["religion"] = df["religion"].astype(float)
    for level, col in RELIGION_DUMMIES.items():
        df[col] = (df["religion"] == level).astype(float)
        df[f"{col}_classchild_int"] = df[col] * df["classchild"]


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


def fit_ordered_model(df: pd.DataFrame, predictors: list[str], terms: list[str]) -> list[dict[str, object]]:
    """Fit the religiosity × class model for the 3-bin ordinal anxiety outcome."""

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
        model_id="loop015_h4_ord3_rich",
        model_desc="Ordered logit: anxiety_ord3 ~ religiosity dummies × classchild + richer controls",
        model_type="ORDERED_LOGIT",
        params=params,
        bse=result.bse[keep],
        pvalues=result.pvalues[keep],
        conf_int=conf,
        terms=terms,
        n_obs=result.nobs,
    )


def fit_logit_model(df: pd.DataFrame, predictors: list[str], terms: list[str]) -> tuple[list[dict[str, object]], sm.discrete.discrete_model.BinaryResultsWrapper]:
    """Fit the religiosity × class model for the ≥5 high-anxiety binary outcome."""

    data = df[["anxiety_high_flag", *predictors]].dropna()
    if data.empty:
        return [], None
    y = data["anxiety_high_flag"].astype(int)
    X = sm.add_constant(data[predictors].astype(float), has_constant="add")
    result = sm.Logit(y, X).fit(disp=False, maxiter=500)
    rows = collect_terms(
        model_id="loop015_h4_highflag_rich",
        model_desc="Logit: anxiety_high_flag ~ religiosity dummies × classchild + richer controls",
        model_type="LOGIT",
        params=result.params,
        bse=result.bse,
        pvalues=result.pvalues,
        conf_int=result.conf_int(),
        terms=terms,
        n_obs=result.nobs,
    )
    return rows, result


def build_prediction_grid(
    logit_result: sm.discrete.discrete_model.BinaryResultsWrapper,
    predictors: list[str],
    class_values: Iterable[float],
) -> pd.DataFrame:
    """Generate predicted high-anxiety probabilities across classchild and religiosity levels."""

    if logit_result is None:
        return pd.DataFrame()

    means = {}
    for col in predictors:
        if col in ("classchild", "classcurrent"):
            continue
        means[col] = logit_result.model.exog[:, logit_result.model.exog_names.index(col)].mean()

    rows: list[dict[str, object]] = []
    for rel_level, rel_label in RELIGION_LEVELS.items():
        for class_value in class_values:
            row = {col: 0.0 for col in predictors}
            row["classchild"] = class_value
            row["classcurrent"] = logit_result.model.exog[:, logit_result.model.exog_names.index("classcurrent")].mean()
            row["classteen"] = means.get("classteen", 0.0)
            row["selfage"] = means.get("selfage", 0.0)
            row["gendermale"] = means.get("gendermale", 0.0)
            row["education"] = means.get("education", 0.0)
            for dummy_level, dummy_col in RELIGION_DUMMIES.items():
                value = 1.0 if rel_level == dummy_level else 0.0
                row[dummy_col] = value
                row[f"{dummy_col}_classchild_int"] = value * class_value
            rows.append({"classchild": class_value, "religion_level": rel_label, **row})

    design = pd.DataFrame(rows)
    X = sm.add_constant(design[predictors], has_constant="add")
    linpred = np.dot(X, logit_result.params.loc[X.columns])
    probs = 1 / (1 + np.exp(-linpred))
    design["predicted_prob"] = probs
    return design[["classchild", "religion_level", "predicted_prob"]]


def plot_predictions(grid: pd.DataFrame) -> None:
    """Plot predicted high-anxiety probabilities by classchild & religiosity."""

    fig, ax = plt.subplots(figsize=(6, 4))
    for rel_label, subset in grid.groupby("religion_level"):
        ax.plot(
            subset["classchild"],
            subset["predicted_prob"],
            label=rel_label.title(),
            linewidth=2,
        )
    ax.set_xlabel("Childhood class (0=underclass … 6=elite)")
    ax.set_ylabel("Predicted P(high anxiety ≥5)")
    ax.set_ylim(0, 0.7)
    ax.legend(title="Religious practice", frameon=False)
    ax.grid(alpha=0.3, linestyle="--")
    fig.tight_layout()
    fig.savefig(FIGURE_PATH, dpi=300)
    plt.close(fig)


def main() -> None:
    df = pd.read_csv(DATA_PATH, low_memory=False)
    add_aligned_columns(df)
    add_religion_dummies(df)

    df["anxiety_ord3"] = collapse_to_three_bins(df["anxiety_aligned"])
    df["anxiety_high_flag"] = derive_high_flag(df)

    interaction_terms = [f"{col}_classchild_int" for col in RELIGION_DUMMIES.values()]
    predictors = [*BASE_CONTROLS, *RELIGION_DUMMIES.values(), *interaction_terms]
    report_terms = [*RELIGION_DUMMIES.values(), *interaction_terms]

    rows: list[dict[str, object]] = []
    rows.extend(fit_ordered_model(df, predictors, report_terms))
    logit_rows, logit_result = fit_logit_model(df, predictors, report_terms)
    rows.extend(logit_rows)
    pd.DataFrame(rows).to_csv(COEFF_PATH, index=False)

    class_values = np.linspace(0, 6, num=50)
    grid = build_prediction_grid(logit_result, predictors, class_values)
    if not grid.empty:
        grid.to_csv(GRID_PATH, index=False)
        plot_predictions(grid)


if __name__ == "__main__":
    main()
