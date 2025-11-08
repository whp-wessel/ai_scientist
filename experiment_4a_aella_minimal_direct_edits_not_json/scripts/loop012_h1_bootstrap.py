#!/usr/bin/env python3
"""Loop 012 bootstrap diagnostics for the confirmatory H1 interactions."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List

import numpy as np
import pandas as pd
import statsmodels.api as sm

from likert_utils import align_likert, ensure_columns, get_likert_specs, zscore

DATA_PATH = Path("childhoodbalancedpublic_original.csv")
TABLES_DIR = Path("tables")
TABLES_DIR.mkdir(parents=True, exist_ok=True)

BOOT_PATH = TABLES_DIR / "loop012_h1_bootstrap_draws.csv"
BOOT_SUMMARY_PATH = TABLES_DIR / "loop012_h1_bootstrap_summary.csv"
SLOPE_PATH = TABLES_DIR / "loop012_h1_bootstrap_slopes.csv"
SLOPE_SUMMARY_PATH = TABLES_DIR / "loop012_h1_bootstrap_slopes_summary.csv"

OUTCOME = "depression_z"

CONTROL_COLUMNS = [
    "classteen",
    "selfage",
    "gendermale",
    "education",
]


@dataclass(frozen=True)
class ModelSpec:
    """Container for a single interaction model used in the bootstrap."""

    model_id: str
    interaction_label: str
    predictors: List[str]
    interaction_term: str
    needs_guidance: bool = False


MODEL_SPECS: Dict[str, ModelSpec] = {
    "guidance": ModelSpec(
        model_id="loop004_h1_guidance_interaction",
        interaction_label="guidance_buffering",
        predictors=[
            "abuse_child_z",
            "abuse_teen_z",
            "guidance_child_z",
            "abuse_child_guidance_int",
            *CONTROL_COLUMNS,
        ],
        interaction_term="abuse_child_guidance_int",
        needs_guidance=True,
    ),
    "male": ModelSpec(
        model_id="loop004_h1_gender_interaction",
        interaction_label="male_vulnerability",
        predictors=[
            "abuse_child_z",
            "abuse_teen_z",
            "abuse_child_male_int",
            *CONTROL_COLUMNS,
            "gendermale",
        ],
        interaction_term="abuse_child_male_int",
    ),
}


def add_aligned_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Attach aligned and z-scored Likert variables."""

    specs = get_likert_specs()
    ensure_columns(df, specs)
    aligned = align_likert(df, specs)
    for spec in specs:
        df[spec.aligned_column] = aligned[spec.aligned_column]
        df[spec.z_column] = zscore(aligned[spec.aligned_column])
    return df


def prepare_dataframe() -> pd.DataFrame:
    """Load, align, and derive interaction-ready dataframe."""

    df = pd.read_csv(DATA_PATH, low_memory=False)
    add_aligned_columns(df)
    df["abuse_child_guidance_int"] = df["abuse_child_z"] * df["guidance_child_z"]
    df["abuse_child_male_int"] = df["abuse_child_z"] * df["gendermale"]
    return df


def fit_ols(data: pd.DataFrame, outcome: str, predictors: Iterable[str]) -> sm.regression.linear_model.RegressionResultsWrapper:
    """Fit an OLS model with an explicit intercept."""

    X = sm.add_constant(data[list(predictors)], has_constant="add")
    model = sm.OLS(data[outcome], X).fit()
    return model


def sample_with_replacement(df: pd.DataFrame, rng: np.random.Generator) -> pd.DataFrame:
    """Return a bootstrap sample with replacement."""

    indices = rng.integers(0, len(df), size=len(df))
    return df.iloc[indices].reset_index(drop=True)


def bh_adjust(p_values: np.ndarray) -> np.ndarray:
    """Apply Benjamini-Hochberg adjustment within a family."""

    m = len(p_values)
    order = np.argsort(p_values)
    adjusted = np.empty(m, dtype=float)
    prev = 1.0
    for i in range(m - 1, -1, -1):
        rank = i + 1
        adj = p_values[order[i]] * m / rank
        adj = min(adj, prev)
        adjusted[order[i]] = adj
        prev = adj
    return np.clip(adjusted, 0, 1)


def summarize_series(values: pd.Series, label: str) -> dict[str, object]:
    """Return key summary statistics for a bootstrap distribution."""

    clean = values.dropna()
    if clean.empty:
        return {
            "metric": label,
            "n_reps": 0,
            "mean": float("nan"),
            "std": float("nan"),
            "p2_5": float("nan"),
            "p25": float("nan"),
            "median": float("nan"),
            "p75": float("nan"),
            "p97_5": float("nan"),
        }
    return {
        "metric": label,
        "n_reps": int(clean.shape[0]),
        "mean": float(clean.mean()),
        "std": float(clean.std(ddof=0)),
        "p2_5": float(clean.quantile(0.025)),
        "p25": float(clean.quantile(0.25)),
        "median": float(clean.quantile(0.5)),
        "p75": float(clean.quantile(0.75)),
        "p97_5": float(clean.quantile(0.975)),
    }


def compute_two_sided_tail(values: pd.Series) -> float:
    """Approximate a two-sided p-value from bootstrap draws."""

    clean = values.dropna()
    if clean.empty:
        return float("nan")
    n = clean.shape[0]
    pos = int((clean > 0).sum())
    neg = int((clean < 0).sum())
    tail = 2 * min(pos, neg) / n
    if tail == 0:
        tail = 2 / (n + 1)
    return float(min(tail, 1.0))


def main(n_reps: int, seed: int) -> None:
    df = prepare_dataframe()
    rng = np.random.default_rng(seed)

    draws: list[dict[str, object]] = []
    slope_draws: list[dict[str, object]] = []

    prepared: Dict[str, pd.DataFrame] = {}
    for key, spec in MODEL_SPECS.items():
        cols = [OUTCOME, *spec.predictors]
        prepared[key] = df[cols].dropna().reset_index(drop=True)

    for rep in range(1, n_reps + 1):
        p_values: list[float] = []
        idxs: list[int] = []
        for key, spec in MODEL_SPECS.items():
            sample = sample_with_replacement(prepared[key], rng)
            model = fit_ols(sample, OUTCOME, spec.predictors)
            term = spec.interaction_term
            if term not in model.params:
                continue
            beta = float(model.params[term])
            se = float(model.bse[term])
            t_value = float(model.tvalues[term])
            p_value = float(model.pvalues[term])
            row = {
                "replicate": rep,
                "model_key": key,
                "model_id": spec.model_id,
                "interaction_label": spec.interaction_label,
                "term": term,
                "estimate": beta,
                "std_err": se,
                "t_value": t_value,
                "p_value": p_value,
                "n_obs": int(model.nobs),
            }
            idxs.append(len(draws))
            p_values.append(p_value)
            draws.append(row)

            if key == "guidance":
                beta_main = float(model.params.get("abuse_child_z", float("nan")))
                beta_int = beta
                for level_label, level_value in (("minus1sd", -1.0), ("plus1sd", 1.0)):
                    slope = beta_main + beta_int * level_value
                    slope_draws.append(
                        {
                            "replicate": rep,
                            "slope_id": f"abuse_at_{level_label}",
                            "level_value": level_value,
                            "estimate": float(slope),
                            "n_obs": int(model.nobs),
                        }
                    )

        if p_values:
            adjusted = bh_adjust(np.array(p_values, dtype=float))
            for local_idx, q_value in zip(idxs, adjusted):
                draws[local_idx]["q_value"] = float(q_value)

    draws_df = pd.DataFrame(draws)
    draws_df.to_csv(BOOT_PATH, index=False)

    slope_df = pd.DataFrame(slope_draws)
    slope_df.to_csv(SLOPE_PATH, index=False)

    summaries: list[dict[str, object]] = []
    for key, spec in MODEL_SPECS.items():
        subset = draws_df[draws_df["model_key"] == key]["estimate"]
        summaries.append(summarize_series(subset, f"{spec.interaction_label}_coef"))
        summaries[-1]["two_sided_tail"] = compute_two_sided_tail(subset)

    slope_summaries: list[dict[str, object]] = []
    for slope_id, group in slope_df.groupby("slope_id"):
        slope_summaries.append(summarize_series(group["estimate"], slope_id))
        slope_summaries[-1]["two_sided_tail"] = compute_two_sided_tail(group["estimate"])

    summary_df = pd.DataFrame(summaries)
    summary_df.to_csv(BOOT_SUMMARY_PATH, index=False)

    slope_summary_df = pd.DataFrame(slope_summaries)
    slope_summary_df.to_csv(SLOPE_SUMMARY_PATH, index=False)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Bootstrap the confirmatory H1 interaction models.")
    parser.add_argument("--n-reps", type=int, default=500, help="Number of bootstrap replicates (default: 500).")
    parser.add_argument("--seed", type=int, default=20251016, help="Random seed for numpy's default_rng.")
    args = parser.parse_args()
    main(n_reps=args.n_reps, seed=args.seed)
