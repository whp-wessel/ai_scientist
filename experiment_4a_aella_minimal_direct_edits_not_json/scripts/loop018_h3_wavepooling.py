#!/usr/bin/env python3
"""Loop 018: Scenario analysis for H3 ≥$10M precision under pooled/oversampled waves.

The current ≥$10M partial proportional-odds (PPO) slope is promising but fails the
power bar once we import the cluster bootstrap variance (design effect ≈ 14.76).
This script prototypes hypothetical expansions—pooling identical survey waves
and/or oversampling the ≥$10M tier—to quantify how the analytic SE, effective
sample size, and two-sided power would change if additional data became
available. The exercise guides whether a confirmatory freeze is feasible once
multiple waves ship or if targeted oversamples are required.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List

import numpy as np
import pandas as pd

from loop010_h3_partial_models import (
    add_cutpoint_dummies,
    build_long_format,
    fit_partial_model,
    prepare_base_dataframe,
)

TABLES_DIR = Path("tables")
TABLES_DIR.mkdir(parents=True, exist_ok=True)

SUMMARY_PATH = TABLES_DIR / "loop018_h3_wavepooling_summary.csv"
POWER_PATH = Path("tables/loop016_h3_power_summary.csv")

CUTPOINT_TARGET = 5


def norm_cdf(value: float) -> float:
    """Return Φ(value) via the error function."""

    return 0.5 * (1.0 + math.erf(value / math.sqrt(2.0)))


def two_sided_power(z_value: float, alpha: float = 0.05) -> float:
    """Approximate two-sided Wald power under N(z_value, 1)."""

    if math.isnan(z_value):
        return float("nan")
    z_alpha = 1.959963984540054  # Φ^-1(1 - α/2)
    lower = norm_cdf(-z_alpha - z_value)
    upper = 1.0 - norm_cdf(z_alpha - z_value)
    return lower + upper


def load_design_effect(default_de: float = 14.75552771350343) -> float:
    """Pull the baseline design effect from the Loop 016 summary table."""

    if not POWER_PATH.exists():
        return default_de
    summary = pd.read_csv(POWER_PATH)
    row = summary[summary["metric"] == "Design effect (cluster vs. SRS)"]
    if row.empty:
        return default_de
    return float(row.iloc[0]["value"])


def replicate_waves(df: pd.DataFrame, multiplier: int) -> pd.DataFrame:
    """Concatenate identical waves to simulate pooled survey releases."""

    if multiplier <= 1:
        return df.copy()
    frames = []
    for wave_id in range(multiplier):
        tmp = df.copy()
        tmp["wave_id_sim"] = wave_id + 1
        frames.append(tmp)
    return pd.concat(frames, ignore_index=True)


def oversample_high_wealth(df: pd.DataFrame, factor: float) -> pd.DataFrame:
    """Replicate ≥$10M observations to mimic targeted oversamples."""

    if factor <= 1.0:
        return df
    mask = df["networth_ord"] >= CUTPOINT_TARGET
    subset = df[mask]
    if subset.empty:
        return df

    frames = [df]
    integer_part = int(math.floor(factor))
    additional_full = max(integer_part - 1, 0)
    for _ in range(additional_full):
        frames.append(subset.copy())

    remainder = factor - integer_part
    if remainder > 1e-9:
        n_partial = max(1, int(round(remainder * len(subset))))
        frames.append(subset.head(n_partial).copy())

    return pd.concat(frames, ignore_index=True)


def extract_cut_effect(
    result,
    cut_cols: Iterable[str],
    base_cut: int,
    cutpoint: int = CUTPOINT_TARGET,
) -> tuple[float, float]:
    """Recover the classchild effect and SE at the requested cutpoint."""

    param_index = {name: idx for idx, name in enumerate(result.params.index)}
    vector = np.zeros(len(result.params))
    vector[param_index["classchild"]] = 1.0
    if cutpoint != base_cut:
        matching = None
        for col in cut_cols:
            suffix = col.split("cut_", 1)[-1]
            try:
                value = int(suffix)
            except ValueError:
                try:
                    value = float(suffix)
                except ValueError:
                    continue
            if value == cutpoint:
                matching = col
                break
        if matching is None:
            raise KeyError(f"Missing dummy column for cutpoint {cutpoint}")
        interaction = f"classchild_x_{matching}"
        if interaction not in param_index:
            raise KeyError(f"Missing interaction coefficient {interaction}")
        vector[param_index[interaction]] = 1.0

    test = result.t_test(vector)
    effect = float(np.atleast_1d(test.effect).squeeze())
    std_err = float(np.atleast_1d(test.sd).squeeze())
    return effect, std_err


@dataclass(frozen=True)
class Scenario:
    """Configuration for a hypothetical sample expansion."""

    scenario_id: str
    description: str
    wave_multiplier: int = 1
    ge10m_multiplier: float = 1.0


SCENARIOS: List[Scenario] = [
    Scenario(
        scenario_id="baseline",
        description="Observed data (single wave, no oversample)",
        wave_multiplier=1,
        ge10m_multiplier=1.0,
    ),
    Scenario(
        scenario_id="two_waves",
        description="Pool two identical GFS waves (naïve independence assumption)",
        wave_multiplier=2,
        ge10m_multiplier=1.0,
    ),
    Scenario(
        scenario_id="three_waves",
        description="Pool three identical waves",
        wave_multiplier=3,
        ge10m_multiplier=1.0,
    ),
    Scenario(
        scenario_id="ge10m_double",
        description="Single wave + targeted 2× oversample of ≥$10M respondents",
        wave_multiplier=1,
        ge10m_multiplier=2.0,
    ),
    Scenario(
        scenario_id="two_waves_ge10m_double",
        description="Two pooled waves plus 2× ≥$10M oversample",
        wave_multiplier=2,
        ge10m_multiplier=2.0,
    ),
]


def main() -> None:
    design_effect = load_design_effect()
    raw = pd.read_csv("childhoodbalancedpublic_original.csv", low_memory=False)
    base_df = prepare_base_dataframe(raw)

    rows: list[dict[str, object]] = []
    for scenario in SCENARIOS:
        df_wave = replicate_waves(base_df, scenario.wave_multiplier)
        df_wave = oversample_high_wealth(df_wave, scenario.ge10m_multiplier)

        n_total = int(df_wave.shape[0])
        ge_mask = df_wave["networth_ord"] >= CUTPOINT_TARGET
        n_ge10m = int(ge_mask.sum())
        share_ge10m = float(n_ge10m / n_total) if n_total else float("nan")

        long_df, _ = build_long_format(df_wave)
        long_df, cut_cols, base_cut = add_cutpoint_dummies(long_df)
        result = fit_partial_model(long_df, cut_cols)
        effect, se = extract_cut_effect(result, cut_cols, base_cut, CUTPOINT_TARGET)
        analytic_z = effect / se if se else float("nan")
        analytic_power = two_sided_power(analytic_z)

        effective_n = n_total / design_effect if design_effect else float("nan")
        cluster_se = se * math.sqrt(design_effect) if se else float("nan")
        cluster_z = effect / cluster_se if cluster_se else float("nan")
        cluster_power = two_sided_power(cluster_z)

        rows.append(
            {
                "scenario_id": scenario.scenario_id,
                "description": scenario.description,
                "wave_multiplier": scenario.wave_multiplier,
                "ge10m_multiplier": scenario.ge10m_multiplier,
                "n_total": n_total,
                "n_ge10m": n_ge10m,
                "share_ge10m": share_ge10m,
                "estimate_log_odds": effect,
                "analytic_se": se,
                "analytic_z": analytic_z,
                "analytic_power": analytic_power,
                "assumed_design_effect": design_effect,
                "effective_n": effective_n,
                "cluster_se": cluster_se,
                "cluster_z": cluster_z,
                "cluster_power": cluster_power,
                "notes": "Design effect held constant at the Loop 016 bootstrap estimate.",
            }
        )

    summary = pd.DataFrame(rows)
    summary.to_csv(SUMMARY_PATH, index=False)


if __name__ == "__main__":
    main()
