"""
Run the frozen confirmatory OLS specifications for hypotheses H1–H4.

Usage:
    python analysis/scripts/run_confirmatory_ols.py

Outputs:
    - analysis/results/loop005_confirmatory_ols.csv

The script assumes `analysis/derived/loop002_likert_scales.csv` already exists
and contains the harmonized *_scaled / *_z columns plus the shared covariates
described in the PAP. All models are estimated with HC3 robust standard errors.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import List

import pandas as pd
import statsmodels.api as sm

DERIVED_PATH = Path("analysis/derived/loop002_likert_scales.csv")
RESULTS_PATH = Path("analysis/results/loop005_confirmatory_ols.csv")


@dataclass(frozen=True)
class RegressionSpec:
    result_id: str
    hypothesis_id: str
    family: str
    outcome: str
    predictor: str
    covariates: List[str]


BASE_COVARIATES = [
    "selfage",
    "gendermale",
    "education",
    "classchild",
    "classteen",
    "classcurrent",
]

SPECS: List[RegressionSpec] = [
    RegressionSpec(
        result_id="H1_loop005_confirm_ols",
        hypothesis_id="H1",
        family="childhood_adversity",
        outcome="ix5iyv3_scaled",
        predictor="mds78zu_scaled",
        covariates=BASE_COVARIATES,
    ),
    RegressionSpec(
        result_id="H2_loop005_confirm_ols",
        hypothesis_id="H2",
        family="parental_support",
        outcome="z0mhd63_scaled",
        predictor="pqo6jmj_scaled",
        covariates=BASE_COVARIATES,
    ),
    RegressionSpec(
        result_id="H3_loop005_confirm_ols",
        hypothesis_id="H3",
        family="digital_exposure",
        outcome="classcurrent_z",
        predictor="4tuoqly_scaled",
        covariates=[c for c in BASE_COVARIATES if c != "classcurrent"],
    ),
    RegressionSpec(
        result_id="H4_loop005_confirm_ols",
        hypothesis_id="H4",
        family="mental_health_continuity",
        outcome="wz901dj_scaled",
        predictor="dfqbzi5_scaled",
        covariates=BASE_COVARIATES,
    ),
]


def run_regression(df: pd.DataFrame, spec: RegressionSpec) -> dict:
    cols = ["respondent_id", spec.outcome, spec.predictor] + spec.covariates
    subset = df[cols].dropna()

    X = subset[[spec.predictor] + spec.covariates]
    X = sm.add_constant(X, has_constant="add")
    model = sm.OLS(subset[spec.outcome], X)
    results = model.fit(cov_type="HC3")

    est = float(results.params[spec.predictor])
    se = float(results.bse[spec.predictor])
    ci_low = est - 1.96 * se
    ci_high = est + 1.96 * se
    p_value = float(results.pvalues[spec.predictor])

    print(
        f"{spec.hypothesis_id} ({spec.family}): "
        f"n={len(subset)}, coef={est:.4f}, se={se:.4f}, p={p_value:.2g}"
    )

    return {
        "result_id": spec.result_id,
        "hypothesis_id": spec.hypothesis_id,
        "hypothesis_family": spec.family,
        "model": "ols_hc3",
        "outcome": spec.outcome,
        "predictor": spec.predictor,
        "estimate": est,
        "se": se,
        "ci_low": ci_low,
        "ci_high": ci_high,
        "p_value": p_value,
        "n_obs": int(len(subset)),
        "r_squared": float(results.rsquared),
        "adj_r_squared": float(results.rsquared_adj),
        "covariates": ",".join(spec.covariates),
        "cov_type": "HC3",
    }


def main() -> None:
    df = pd.read_csv(DERIVED_PATH)
    RESULTS_PATH.parent.mkdir(parents=True, exist_ok=True)
    rows = [run_regression(df, spec) for spec in SPECS]
    pd.DataFrame(rows).to_csv(RESULTS_PATH, index=False)
    print(f"Wrote {RESULTS_PATH}")


if __name__ == "__main__":
    main()
