"""
Run the pre-specified ordered logit sensitivity for H3 using statsmodels.

Usage:
    python analysis/scripts/ordered_logit_h3.py

Outputs:
    - analysis/results/loop005_h3_ordered_logit.csv
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import List

import numpy as np
import pandas as pd
from statsmodels.miscmodels.ordinal_model import OrderedModel


DERIVED_PATH = Path("analysis/derived/loop002_likert_scales.csv")
RESULTS_PATH = Path("analysis/results/loop005_h3_ordered_logit.csv")


BASE_COVARIATES: List[str] = [
    "selfage",
    "gendermale",
    "education",
    "classchild",
    "classteen",
]


def main() -> None:
    df = pd.read_csv(DERIVED_PATH)
    # Endogenous ordinal outcome must be categorical with ordered integer labels
    if "classcurrent" not in df.columns:
        raise RuntimeError("classcurrent not found in derived data")

    cols = ["classcurrent", "4tuoqly_scaled"] + BASE_COVARIATES
    subset = df[cols].dropna()
    # Ensure outcome is int categorical 0..6
    y = subset["classcurrent"].astype(int)
    X = subset[["4tuoqly_scaled"] + BASE_COVARIATES]

    # Fit ordered logit with logit link
    model = OrderedModel(y, X, distr="logit")
    res = model.fit(method="bfgs", disp=False)

    # Extract parameter of interest
    param = "4tuoqly_scaled"
    est = float(res.params[param])
    se = float(res.bse[param])
    z = float(est / se) if se != 0 else np.nan
    p = float(res.pvalues[param])
    ci_low = est - 1.96 * se
    ci_high = est + 1.96 * se

    RESULTS_PATH.parent.mkdir(parents=True, exist_ok=True)
    out = pd.DataFrame(
        [
            {
                "hypothesis_id": "H3",
                "hypothesis_family": "digital_exposure",
                "model": "ordered_logit",
                "outcome": "classcurrent",
                "predictor": param,
                "estimate": est,
                "se": se,
                "z_value": z,
                "p_value": p,
                "ci_low": ci_low,
                "ci_high": ci_high,
                "n_obs": int(len(subset)),
                "covariates": ",".join(BASE_COVARIATES),
                "link": "logit",
                "method": "bfgs",
            }
        ]
    )
    out.to_csv(RESULTS_PATH, index=False)
    print(f"Wrote {RESULTS_PATH}")


if __name__ == "__main__":
    main()
