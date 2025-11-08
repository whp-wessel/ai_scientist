"""
Run exploratory OLS prototypes for hypotheses H1 and H2 using the harmonized
Likert scales.

Usage:
    python analysis/scripts/prototype_h1_h2_regressions.py

Outputs:
    - analysis/results/loop002_h1_h2_regressions.csv
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import List

import pandas as pd
import statsmodels.api as sm

DERIVED_PATH = Path("analysis/derived/loop002_likert_scales.csv")
RESULTS_PATH = Path("analysis/results/loop002_h1_h2_regressions.csv")

COVARIATES = [
    "selfage",
    "gendermale",
    "education",
    "classchild",
    "classteen",
    "classcurrent",
]


@dataclass(frozen=True)
class RegressionSpec:
    hypothesis_id: str
    outcome: str
    predictor: str
    family: str


SPECS: List[RegressionSpec] = [
    RegressionSpec(
        hypothesis_id="H1",
        family="childhood_adversity",
        outcome="ix5iyv3_scaled",
        predictor="mds78zu_scaled",
    ),
    RegressionSpec(
        hypothesis_id="H2",
        family="parental_support",
        outcome="z0mhd63_scaled",
        predictor="pqo6jmj_scaled",
    ),
]


def run_regression(df: pd.DataFrame, spec: RegressionSpec) -> dict:
    cols = ["respondent_id", spec.outcome, spec.predictor] + COVARIATES
    subset = df[cols].dropna()
    X = subset[[spec.predictor] + COVARIATES]
    X = sm.add_constant(X, has_constant="add")
    model = sm.OLS(subset[spec.outcome], X)
    results = model.fit(cov_type="HC3")
    params = results.params
    bse = results.bse
    tvalues = results.tvalues
    pvalues = results.pvalues
    print(f"{spec.hypothesis_id}: n={len(subset)}, coef={params[spec.predictor]:.4f}, se={bse[spec.predictor]:.4f}, p={pvalues[spec.predictor]:.4g}")
    return {
        "hypothesis_id": spec.hypothesis_id,
        "hypothesis_family": spec.family,
        "outcome": spec.outcome,
        "predictor": spec.predictor,
        "estimate": params[spec.predictor],
        "se": bse[spec.predictor],
        "t_value": tvalues[spec.predictor],
        "p_value": pvalues[spec.predictor],
        "n_obs": len(subset),
        "r_squared": results.rsquared,
        "adj_r_squared": results.rsquared_adj,
        "covariates": ",".join(COVARIATES),
        "cov_type": "HC3",
    }


def main() -> None:
    df = pd.read_csv(DERIVED_PATH)
    OUTPUT_PATH = RESULTS_PATH
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    rows = [run_regression(df, spec) for spec in SPECS]
    pd.DataFrame(rows).to_csv(OUTPUT_PATH, index=False)
    print(f"Wrote {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
