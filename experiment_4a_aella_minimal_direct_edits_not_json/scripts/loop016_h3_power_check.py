#!/usr/bin/env python3
"""Loop 016: Effective sample size and power diagnostics for the H3 ≥$10M contrast."""

from __future__ import annotations

import math
from pathlib import Path
from typing import List

import pandas as pd

DATA_PATH = Path("childhoodbalancedpublic_original.csv")
THRESHOLD_PATH = Path("tables/loop010_h3_threshold_effects.csv")
BOOT_SUMMARY_PATH = Path("tables/loop014_h3_bootstrap_summary.csv")
BOOT_DRAWS_PATH = Path("tables/loop014_h3_bootstrap_draws.csv")
SUMMARY_PATH = Path("tables/loop016_h3_power_summary.csv")
CONFIRM_PATH = Path("tables/loop016_h3_confirmatory.csv")

COUNTRY_COL = "What country do you live in? (4bxk14u)"


def norm_cdf(value: float) -> float:
    """Return Φ(value) using the error function."""

    return 0.5 * (1.0 + math.erf(value / math.sqrt(2.0)))


def two_sided_power(z_true: float, alpha: float = 0.05) -> float:
    """Two-sided Wald test power under N(z_true, 1)."""

    if math.isnan(z_true):
        return float("nan")
    z_alpha = 1.959963984540054  # Φ^-1(1 - α/2) with α=0.05
    lower = norm_cdf(-z_alpha - z_true)
    upper = 1.0 - norm_cdf(z_alpha - z_true)
    return lower + upper


def main() -> None:
    keep_cols = ["networth", "classchild", COUNTRY_COL]
    df = pd.read_csv(DATA_PATH, usecols=keep_cols, low_memory=False)
    df = df.dropna(subset=["networth", "classchild", COUNTRY_COL])
    df["networth_ord"] = df["networth"].astype(int)
    ge_10m = df["networth_ord"] >= 5

    n_total = int(df.shape[0])
    n_ge10m = int(ge_10m.sum())
    share_ge10m = float(ge_10m.mean())

    clusters = df[COUNTRY_COL]
    cluster_sizes = clusters.value_counts()
    n_clusters = int(cluster_sizes.shape[0])
    min_cluster = int(cluster_sizes.min())
    median_cluster = float(cluster_sizes.median())

    threshold_df = pd.read_csv(THRESHOLD_PATH)
    thresh_row = threshold_df[
        (threshold_df["term"] == "classchild") & (threshold_df["cutpoint"] == 5)
    ]
    if thresh_row.empty:
        raise RuntimeError("Missing ≥$10M cutpoint in threshold effects table.")
    thresh = thresh_row.iloc[0]
    analytic_effect = float(thresh["effect"])
    analytic_se = float(thresh["std_err"])
    analytic_ci_low = float(thresh["ci_low"])
    analytic_ci_high = float(thresh["ci_high"])
    analytic_z = analytic_effect / analytic_se if analytic_se else float("nan")
    analytic_power = two_sided_power(analytic_z)

    boot_summary = pd.read_csv(BOOT_SUMMARY_PATH)
    boot_row = boot_summary[boot_summary["cut_label"] == "networth_ge_10m"]
    if boot_row.empty:
        raise RuntimeError("Missing ≥$10M cutpoint in bootstrap summary table.")
    boot = boot_row.iloc[0]
    boot_mean = float(boot["mean"])
    boot_sd = float(boot["std"])
    boot_ci_low = float(boot["p2_5"])
    boot_ci_high = float(boot["p97_5"])
    boot_tail = float(boot["two_sided_tail"])
    boot_z = boot_mean / boot_sd if boot_sd else float("nan")
    boot_power = two_sided_power(boot_z)

    design_effect = (boot_sd / analytic_se) ** 2 if analytic_se else float("nan")
    effective_n = n_total / design_effect if design_effect else float("nan")

    draws = pd.read_csv(BOOT_DRAWS_PATH)
    cut_draws = draws[draws["cut_label"] == "networth_ge_10m"]["estimate"]
    pos_share = float((cut_draws > 0).mean()) if not cut_draws.empty else float("nan")
    wald_reject_srs = float((cut_draws.abs() / analytic_se > 1.96).mean()) if analytic_se else float("nan")
    wald_reject_boot = float((cut_draws.abs() / boot_sd > 1.96).mean()) if boot_sd else float("nan")

    rows: List[dict[str, object]] = [
        {
            "section": "sample",
            "metric": "Respondents with complete H3 data",
            "value": n_total,
            "units": "individuals",
            "notes": "Rows with non-missing childhood class and ordered net-worth ladder.",
        },
        {
            "section": "sample",
            "metric": "Respondents in ≥$10M tier",
            "value": n_ge10m,
            "units": "individuals",
            "notes": "Counts $10M and ≥$100M categories (networth_ord ≥ 5).",
        },
        {
            "section": "sample",
            "metric": "Share in ≥$10M tier",
            "value": share_ge10m,
            "units": "share",
            "notes": "n_ge10m / n_total",
        },
        {
            "section": "sample",
            "metric": "Countries represented",
            "value": n_clusters,
            "units": "countries",
            "notes": f"Minimum cluster size = {min_cluster}, median = {median_cluster:.0f}.",
        },
        {
            "section": "analytic_precision",
            "metric": "PPO effect (log-odds)",
            "value": analytic_effect,
            "units": "log-odds",
            "notes": "Partial proportional-odds estimate at the ≥$10M cutpoint (tables/loop010_h3_threshold_effects.csv).",
        },
        {
            "section": "analytic_precision",
            "metric": "Analytic SE (SRS)",
            "value": analytic_se,
            "units": "log-odds",
            "notes": "Standard error from the stacked PPO model under the SRS assumption.",
        },
        {
            "section": "analytic_precision",
            "metric": "Analytic 95% CI low",
            "value": analytic_ci_low,
            "units": "log-odds",
            "notes": "effect ± 1.96 × SE.",
        },
        {
            "section": "analytic_precision",
            "metric": "Analytic 95% CI high",
            "value": analytic_ci_high,
            "units": "log-odds",
            "notes": "effect ± 1.96 × SE.",
        },
        {
            "section": "analytic_precision",
            "metric": "Approximate power (α=0.05)",
            "value": analytic_power,
            "units": "probability",
            "notes": "Two-sided Wald test power using the analytic z-statistic.",
        },
        {
            "section": "bootstrap_precision",
            "metric": "Cluster-bootstrap mean",
            "value": boot_mean,
            "units": "log-odds",
            "notes": "Average childhood-class slope from 300 country-cluster resamples.",
        },
        {
            "section": "bootstrap_precision",
            "metric": "Cluster-bootstrap SD",
            "value": boot_sd,
            "units": "log-odds",
            "notes": "Standard deviation of the bootstrap draws.",
        },
        {
            "section": "bootstrap_precision",
            "metric": "Bootstrap percentile CI low",
            "value": boot_ci_low,
            "units": "log-odds",
            "notes": "2.5th percentile of the bootstrap draws.",
        },
        {
            "section": "bootstrap_precision",
            "metric": "Bootstrap percentile CI high",
            "value": boot_ci_high,
            "units": "log-odds",
            "notes": "97.5th percentile of the bootstrap draws.",
        },
        {
            "section": "bootstrap_precision",
            "metric": "Two-sided tail probability",
            "value": boot_tail,
            "units": "probability",
            "notes": "2 × min(P(draw > 0), P(draw < 0)) across replicates.",
        },
        {
            "section": "bootstrap_precision",
            "metric": "Share of positive draws",
            "value": pos_share,
            "units": "share",
            "notes": "Fraction of bootstrap replicates with estimate > 0.",
        },
        {
            "section": "bootstrap_precision",
            "metric": "Approximate power (α=0.05)",
            "value": boot_power,
            "units": "probability",
            "notes": "Two-sided Wald power using bootstrap mean/SD.",
        },
        {
            "section": "bootstrap_precision",
            "metric": "Wald rejection share (analytic SE)",
            "value": wald_reject_srs,
            "units": "share",
            "notes": "Fraction of bootstrap draws whose |β|/SE_analytic exceeds 1.96.",
        },
        {
            "section": "bootstrap_precision",
            "metric": "Wald rejection share (bootstrap SD)",
            "value": wald_reject_boot,
            "units": "share",
            "notes": "Fraction of draws whose |β|/SD_boot exceeds 1.96.",
        },
        {
            "section": "derived",
            "metric": "Design effect (cluster vs. SRS)",
            "value": design_effect,
            "units": "ratio",
            "notes": "(bootstrap SD ÷ analytic SE)².",
        },
        {
            "section": "derived",
            "metric": "Effective sample size",
            "value": effective_n,
            "units": "individuals",
            "notes": "n_total ÷ design effect.",
        },
    ]

    summary = pd.DataFrame(rows)
    summary.to_csv(SUMMARY_PATH, index=False)

    confirm_row = {
        "contrast_id": "H3_ge10m_classchild",
        "estimand": "Log-odds slope for childhood class predicting Pr(net worth ≥ $10M)",
        "model": "Partial proportional-odds stacked logit",
        "n_total": n_total,
        "n_ge10m": n_ge10m,
        "share_ge10m": share_ge10m,
        "estimate_log_odds": analytic_effect,
        "analytic_se": analytic_se,
        "analytic_ci_low": analytic_ci_low,
        "analytic_ci_high": analytic_ci_high,
        "bootstrap_mean": boot_mean,
        "bootstrap_sd": boot_sd,
        "bootstrap_ci_low": boot_ci_low,
        "bootstrap_ci_high": boot_ci_high,
        "design_effect": design_effect,
        "effective_n": effective_n,
        "power_srs": analytic_power,
        "power_cluster": boot_power,
        "positive_draw_share": pos_share,
        "wald_reject_share_srs": wald_reject_srs,
        "wald_reject_share_boot": wald_reject_boot,
        "script": "PYTHONHASHSEED=20251016 python scripts/loop014_h3_cluster_bootstrap.py --n-reps 300; python scripts/loop016_h3_power_check.py",
        "notes": "Analytic stats from tables/loop010_h3_threshold_effects.csv; bootstrap stats from tables/loop014_h3_bootstrap_summary.csv/draws.csv.",
    }
    pd.DataFrame([confirm_row]).to_csv(CONFIRM_PATH, index=False)


if __name__ == "__main__":
    main()
