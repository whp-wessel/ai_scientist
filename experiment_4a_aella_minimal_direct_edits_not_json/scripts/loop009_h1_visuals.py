#!/usr/bin/env python3
"""Generate manuscript-ready visuals for the H1 confirmatory contrasts."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import statsmodels.api as sm

from likert_utils import align_likert, ensure_columns, get_likert_specs, zscore

DATA_PATH = Path("childhoodbalancedpublic_original.csv")
TABLES_DIR = Path("tables")
FIGURES_DIR = Path("figures")
TABLES_DIR.mkdir(parents=True, exist_ok=True)
FIGURES_DIR.mkdir(parents=True, exist_ok=True)
FIGURE_PATH = FIGURES_DIR / "loop009_h1_confirmatory_interactions.png"
TABLE_PATH = TABLES_DIR / "loop009_h1_interaction_grid.csv"

CONTROL_COLUMNS: List[str] = [
    "classteen",
    "selfage",
    "gendermale",
    "education",
]


def add_aligned_columns(df: pd.DataFrame) -> pd.DataFrame:
    specs = get_likert_specs()
    ensure_columns(df, specs)
    aligned = align_likert(df, specs)
    for spec in specs:
        df[spec.aligned_column] = aligned[spec.aligned_column]
        df[spec.z_column] = zscore(aligned[spec.aligned_column])
    return df


def fit_ols(df: pd.DataFrame, outcome: str, predictors: Iterable[str]):
    cols = [outcome, *predictors]
    data = df[cols].dropna()
    X = sm.add_constant(data[predictors], has_constant="add")
    model = sm.OLS(data[outcome], X).fit()
    return model, data[predictors], len(data)


@dataclass
class ModeratorSpec:
    label: str
    value: float


def build_grid(
    model: sm.regression.linear_model.RegressionResultsWrapper,
    predictor_frame: pd.DataFrame,
    predictors: List[str],
    abuse_values: Iterable[float],
    moderator_column: str,
    interaction_column: str,
    moderator_specs: List[ModeratorSpec],
    descriptor: str,
    overrides: dict[str, float] | None = None,
) -> pd.DataFrame:
    base = predictor_frame.mean()
    rows: list[dict[str, float | str]] = []
    for abuse_val in abuse_values:
        for spec in moderator_specs:
            features = base.copy()
            features["abuse_child_z"] = abuse_val
            features[moderator_column] = spec.value
            features[interaction_column] = abuse_val * spec.value
            if overrides:
                for key, value in overrides.items():
                    features[key] = value

            pred_df = pd.DataFrame([features[predictors]])
            pred_exog = sm.add_constant(pred_df, has_constant="add")
            prediction = model.get_prediction(pred_exog)
            mean = float(prediction.predicted_mean.squeeze())
            ci_low, ci_high = prediction.conf_int(alpha=0.05)[0]
            rows.append(
                {
                    "interaction": descriptor,
                    "abuse_child_z": abuse_val,
                    "moderator_label": spec.label,
                    "moderator_value": spec.value,
                    "predicted_depression": mean,
                    "ci_low": float(ci_low),
                    "ci_high": float(ci_high),
                    "n_obs": int(model.nobs),
                }
            )
    return pd.DataFrame(rows)


def plot_interactions(guidance_df: pd.DataFrame, gender_df: pd.DataFrame) -> None:
    plt.style.use("seaborn-v0_8-whitegrid")
    figsize = (12, 4.5)
    fig, axes = plt.subplots(1, 2, figsize=figsize, sharey=True)

    for moderator, group in guidance_df.groupby("moderator_label"):
        group = group.sort_values("abuse_child_z")
        axes[0].plot(group["abuse_child_z"], group["predicted_depression"], label=moderator)
        axes[0].fill_between(
            group["abuse_child_z"],
            group["ci_low"],
            group["ci_high"],
            alpha=0.15,
        )
    axes[0].set_title("Guidance buffers abuse → depression")
    axes[0].set_xlabel("Childhood abuse (z)")
    axes[0].set_ylabel("Predicted depression (z)")

    for moderator, group in gender_df.groupby("moderator_label"):
        group = group.sort_values("abuse_child_z")
        axes[1].plot(group["abuse_child_z"], group["predicted_depression"], label=moderator)
        axes[1].fill_between(
            group["abuse_child_z"],
            group["ci_low"],
            group["ci_high"],
            alpha=0.15,
        )
    axes[1].set_title("Male vulnerability to childhood abuse")
    axes[1].set_xlabel("Childhood abuse (z)")

    axes[0].legend(title="Guidance level")
    axes[1].legend(title="Gender")
    fig.suptitle("H1 Confirmatory Interaction Effects (Loop 009)")
    fig.tight_layout(rect=(0, 0, 1, 0.96))
    fig.savefig(FIGURE_PATH, dpi=300, bbox_inches="tight")
    plt.close(fig)


def main() -> None:
    df = pd.read_csv(DATA_PATH, low_memory=False)
    add_aligned_columns(df)
    df["abuse_child_guidance_int"] = df["abuse_child_z"] * df["guidance_child_z"]
    df["abuse_child_male_int"] = df["abuse_child_z"] * df["gendermale"]

    guidance_predictors = [
        "abuse_child_z",
        "abuse_teen_z",
        "guidance_child_z",
        "abuse_child_guidance_int",
        *CONTROL_COLUMNS,
    ]
    guidance_model, guidance_frame, _ = fit_ols(df, "depression_z", guidance_predictors)

    gender_predictors = [
        "abuse_child_z",
        "abuse_teen_z",
        "abuse_child_male_int",
        *CONTROL_COLUMNS,
    ]
    gender_model, gender_frame, _ = fit_ols(df, "depression_z", gender_predictors)

    abuse_values = np.linspace(-2.5, 2.5, 21)
    guidance_specs = [
        ModeratorSpec(label="-1 SD guidance", value=-1.0),
        ModeratorSpec(label="mean guidance", value=0.0),
        ModeratorSpec(label="+1 SD guidance", value=1.0),
    ]
    gender_specs = [
        ModeratorSpec(label="Women (0)", value=0.0),
        ModeratorSpec(label="Men (1)", value=1.0),
    ]

    guidance_grid = build_grid(
        model=guidance_model,
        predictor_frame=guidance_frame,
        predictors=guidance_predictors,
        abuse_values=abuse_values,
        moderator_column="guidance_child_z",
        interaction_column="abuse_child_guidance_int",
        moderator_specs=guidance_specs,
        descriptor="guidance_buffering",
    )
    gender_grid = build_grid(
        model=gender_model,
        predictor_frame=gender_frame,
        predictors=gender_predictors,
        abuse_values=abuse_values,
        moderator_column="gendermale",
        interaction_column="abuse_child_male_int",
        moderator_specs=gender_specs,
        descriptor="male_vulnerability",
    )

    plot_interactions(guidance_grid, gender_grid)

    combined = pd.concat([guidance_grid, gender_grid], ignore_index=True)
    combined["model_id"] = combined["interaction"].map(
        {
            "guidance_buffering": "loop004_h1_guidance_interaction",
            "male_vulnerability": "loop004_h1_gender_interaction",
        }
    )
    combined.to_csv(TABLE_PATH, index=False)


if __name__ == "__main__":
    main()
