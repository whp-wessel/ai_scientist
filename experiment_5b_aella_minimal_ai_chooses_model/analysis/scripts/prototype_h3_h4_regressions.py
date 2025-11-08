"""
Run exploratory OLS prototypes for hypotheses H3 and H4 using the harmonized
scales (including classcurrent outcome handling for H3).

Usage:
    python analysis/scripts/prototype_h3_h4_regressions.py

Outputs:
    - analysis/results/loop003_h3_h4_regressions.csv
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import List

import pandas as pd
import statsmodels.api as sm

DERIVED_PATH = Path("analysis/derived/loop002_likert_scales.csv")
RESULTS_PATH = Path("analysis/results/loop003_h3_h4_regressions.csv")

BASE_COVARIATES = [
    "selfage",
    "gendermale",
    "education",
    "classchild",
    "classteen",
    # note: do not include classcurrent when it is the outcome
]


@dataclass(frozen=True)
class RegressionSpec:
    hypothesis_id: str
    family: str
    outcome: str
    predictor: str
    covariates: List[str]


SPECS: List[RegressionSpec] = [
    # H3: digital exposure -> current socioeconomic status (ordinal outcome)
    RegressionSpec(
        hypothesis_id="H3",
        family="digital_exposure",
        outcome="classcurrent_z",
        predictor="4tuoqly_scaled",
        covariates=[c for c in BASE_COVARIATES if c != "classcurrent"],
    ),
    # H4: childhood depression -> adult depression
    RegressionSpec(
        hypothesis_id="H4",
        family="mental_health_continuity",
        outcome="wz901dj_scaled",
        predictor="dfqbzi5_scaled",
        covariates=BASE_COVARIATES + ["classcurrent"],
    ),
]


def run_regression(df: pd.DataFrame, spec: RegressionSpec) -> dict:
    cols = ["respondent_id", spec.outcome, spec.predictor] + spec.covariates
    subset = df[cols].dropna()
    X = subset[[spec.predictor] + spec.covariates]
    X = sm.add_constant(X, has_constant="add")
    model = sm.OLS(subset[spec.outcome], X)
    results = model.fit(cov_type="HC3")
    params = results.params
    bse = results.bse
    pvalues = results.pvalues
    est = float(params[spec.predictor])
    se = float(bse[spec.predictor])
    p = float(pvalues[spec.predictor])
    ci_low = est - 1.96 * se
    ci_high = est + 1.96 * se
    print(
        f"{spec.hypothesis_id}: n={len(subset)}, coef={est:.4f}, se={se:.4f}, p={p:.4g}"
    )
    return {
        "hypothesis_id": spec.hypothesis_id,
        "hypothesis_family": spec.family,
        "outcome": spec.outcome,
        "predictor": spec.predictor,
        "estimate": est,
        "se": se,
        "ci_low": ci_low,
        "ci_high": ci_high,
        "p_value": p,
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

