#!/usr/bin/env python3
"""
Run minimal exploratory OLS models based on analysis/hypotheses.csv.

- Reads dataset (CSV) and hypotheses registry
- For each hypothesis row, supports multiple outcomes separated by commas
- Fits OLS: outcome ~ predictor + covariates (all standardized)
- Appends results to analysis/results.csv with effect size, SE, CI, p-value

Usage:
  python scripts/analysis/run_models.py \
    --input childhoodbalancedpublic_original.csv \
    --hypotheses analysis/hypotheses.csv \
    --results analysis/results.csv \
    --seed 20251016

Notes:
  - Designed for exploratory use (confirmatory flag is read from hypotheses)
  - Assumes SRS; sets design_used=false and provides srs_justification text
  - Uses normal approximation for p-values (large-sample t ≈ N(0,1))
"""
from __future__ import annotations

import argparse
import csv
import math
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Sequence

import numpy as np
import pandas as pd

REPO = Path(__file__).resolve().parents[2]


def zscore(x: pd.Series) -> pd.Series:
    mu = x.mean()
    sd = x.std(ddof=1)
    if sd == 0 or pd.isna(sd):
        return x * 0.0
    return (x - mu) / sd


@dataclass
class ModelSpec:
    hypothesis_id: str
    hypothesis_family: str
    confirmatory: bool
    outcome: str
    predictor: str
    covariates: List[str]


def parse_hypotheses(df: pd.DataFrame) -> List[ModelSpec]:
    specs: List[ModelSpec] = []
    for _, row in df.iterrows():
        hid = str(row.get("hypothesis_id", "")).strip()
        fam = str(row.get("hypothesis_family", "")).strip()
        conf_raw = str(row.get("confirmatory", "false")).strip().lower()
        confirmatory = conf_raw in {"true", "1", "yes"}
        outcomes_raw = str(row.get("outcome_var", "")).strip()
        predictor = str(row.get("predictor_var", "")).strip()
        cov_raw = str(row.get("covariates", "")).strip()

        outcomes = [o.strip() for o in outcomes_raw.split(",") if o.strip()]
        covars = [c.strip() for c in cov_raw.split(",") if c.strip()]
        for out in outcomes:
            specs.append(
                ModelSpec(
                    hypothesis_id=hid,
                    hypothesis_family=fam,
                    confirmatory=confirmatory,
                    outcome=out,
                    predictor=predictor,
                    covariates=covars,
                )
            )
    return specs


def ols_fit(y: np.ndarray, X: np.ndarray) -> tuple[np.ndarray, np.ndarray, float, int]:
    # Add small ridge if singular
    XtX = X.T @ X
    try:
        XtX_inv = np.linalg.inv(XtX)
    except np.linalg.LinAlgError:
        XtX_inv = np.linalg.pinv(XtX)
    beta = XtX_inv @ (X.T @ y)
    resid = y - X @ beta
    n, k = X.shape
    dof = max(n - k, 1)
    sigma2 = float((resid @ resid) / dof)
    var_beta = sigma2 * XtX_inv
    se = np.sqrt(np.clip(np.diag(var_beta), 0, np.inf))
    return beta, se, sigma2, dof


def normal_pvalue(z: float) -> float:
    # two-sided p under N(0,1)
    # Phi(z) = 0.5 * (1 + erf(z / sqrt(2)))
    phi = 0.5 * (1.0 + math.erf(abs(z) / math.sqrt(2.0)))
    return max(0.0, min(1.0, 2.0 * (1.0 - phi)))


def fit_spec(df: pd.DataFrame, spec: ModelSpec) -> Optional[dict]:
    cols = [spec.outcome, spec.predictor] + spec.covariates
    missing = [c for c in cols if c not in df.columns]
    if missing:
        return {
            "result_id": "",
            "hypothesis_id": spec.hypothesis_id,
            "hypothesis_family": spec.hypothesis_family,
            "confirmatory": spec.confirmatory,
            "estimate": "",
            "se": "",
            "ci_low": "",
            "ci_high": "",
            "p_value": "",
            "q_value": "",
            "design_used": False,
            "srs_justification": "No weights/strata/clusters found; SRS approximation used (see config/survey_design.yaml).",
            "notes": f"Skipped: missing columns {missing} for outcome {spec.outcome} and predictor {spec.predictor}",
        }

    sub = df[cols].dropna()
    if sub.shape[0] < 30:
        return {
            "result_id": "",
            "hypothesis_id": spec.hypothesis_id,
            "hypothesis_family": spec.hypothesis_family,
            "confirmatory": spec.confirmatory,
            "estimate": "",
            "se": "",
            "ci_low": "",
            "ci_high": "",
            "p_value": "",
            "q_value": "",
            "design_used": False,
            "srs_justification": "No weights/strata/clusters found; SRS approximation used (see config/survey_design.yaml).",
            "notes": f"Skipped: insufficient complete cases (n={sub.shape[0]})",
        }

    y = zscore(sub[spec.outcome]).to_numpy(dtype=float)
    X_cols = [spec.predictor] + spec.covariates
    X = np.column_stack([np.ones(sub.shape[0])] + [zscore(sub[c]).to_numpy(dtype=float) for c in X_cols])

    beta, se, sigma2, dof = ols_fit(y, X)

    # Index 1 corresponds to the predictor coefficient (0 is intercept)
    b = float(beta[1])
    s = float(se[1]) if se[1] > 0 else float("nan")
    z = b / s if s and s > 0 else float("nan")
    p = normal_pvalue(z) if not math.isnan(z) else float("nan")
    ci95 = 1.96 * s if not math.isnan(s) else float("nan")

    return {
        "estimate": b,
        "se": s,
        "ci_low": b - ci95 if not math.isnan(ci95) else "",
        "ci_high": b + ci95 if not math.isnan(ci95) else "",
        "p_value": p,
        "notes": f"OLS (standardized); n={sub.shape[0]}; dof={dof}; sigma2={sigma2:.4f}",
    }


def write_results(results_path: Path, rows: List[dict]):
    results_path.parent.mkdir(parents=True, exist_ok=True)
    header = [
        "result_id",
        "hypothesis_id",
        "hypothesis_family",
        "confirmatory",
        "estimate",
        "se",
        "ci_low",
        "ci_high",
        "p_value",
        "q_value",
        "design_used",
        "srs_justification",
        "notes",
    ]
    write_header = not results_path.exists() or results_path.read_text().strip() == ""
    with results_path.open("a", newline="") as f:
        w = csv.DictWriter(f, fieldnames=header)
        if write_header:
            w.writeheader()
        for r in rows:
            w.writerow(r)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True)
    ap.add_argument("--hypotheses", default=str(REPO / "analysis" / "hypotheses.csv"))
    ap.add_argument("--results", default=str(REPO / "analysis" / "results.csv"))
    ap.add_argument("--seed", type=int, default=20251016)
    args = ap.parse_args()

    df = pd.read_csv(REPO / args.input)
    # Drop empty first column if present
    if df.columns[0].strip() == "":
        df = df.drop(columns=df.columns[0])

    hyp_df = pd.read_csv(args.hypotheses)
    specs = parse_hypotheses(hyp_df)

    out_rows: List[dict] = []
    counter = 1
    for spec in specs:
        res = fit_spec(df, spec)
        if res is None:
            continue
        # Assemble full row
        rid = f"R003_{counter:03d}"
        counter += 1
        row = {
            "result_id": rid,
            "hypothesis_id": spec.hypothesis_id,
            "hypothesis_family": spec.hypothesis_family,
            "confirmatory": spec.confirmatory,
            "q_value": "",  # exploratory families only in this loop
            "design_used": False,
            "srs_justification": "No weights/strata/clusters found; SRS approximation used (see config/survey_design.yaml).",
        }
        row.update(res)
        out_rows.append(row)

    write_results(Path(args.results), out_rows)
    print(f"Wrote {len(out_rows)} result rows to {args.results}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

