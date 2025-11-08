#!/usr/bin/env python3
"""Loop 012 visuals/tables comparing PPO vs multinomial H3 estimators."""

from __future__ import annotations

from pathlib import Path
from typing import Dict

import matplotlib.pyplot as plt
import pandas as pd

DATA_PATH = Path("childhoodbalancedpublic_original.csv")
TABLES_DIR = Path("tables")
FIGURES_DIR = Path("figures")
TABLES_DIR.mkdir(parents=True, exist_ok=True)
FIGURES_DIR.mkdir(parents=True, exist_ok=True)

PPO_THRESHOLD_PATH = TABLES_DIR / "loop010_h3_threshold_effects.csv"
PPO_PARAM_PATH = TABLES_DIR / "loop010_h3_partial_params.csv"
MULTI_MARGINAL_PATH = TABLES_DIR / "loop011_h3_multinomial_marginals.csv"
MULTI_FIT_PATH = TABLES_DIR / "loop011_h3_multinomial_fit.csv"
PPO_FIT_PATH = TABLES_DIR / "loop010_h3_partial_fit.csv"

CLASS_EFFECTS_PATH = TABLES_DIR / "loop012_h3_classchild_effects.csv"
MODEL_SUMMARY_PATH = TABLES_DIR / "loop012_h3_model_summary.csv"
FIG_PATH = FIGURES_DIR / "loop012_h3_classchild_comparison.png"


def load_networth_labels() -> Dict[int, str]:
    """Map numeric net-worth codes to human-readable buckets."""

    cols = ["networth", "Your CURRENT net worth is closest to (nhoz8ia)"]
    df = pd.read_csv(DATA_PATH, usecols=cols, low_memory=False).dropna()
    mapping = (
        df.drop_duplicates()
        .assign(networth=lambda d: d["networth"].astype(int))
        .sort_values("networth")
        .set_index("networth")["Your CURRENT net worth is closest to (nhoz8ia)"]
        .to_dict()
    )
    return mapping


def build_classchild_table(labels: Dict[int, str]) -> pd.DataFrame:
    """Combine PPO threshold effects with multinomial marginal effects."""

    ppo = pd.read_csv(PPO_THRESHOLD_PATH)
    ppo = ppo[ppo["term"] == "classchild"].copy()
    ppo["spec"] = "partial_proportional_odds"
    ppo["effect_type"] = "cumulative_logit"
    ppo["label"] = ppo["cutpoint"].astype(int).map(labels)
    ppo["label"] = ">=" + ppo["label"].fillna(ppo["cutpoint"].astype(str))
    ppo = ppo.rename(
        columns={
            "cutpoint": "level",
            "effect": "estimate",
        }
    )

    multi = pd.read_csv(MULTI_MARGINAL_PATH)
    multi = multi[multi["term"] == "classchild"].copy()
    multi["spec"] = "multinomial_logit"
    multi["effect_type"] = "probability"
    multi["label"] = multi["outcome_level"].astype(int).map(labels)
    multi["label"] = multi["label"].fillna(multi["outcome_level"].astype(str))
    multi = multi.rename(
        columns={
            "outcome_level": "level",
            "dy_dx": "estimate",
        }
    )

    cols = [
        "spec",
        "effect_type",
        "level",
        "label",
        "estimate",
        "std_err",
        "ci_low",
        "ci_high",
        "p_value",
    ]
    combined = pd.concat([ppo[cols], multi[cols]], ignore_index=True)
    combined.sort_values(["spec", "level"], inplace=True)
    combined.to_csv(CLASS_EFFECTS_PATH, index=False)
    return combined


def build_model_summary() -> None:
    """Merge PPO and multinomial fit statistics for quick comparison."""

    def extract_metric(df: pd.DataFrame, metric: str) -> float | None:
        match = df.loc[df["metric"] == metric, "value"]
        return float(match.iloc[0]) if not match.empty else None

    rows: list[dict[str, object]] = []

    if PPO_FIT_PATH.exists():
        ppo_fit = pd.read_csv(PPO_FIT_PATH)
        ppo_params = pd.read_csv(PPO_PARAM_PATH)
        rows.append(
            {
                "model": "partial_proportional_odds",
                "log_likelihood": extract_metric(ppo_fit, "log_likelihood"),
                "aic": extract_metric(ppo_fit, "aic"),
                "bic": extract_metric(ppo_fit, "bic"),
                "pseudo_r2": extract_metric(ppo_fit, "pseudo_r2_mcfadden"),
                "n_individuals": extract_metric(ppo_fit, "n_individuals"),
                "n_effective_obs": extract_metric(ppo_fit, "n_long_rows"),
                "loglik_per_person": None,
                "loglik_per_effective_obs": None,
                "df_model": int(len(ppo_params)),
            }
        )
        if rows[-1]["log_likelihood"] is not None and rows[-1]["n_individuals"]:
            rows[-1]["loglik_per_person"] = rows[-1]["log_likelihood"] / rows[-1]["n_individuals"]
        if rows[-1]["log_likelihood"] is not None and rows[-1]["n_effective_obs"]:
            rows[-1]["loglik_per_effective_obs"] = rows[-1]["log_likelihood"] / rows[-1]["n_effective_obs"]

    if MULTI_FIT_PATH.exists():
        multi_fit = pd.read_csv(MULTI_FIT_PATH)
        df_model = extract_metric(multi_fit, "df_model")
        rows.append(
            {
                "model": "multinomial_logit",
                "log_likelihood": extract_metric(multi_fit, "log_likelihood"),
                "aic": extract_metric(multi_fit, "aic"),
                "bic": extract_metric(multi_fit, "bic"),
                "pseudo_r2": extract_metric(multi_fit, "pseudo_r2_mcfadden"),
                "n_individuals": extract_metric(multi_fit, "n_individuals"),
                "n_effective_obs": extract_metric(multi_fit, "n_individuals"),
                "loglik_per_person": None,
                "loglik_per_effective_obs": None,
                "df_model": int(df_model) if df_model is not None else None,
            }
        )
        if rows[-1]["log_likelihood"] is not None and rows[-1]["n_individuals"]:
            per = rows[-1]["log_likelihood"] / rows[-1]["n_individuals"]
            rows[-1]["loglik_per_person"] = per
            rows[-1]["loglik_per_effective_obs"] = per

    pd.DataFrame(rows).to_csv(MODEL_SUMMARY_PATH, index=False)


def make_figure(class_table: pd.DataFrame) -> None:
    """Plot PPO threshold effects and multinomial marginal effects."""

    fig, axes = plt.subplots(1, 2, figsize=(12, 4), constrained_layout=True)

    # Panel A: PPO cumulative effects
    ax = axes[0]
    ppo = class_table[class_table["spec"] == "partial_proportional_odds"].copy()
    ppo.sort_values("level", inplace=True)
    ax.plot(ppo["level"], ppo["estimate"], marker="o", color="#1b6ca8", label="PPO classchild slope")
    ax.fill_between(
        ppo["level"],
        ppo["ci_low"],
        ppo["ci_high"],
        color="#1b6ca8",
        alpha=0.2,
        linewidth=0,
    )
    ax.axhline(0, color="gray", linestyle="--", linewidth=0.8)
    ax.set_xticks(ppo["level"])
    ax.set_xticklabels(ppo["label"], rotation=35, ha="right")
    ax.set_ylabel("Log-odds effect of childhood class")
    ax.set_title("PPO cumulative logits (net worth ≥ threshold)")

    # Panel B: multinomial marginal effects on exact bins
    ax = axes[1]
    multi = class_table[class_table["spec"] == "multinomial_logit"].copy()
    multi.sort_values("level", inplace=True)
    ax.bar(multi["level"], multi["estimate"], color="#c7522a", width=0.6)
    ax.errorbar(
        multi["level"],
        multi["estimate"],
        yerr=[multi["estimate"] - multi["ci_low"], multi["ci_high"] - multi["estimate"]],
        fmt="none",
        ecolor="#333333",
        capsize=3,
        linewidth=1,
    )
    ax.axhline(0, color="gray", linestyle="--", linewidth=0.8)
    ax.set_xticks(multi["level"])
    ax.set_xticklabels(multi["label"], rotation=35, ha="right")
    ax.set_ylabel("Marginal ΔPr(net worth = bin)")
    ax.set_title("Multinomial marginal effects (exact wealth bins)")

    fig.suptitle("Childhood class effects: Partial proportional odds vs multinomial logit", fontsize=13)
    fig.savefig(FIG_PATH, dpi=300)
    plt.close(fig)


def main() -> None:
    labels = load_networth_labels()
    class_table = build_classchild_table(labels)
    build_model_summary()
    make_figure(class_table)


if __name__ == "__main__":
    main()
