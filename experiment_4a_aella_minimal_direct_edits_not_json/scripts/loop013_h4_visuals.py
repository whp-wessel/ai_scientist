#!/usr/bin/env python3
"""Summarize H4 religiosity effects across outcome codings and emit a figure."""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

TABLES_DIR = Path("tables")
FIGURES_DIR = Path("figures")
TABLES_DIR.mkdir(parents=True, exist_ok=True)
FIGURES_DIR.mkdir(parents=True, exist_ok=True)

LOOP003_PATH = TABLES_DIR / "loop003_model_estimates.csv"
LOOP012_PATH = TABLES_DIR / "loop012_h4_alt_models.csv"
SUMMARY_PATH = TABLES_DIR / "loop013_h4_outcome_effects.csv"
FIGURE_PATH = FIGURES_DIR / "loop013_h4_outcome_effects.png"


def _load_loop003() -> pd.DataFrame:
    df = pd.read_csv(LOOP003_PATH)
    keep_ids = {"loop003_h4_ols": "Anxiety z-score (OLS, SD units)",
                "loop003_h4_logit": "High anxiety ≥2 (logit, log-odds)"}
    subset = df[(df["model_id"].isin(keep_ids)) & (df["term"] == "religion")].copy()
    subset["model_label"] = subset["model_id"].map(keep_ids)
    subset["scale"] = np.where(subset["model_type"] == "OLS",
                               "SD change in anxiety per religiosity step",
                               "Log-odds change per religiosity step")
    subset["source_table"] = str(LOOP003_PATH)
    return subset


def _load_loop012() -> pd.DataFrame:
    df = pd.read_csv(LOOP012_PATH)
    keep_ids = {
        "ordered_logit_anxiety3": "3-bin anxiety (ordered logit, log-odds)",
        "logit_high_anxiety": "High anxiety ≥5 (logit, log-odds)",
        "lpm_high_anxiety": "High anxiety ≥5 (LPM, percentage points)",
    }
    subset = df[(df["model_id"].isin(keep_ids)) & (df["term"] == "religion")].copy()
    subset["model_label"] = subset["model_id"].map(keep_ids)
    subset["scale"] = subset["model_label"].apply(
        lambda lbl: "Percentage-point change per religiosity step" if "LPM" in lbl else "Log-odds change per religiosity step"
    )
    subset.loc[subset["model_type"] == "OLS", "scale"] = "Percentage-point change per religiosity step"
    subset["source_table"] = str(LOOP012_PATH)
    return subset


def build_summary() -> pd.DataFrame:
    combined = pd.concat([_load_loop003(), _load_loop012()], ignore_index=True)
    columns = [
        "model_label",
        "estimate",
        "std_err",
        "ci_low",
        "ci_high",
        "p_value",
        "n_obs",
        "model_type",
        "scale",
        "source_table",
    ]
    summary = combined[columns].copy()
    summary = summary.sort_values("model_label").reset_index(drop=True)
    summary.to_csv(SUMMARY_PATH, index=False)
    return summary


def make_figure(summary: pd.DataFrame) -> None:
    fig, ax = plt.subplots(figsize=(7.5, 4))
    y_pos = np.arange(len(summary))
    estimates = summary["estimate"].to_numpy()
    ci_low = estimates - summary["ci_low"].to_numpy()
    ci_high = summary["ci_high"].to_numpy() - estimates
    ax.errorbar(
        estimates,
        y_pos,
        xerr=[ci_low, ci_high],
        fmt="o",
        color="#08306b",
        ecolor="#6baed6",
        elinewidth=2,
        capsize=4,
        markersize=6,
    )
    ax.axvline(0, color="#bdbdbd", linestyle="--", linewidth=1)
    ax.set_yticks(y_pos)
    ax.set_yticklabels(summary["model_label"])
    ax.set_xlabel("Religiosity effect (units noted per label)")
    ax.set_title("H4: Religiosity consistently predicts lower anxiety across codings")
    ax.grid(axis="x", color="#f0f0f0")
    fig.tight_layout()
    fig.savefig(FIGURE_PATH, dpi=300)
    plt.close(fig)


def main() -> None:
    summary = build_summary()
    make_figure(summary)


if __name__ == "__main__":
    main()
