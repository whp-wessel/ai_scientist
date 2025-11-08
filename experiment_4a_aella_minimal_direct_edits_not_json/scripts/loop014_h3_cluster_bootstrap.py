#!/usr/bin/env python3
"""Loop 014: Clustered bootstrap of the H3 PPO estimator."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List

import numpy as np
import pandas as pd
import statsmodels.api as sm

DATA_PATH = Path("childhoodbalancedpublic_original.csv")
TABLES_DIR = Path("tables")
TABLES_DIR.mkdir(parents=True, exist_ok=True)

CLUSTER_COLUMN = "What country do you live in? (4bxk14u)"
PROP_TERMS = ["classteen", "selfage", "gendermale", "education"]
NON_PROP_TERMS = ["classchild", "classchild_male_int"]
TARGET_CUTPOINTS = {
    3: "networth_ge_100k",
    4: "networth_ge_1m",
    5: "networth_ge_10m",
}

DRAWS_PATH = TABLES_DIR / "loop014_h3_bootstrap_draws.csv"
SUMMARY_PATH = TABLES_DIR / "loop014_h3_bootstrap_summary.csv"


@dataclass(frozen=True)
class BootstrapResult:
    """Container for a single threshold-specific bootstrap draw."""

    replicate: int
    cutpoint: int
    cut_label: str
    estimate: float
    std_err: float
    p_value: float
    ci_low: float
    ci_high: float
    n_obs: int
    n_long_rows: int


def prepare_dataframe() -> pd.DataFrame:
    """Return the base PPO dataframe with cluster labels and no missing data."""

    keep_cols = [
        "networth",
        "classchild",
        "classteen",
        "selfage",
        "gendermale",
        "education",
        CLUSTER_COLUMN,
    ]
    df = pd.read_csv(DATA_PATH, usecols=keep_cols, low_memory=False)
    df = df.dropna(subset=["networth", CLUSTER_COLUMN])
    df["networth_ord"] = df["networth"].astype(int)
    df["classchild_male_int"] = df["classchild"] * df["gendermale"]
    df = df.dropna()
    df["cluster_id"] = df[CLUSTER_COLUMN].astype(str)
    return df


def build_long_format(df: pd.DataFrame) -> tuple[pd.DataFrame, List[int]]:
    """Stack the ordinal outcome into cumulative logits."""

    thresholds = sorted(df["networth_ord"].unique())
    frames: list[pd.DataFrame] = []
    for cut in thresholds[1:]:
        tmp = df.copy()
        tmp["ge_cut"] = (tmp["networth_ord"] >= cut).astype(int)
        tmp["cutpoint"] = int(cut)
        frames.append(tmp)
    long_df = pd.concat(frames, ignore_index=True)
    return long_df, thresholds[1:]


def add_cutpoint_dummies(long_df: pd.DataFrame) -> tuple[pd.DataFrame, List[str], int]:
    """Attach cutpoint dummies (minus the baseline)."""

    cut_dummies = pd.get_dummies(long_df["cutpoint"], prefix="cut", drop_first=True, dtype=int)
    long_df = pd.concat([long_df, cut_dummies], axis=1)
    base_cut = int(long_df["cutpoint"].min())
    return long_df, list(cut_dummies.columns), base_cut


def fit_partial_model(long_df: pd.DataFrame, cut_cols: Iterable[str]) -> sm.discrete.discrete_model.BinaryResultsWrapper:
    """Fit the stacked logit that relaxes proportional odds."""

    predictors: list[str] = [*PROP_TERMS, *NON_PROP_TERMS, *cut_cols]
    for term in NON_PROP_TERMS:
        for cut_col in cut_cols:
            interaction = f"{term}_x_{cut_col}"
            long_df[interaction] = long_df[term] * long_df[cut_col]
            predictors.append(interaction)

    X = sm.add_constant(long_df[predictors], has_constant="add")
    model = sm.Logit(long_df["ge_cut"], X)
    return model.fit(disp=False, maxiter=200)


def _column_for_cut(cut_cols: Iterable[str], cut: int) -> str | None:
    """Locate the dummy column corresponding to a specific cutpoint."""

    for col in cut_cols:
        suffix = col.split("cut_", 1)[-1]
        try:
            value = int(suffix)
        except ValueError:
            try:
                value = float(suffix)
            except ValueError:
                continue
        if value == cut:
            return col
    return None


def extract_threshold_effect(
    result: sm.discrete.discrete_model.BinaryResultsWrapper,
    cut_cols: Iterable[str],
    base_cut: int,
    cut: int,
    label: str,
) -> BootstrapResult:
    """Recover the net childhood-class effect at a given cutpoint."""

    param_index = {name: idx for idx, name in enumerate(result.params.index)}
    vec = np.zeros(len(result.params))
    vec[param_index["classchild"]] = 1.0
    if cut != base_cut:
        cut_col = _column_for_cut(cut_cols, cut)
        if cut_col is None:
            raise KeyError(f"Missing dummy column for cutpoint {cut}")
        interaction = f"classchild_x_{cut_col}"
        if interaction not in param_index:
            raise KeyError(f"Missing interaction term {interaction}")
        vec[param_index[interaction]] = 1.0

    test = result.t_test(vec)
    effect = float(np.atleast_1d(test.effect).squeeze())
    std_err = float(np.atleast_1d(test.sd).squeeze())
    z_value = effect / std_err if std_err > 0 else float("nan")
    p_value = float(np.atleast_1d(test.pvalue).squeeze())
    ci_low = effect - 1.96 * std_err
    ci_high = effect + 1.96 * std_err
    return BootstrapResult(
        replicate=0,
        cutpoint=cut,
        cut_label=label,
        estimate=effect,
        std_err=std_err,
        p_value=p_value,
        ci_low=ci_low,
        ci_high=ci_high,
        n_obs=int(getattr(result, "nobs", 0)),
        n_long_rows=int(getattr(result, "nobs", 0)),
    )


def sample_by_cluster(cluster_frames: Dict[str, pd.DataFrame], rng: np.random.Generator) -> pd.DataFrame:
    """Resample clusters with replacement and concatenate their rows."""

    cluster_ids = list(cluster_frames.keys())
    picks = rng.choice(cluster_ids, size=len(cluster_ids), replace=True)
    frames = [cluster_frames[c] for c in picks]
    sample = pd.concat(frames, ignore_index=True)
    sample["cluster_id"] = sample["cluster_id"].astype(str)
    return sample


def summarize_draws(draws: pd.DataFrame) -> pd.DataFrame:
    """Compute percentile summaries and tail probabilities ordered by cutpoint."""

    summaries: list[dict[str, object]] = []
    grouped = list(draws.groupby("cut_label"))
    grouped.sort(key=lambda item: int(item[1]["cutpoint"].iloc[0]))
    for cut, group in grouped:
        estimates = group["estimate"].dropna()
        if estimates.empty:
            summaries.append(
                {
                    "cut_label": cut,
                    "cutpoint": int(group["cutpoint"].iloc[0]),
                    "n_success": 0,
                    "mean": float("nan"),
                    "std": float("nan"),
                    "p2_5": float("nan"),
                    "p25": float("nan"),
                    "median": float("nan"),
                    "p75": float("nan"),
                    "p97_5": float("nan"),
                    "two_sided_tail": float("nan"),
                }
            )
            continue
        pos = (estimates > 0).sum()
        neg = (estimates < 0).sum()
        tail = 2 * min(pos, neg) / len(estimates)
        if tail == 0 and len(estimates) > 0:
            tail = 2 / (len(estimates) + 1)
        summaries.append(
            {
                "cut_label": cut,
                "cutpoint": int(group["cutpoint"].iloc[0]),
                "n_success": int(len(estimates)),
                "mean": float(estimates.mean()),
                "std": float(estimates.std(ddof=0)),
                "p2_5": float(estimates.quantile(0.025)),
                "p25": float(estimates.quantile(0.25)),
                "median": float(estimates.quantile(0.5)),
                "p75": float(estimates.quantile(0.75)),
                "p97_5": float(estimates.quantile(0.975)),
                "two_sided_tail": float(min(tail, 1.0)),
            }
        )
    return pd.DataFrame(summaries)


def main(n_reps: int, seed: int) -> None:
    base_df = prepare_dataframe()
    clusters = base_df["cluster_id"].unique().tolist()
    if not clusters:
        raise RuntimeError("No cluster labels detected; cannot run clustered bootstrap.")
    cluster_frames = {cluster: base_df[base_df["cluster_id"] == cluster].copy() for cluster in clusters}

    rng = np.random.default_rng(seed)
    draws: list[dict[str, object]] = []
    failures = 0

    for rep in range(1, n_reps + 1):
        sample = sample_by_cluster(cluster_frames, rng)
        sample_long, _ = build_long_format(sample)
        sample_long, cut_cols, base_cut = add_cutpoint_dummies(sample_long)
        try:
            result = fit_partial_model(sample_long, cut_cols)
        except Exception:  # pragma: no cover - statsmodels failure path
            failures += 1
            continue

        for cut, label in TARGET_CUTPOINTS.items():
            boot = extract_threshold_effect(result, cut_cols, base_cut, cut, label)
            boot_dict = boot.__dict__.copy()
            boot_dict.update(
                {
                    "replicate": rep,
                    "n_individuals": int(sample.shape[0]),
                    "n_clusters_sampled": int(len(clusters)),
                }
            )
            draws.append(boot_dict)

    draws_df = pd.DataFrame(draws)
    draws_df.to_csv(DRAWS_PATH, index=False)

    summary_df = summarize_draws(draws_df)
    summary_df["n_failures"] = failures
    summary_df.to_csv(SUMMARY_PATH, index=False)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Clustered bootstrap for the H3 PPO estimator.")
    parser.add_argument("--n-reps", type=int, default=400, help="Number of bootstrap replicates (default: 400).")
    parser.add_argument("--seed", type=int, default=20251016, help="Random seed for numpy's default_rng.")
    args = parser.parse_args()
    main(n_reps=args.n_reps, seed=args.seed)
