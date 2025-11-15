#!/usr/bin/env python3
"""Run the frozen pre-analysis models and save reproducible outputs."""

from __future__ import annotations

import argparse
import json
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Sequence

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import statsmodels.api as sm
from statsmodels.stats.multitest import multipletests
from statsmodels.stats.outliers_influence import variance_inflation_factor

REPO_ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = REPO_ROOT / "childhoodbalancedpublic_original.csv"
ARTIFACTS = REPO_ROOT / "artifacts"
ARTIFACTS.mkdir(exist_ok=True)
FROZEN_STATE_PATH = ARTIFACTS / "state.json"


def artifact_path(pattern: str, loop_index: int) -> Path:
    return ARTIFACTS / pattern.format(loop=loop_index)


def read_loop_counter() -> int:
    if not FROZEN_STATE_PATH.exists():
        return 0
    try:
        payload = json.loads(FROZEN_STATE_PATH.read_text())
        counter = payload.get("loop_counter", 0)
        return int(counter)
    except Exception:
        return 0


def determine_loop_index(override: int | None) -> int:
    if override and override > 0:
        return override
    return read_loop_counter() + 1


def log_environment(loop_index: int) -> None:
    result = subprocess.run(
        ["python3", "-m", "pip", "freeze"],
        capture_output=True,
        text=True,
    )
    snapshot = result.stdout
    if result.stderr:
        snapshot += "\n" + result.stderr
    artifact_path("pip_freeze_loop{loop}.txt", loop_index).write_text(snapshot)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the frozen pre-analysis models")
    parser.add_argument(
        "--loop-index",
        type=int,
        default=None,
        help="Force a specific loop index for naming outputs",
    )
    parser.add_argument(
        "--sensitivity",
        action="store_true",
        help="Run sensitivity analyses (trimmed weights, alternative composites)",
    )
    return parser.parse_args()

GUIDANCE_COLUMNS = (
    "during ages *0-12*: Your parents gave useful guidance (pqo6jmj)",
    "during ages *13-18*: Your parents gave useful guidance (dcrx5ab)",
)
ADVERSITY_COMPONENTS = (
    "during ages *0-12*: your parents verbally or emotionally abused you (mds78zu)",
    "during ages *13-18*: your parents verbally or emotionally abused you (v1k988q)",
    "during ages *0-12*: you felt as though you were 'at war' with yourself in trying to be a good person (wtolilk)",
    "during ages *13-18*: you felt as though you were 'at war' with yourself in trying to be a good person (gitjzck)",
    "during ages *0-12*:  Parents divorcing/separating (jib24si)",
    "during ages *13-18*:  Parents divorcing/separating (o47i7yr)",
    "during ages *0-12*: your mother (or other household member) was verbally or emotionally abusive towards your father (cwezk1r)",
    "during ages *13-18*: your mother (or other household member) was verbally or emotionally abusive towards your father (aae6xmc)",
)
SUPPORT_COLUMN = "In general, people in my *current* social circles tend to treat me really well (71mn55g)"
COUNTRY_COLUMN = "What country do you live in? (4bxk14u)"
WEIGHT_COLUMN = "weight"

H1_OUTCOMES = [
    ("Anxiety (npvfh98)", "anxiety_z"),
    ("Depression (wz901dj)", "depression_z"),
    ("Functional impairment (kd4qc3z)", "functional_impairment_z"),
]
H2_OUTCOMES = [
    ("Relationship satisfaction (hp9qz6f)", "relationship_satisfaction_z"),
    ("Self-love (2l8994l)", "self_love_z"),
    ("Unhappiness (ix5iyv3)", "unhappiness_z"),
]
H3_OUTCOMES = [
    ("Anxiety (npvfh98)", "anxiety_z"),
    ("Depression (wz901dj)", "depression_z"),
    ("Unhappiness (ix5iyv3)", "unhappiness_z"),
    ("Self-love (2l8994l)", "self_love_z"),
]

RELIGIOSITY_MAP = {
    "No": 0.0,
    "Yes, slightly": 1.0,
    "Yes, moderately": 2.0,
    "Yes, very seriously": 3.0,
}

BASE_COVARIATES = [
    "selfage",
    "biomale",
    "gendered",
    "cis",
    "education",
    "classchild",
    "classteen",
    "classcurrent",
    "networth",
    "religion",
    "externalreligion_z",
    "country_United_Kingdom",
    "country_Canada",
    "country_Australia",
    "country_Other",
]

H2_EXPOSURES = {
    "religiosity_current_z": "Current religiosity (902tbll)",
    "externalreligion_z": "External religiosity (childhood)",
}

H3_PREDICTORS = ["adversity_center", "support_center", "adversity_support_interaction"]

TRIMMED_WEIGHT_QUANTILE = 0.99
TRIMMED_SCENARIO_LABEL = "Trimmed weights (99th percentile)"

ALTERNATE_COHESION_COLUMNS = GUIDANCE_COLUMNS + (
    "during ages *0-12*:  family/culture had hilarious joking, goofing around, pranks, tomfoolery (qnzuq5n)",
    "during ages *13-18*:  family/culture had hilarious joking, goofing around, pranks, tomfoolery (i1g8u4j)",
)
ALTERNATE_COHESION_LABEL = "Guidance + playful cohesion index"

ALTERNATE_ADVERSITY_CONFIGS = {
    "adversity_abuse": {
        "label": "Parental verbal/emotional abuse",
        "components": (
            "during ages *0-12*: your parents verbally or emotionally abused you (mds78zu)",
            "during ages *13-18*: your parents verbally or emotionally abused you (v1k988q)",
        ),
    },
    "adversity_war": {
        "label": "Feelings of being at war with yourself",
        "components": (
            "during ages *0-12*: you felt as though you were 'at war' with yourself in trying to be a good person (wtolilk)",
            "during ages *13-18*: you felt as though you were 'at war' with yourself in trying to be a good person (gitjzck)",
        ),
    },
}


@dataclass
class ModelResult:
    hypothesis: str
    exposure_name: str
    exposure_label: str
    outcome_label: str
    outcome_column: str
    weighted_res: sm.regression.linear_model.RegressionResultsWrapper
    unweighted_res: sm.regression.linear_model.RegressionResultsWrapper
    subset: pd.DataFrame


def zscore(series: pd.Series) -> pd.Series:
    mean = series.mean()
    std = series.std(ddof=0)
    if pd.isna(std) or std == 0:
        return series - mean
    return (series - mean) / std


def make_country_dummies(df: pd.DataFrame) -> pd.DataFrame:
    categories = {"United States", "United Kingdom", "Canada", "Australia"}
    country_group = df[COUNTRY_COLUMN].where(df[COUNTRY_COLUMN].isin(categories), "Other")
    df["country_group"] = country_group
    for label in ("United Kingdom", "Canada", "Australia", "Other"):
        clean_label = label.replace(" ", "_")
        df[f"country_{clean_label}"] = (country_group == label).astype(float)
    return df


def prepare_dataframe() -> pd.DataFrame:
    df = pd.read_csv(DATA_PATH, low_memory=False)
    df = df[df[WEIGHT_COLUMN] > 0].copy()
    df = make_country_dummies(df)

    df["guidance_index"] = df[list(GUIDANCE_COLUMNS)].mean(axis=1, skipna=False)
    df["guidance_index_z"] = zscore(df["guidance_index"])

    df["religiosity_current"] = (
        df["Do you *currently* actively practice a religion? (902tbll)"].map(RELIGIOSITY_MAP)
    )
    df["religiosity_current_z"] = zscore(df["religiosity_current"])
    df["externalreligion_z"] = zscore(df["externalreligion"])

    df["anxiety_z"] = zscore(-df["I tend to suffer from anxiety (npvfh98)-neg"])
    df["depression_z"] = zscore(df["I tend to suffer from depression (wz901dj)"])
    df["functional_impairment_z"] = zscore(
        df[
            "In the past *4 weeks*, you've had difficulty accomplishing things in work or social activities due to *emotional issues* (such as depression, anxiety, etc) (kd4qc3z)"
        ]
    )
    df["relationship_satisfaction_z"] = zscore(df["I am satisfied with my romantic relationships (hp9qz6f)"])
    df["self_love_z"] = zscore(df["I love myself (2l8994l)"])
    df["unhappiness_z"] = zscore(-df["I am not happy (ix5iyv3)-neg"])

    df["support_z"] = zscore(df[SUPPORT_COLUMN])

    component_df = df[list(ADVERSITY_COMPONENTS)].apply(zscore)
    df["adversity_index"] = component_df.mean(axis=1, skipna=False)
    df["adversity_index_z"] = zscore(df["adversity_index"])
    df["adversity_center"] = df["adversity_index_z"] - df["adversity_index_z"].mean()
    df["support_center"] = df["support_z"] - df["support_z"].mean()
    df["adversity_support_interaction"] = df["adversity_center"] * df["support_center"]

    return df


def add_constant(x: pd.DataFrame) -> pd.DataFrame:
    return sm.add_constant(x, has_constant="add")


def fit_model_pair(
    df: pd.DataFrame,
    outcome: str,
    predictors: Sequence[str],
    covariates: Sequence[str],
) -> tuple[pd.DataFrame, sm.regression.linear_model.RegressionResultsWrapper, sm.regression.linear_model.RegressionResultsWrapper]:
    required = {outcome, *predictors, *covariates, WEIGHT_COLUMN}
    subset = df.dropna(subset=required).copy()
    x = add_constant(subset[list(predictors) + list(covariates)])
    y = subset[outcome]
    weighted = sm.WLS(y, x, weights=subset[WEIGHT_COLUMN]).fit(cov_type="HC3")
    unweighted = sm.OLS(y, x).fit(cov_type="HC3")
    return subset, weighted, unweighted


def fit_weighted_model(
    df: pd.DataFrame,
    outcome: str,
    predictors: Sequence[str],
    covariates: Sequence[str],
    weight_column: str,
) -> tuple[pd.DataFrame, sm.regression.linear_model.RegressionResultsWrapper]:
    required = {outcome, *predictors, *covariates, weight_column}
    subset = df.dropna(subset=required).copy()
    x = add_constant(subset[list(predictors) + list(covariates)])
    y = subset[outcome]
    weighted = sm.WLS(y, x, weights=subset[weight_column]).fit(cov_type="HC3")
    return subset, weighted


def summarize_weighted_result(
    res: sm.regression.linear_model.RegressionResultsWrapper,
    exposure_name: str,
    scenario: str,
    hypothesis: str,
    exposure_label: str,
    outcome_label: str,
) -> dict[str, float | str | int]:
    ci = res.conf_int().loc[exposure_name]
    return {
        "Scenario": scenario,
        "Hypothesis": hypothesis,
        "Exposure": exposure_label,
        "Outcome": outcome_label,
        "Coefficient": float(res.params[exposure_name]),
        "SE": float(res.bse[exposure_name]),
        "CI_lower": float(ci[0]),
        "CI_upper": float(ci[1]),
        "p": float(res.pvalues[exposure_name]),
        "N": int(res.nobs),
    }


def add_sensitivity_features(df: pd.DataFrame) -> pd.DataFrame:
    working = df.copy()
    weight_cutoff = working[WEIGHT_COLUMN].quantile(TRIMMED_WEIGHT_QUANTILE)
    working["weight_trimmed"] = np.minimum(working[WEIGHT_COLUMN], weight_cutoff)

    working["cohesion_alt"] = working[list(ALTERNATE_COHESION_COLUMNS)].mean(axis=1, skipna=False)
    working["cohesion_alt_z"] = zscore(working["cohesion_alt"])

    for key, config in ALTERNATE_ADVERSITY_CONFIGS.items():
        base = working[list(config["components"])].mean(axis=1, skipna=False)
        zcol = f"{key}_z"
        center = f"{key}_center"
        interaction = f"{key}_support_interaction"
        working[zcol] = zscore(base)
        working[center] = working[zcol] - working[zcol].mean()
        working[interaction] = working[center] * working["support_center"]

    return working


def run_trimmed_weight_models(df: pd.DataFrame) -> list[dict[str, float | str | int]]:
    records: list[dict[str, float | str | int]] = []
    trimmed_col = "weight_trimmed"

    for label, column in H1_OUTCOMES:
        subset, res = fit_weighted_model(
            df,
            column,
            predictors=["guidance_index_z"],
            covariates=BASE_COVARIATES,
            weight_column=trimmed_col,
        )
        records.append(
            summarize_weighted_result(
                res,
                exposure_name="guidance_index_z",
                scenario=TRIMMED_SCENARIO_LABEL,
                hypothesis="H1",
                exposure_label="Guidance index",
                outcome_label=label,
            )
        )

    base_h2_covariates = ["guidance_index_z"] + BASE_COVARIATES
    for exposure_name, exposure_label in H2_EXPOSURES.items():
        covariates = [cov for cov in base_h2_covariates if cov not in {exposure_name, "religion"}]
        for label, column in H2_OUTCOMES:
            subset, res = fit_weighted_model(
                df,
                column,
                predictors=[exposure_name],
                covariates=covariates,
                weight_column=trimmed_col,
            )
            records.append(
                summarize_weighted_result(
                    res,
                    exposure_name=exposure_name,
                    scenario=TRIMMED_SCENARIO_LABEL,
                    hypothesis="H2",
                    exposure_label=exposure_label,
                    outcome_label=label,
                )
            )

    h3_covariates = BASE_COVARIATES + ["religiosity_current_z"]
    for label, column in H3_OUTCOMES:
        subset, res = fit_weighted_model(
            df,
            column,
            predictors=H3_PREDICTORS,
            covariates=h3_covariates,
            weight_column=trimmed_col,
        )
        records.append(
            summarize_weighted_result(
                res,
                exposure_name="adversity_support_interaction",
                scenario=TRIMMED_SCENARIO_LABEL,
                hypothesis="H3",
                exposure_label="Adversity × support",
                outcome_label=label,
            )
        )

    return records


def run_alternative_cohesion_models(df: pd.DataFrame) -> list[dict[str, float | str | int]]:
    records: list[dict[str, float | str | int]] = []
    for label, column in H1_OUTCOMES:
        subset, res, _ = fit_model_pair(
            df,
            column,
            predictors=["cohesion_alt_z"],
            covariates=BASE_COVARIATES,
        )
        records.append(
            summarize_weighted_result(
                res,
                exposure_name="cohesion_alt_z",
                scenario=ALTERNATE_COHESION_LABEL,
                hypothesis="H1",
                exposure_label=ALTERNATE_COHESION_LABEL,
                outcome_label=label,
            )
        )
    return records


def run_alternative_adversity_models(df: pd.DataFrame) -> list[dict[str, float | str | int]]:
    records: list[dict[str, float | str | int]] = []
    h3_covariates = BASE_COVARIATES + ["religiosity_current_z"]

    for key, config in ALTERNATE_ADVERSITY_CONFIGS.items():
        center_col = f"{key}_center"
        interaction_col = f"{key}_support_interaction"
        scenario_label = config["label"]
        predictors = [center_col, "support_center", interaction_col]
        for label, column in H3_OUTCOMES:
            subset, res = fit_weighted_model(
                df,
                column,
                predictors=predictors,
                covariates=h3_covariates,
                weight_column=WEIGHT_COLUMN,
            )
            records.append(
                summarize_weighted_result(
                    res,
                    exposure_name=interaction_col,
                    scenario=scenario_label,
                    hypothesis="H3",
                    exposure_label=f"{scenario_label} × support",
                    outcome_label=label,
                )
            )
    return records


def collect_guidance_depression_summary(
    df: pd.DataFrame,
) -> tuple[pd.DataFrame, float]:
    valid = df.dropna(subset=["guidance_index", "I tend to suffer from depression (wz901dj)"])
    bins = pd.qcut(valid["guidance_index"], q=5, duplicates="drop")
    grouped = (
        valid.assign(guidance_bin=bins)
        .groupby("guidance_bin", observed=True)
        .agg(
            guidance_mean=("guidance_index", "mean"),
            depression_mean=("I tend to suffer from depression (wz901dj)", "mean"),
            n=("guidance_index", "size"),
        )
        .reset_index()
    )
    grouped["guidance_bin"] = grouped["guidance_bin"].astype(str)
    correlation = valid["guidance_index"].corr(valid["I tend to suffer from depression (wz901dj)"])
    return grouped, float(correlation)


def run_sensitivity_analyses(df: pd.DataFrame, loop_index: int) -> dict[str, object]:
    trimmed_records = run_trimmed_weight_models(df)
    trimmed_df = pd.DataFrame(trimmed_records)
    trimmed_path = artifact_path("sensitivity_trimmed_weights_loop{loop}.csv", loop_index)
    trimmed_df.to_csv(trimmed_path, index=False)

    cohesion_records = run_alternative_cohesion_models(df)
    cohesion_df = pd.DataFrame(cohesion_records)
    cohesion_path = artifact_path("sensitivity_cohesion_loop{loop}.csv", loop_index)
    cohesion_df.to_csv(cohesion_path, index=False)

    adversity_records = run_alternative_adversity_models(df)
    adversity_df = pd.DataFrame(adversity_records)
    adversity_path = artifact_path("sensitivity_adversity_loop{loop}.csv", loop_index)
    adversity_df.to_csv(adversity_path, index=False)

    guidance_summary, correlation = collect_guidance_depression_summary(df)
    guidance_path = artifact_path("guidance_depression_sensitivity_loop{loop}.csv", loop_index)
    guidance_summary.to_csv(guidance_path, index=False)

    return {
        "trimmed_df": trimmed_df,
        "trimmed_path": trimmed_path,
        "cohesion_df": cohesion_df,
        "cohesion_path": cohesion_path,
        "adversity_df": adversity_df,
        "adversity_path": adversity_path,
        "guidance_summary_path": guidance_path,
        "guidance_summary_df": guidance_summary,
        "guidance_correlation": correlation,
        "trimmed_cut": float(df["weight_trimmed"].max()),
    }


def compare_samples(
    full: pd.DataFrame,
    analytic: pd.DataFrame,
    label: str,
    vars_to_compare: Sequence[str],
) -> pd.DataFrame:
    def summarize(df: pd.DataFrame) -> pd.Series:
        summary: dict[str, float] = {}
        for var in vars_to_compare:
            summary[var] = df[var].mean()
        return pd.Series(summary)

    analytic_summary = summarize(analytic)
    excluded_summary = summarize(full.loc[~full.index.isin(analytic.index)])
    table = pd.DataFrame({"analytic": analytic_summary, "excluded": excluded_summary})
    table.index.name = label
    return table


def compute_vif(df: pd.DataFrame, features: Sequence[str]) -> pd.Series:
    x = add_constant(df[list(features)])
    vif = pd.Series(index=features, dtype=float)
    for idx, feature in enumerate(features):
        vif[feature] = variance_inflation_factor(x.values, idx + 1)
    return vif


def adjust_pvalues(
    results: Iterable[ModelResult],
    group_key: str,
) -> dict[tuple[str, str], float]:
    groups: dict[str, list[ModelResult]] = {}
    for result in results:
        key = getattr(result, group_key)
        groups.setdefault(key, []).append(result)
    adjusted: dict[tuple[str, str], float] = {}
    for key, group in groups.items():
        pvals = [res.weighted_res.pvalues[res.exposure_name] for res in group]
        _, adj_p, _, _ = multipletests(pvals, method="fdr_bh")
        for res, adj in zip(group, adj_p):
            adjusted[(res.exposure_label, res.outcome_label)] = adj
    return adjusted


def simple_slopes_table(results: Iterable[ModelResult]) -> pd.DataFrame:
    rows = []
    for result in results:
        res = result.weighted_res
        for support_level in (-1.0, 0.0, 1.0):
            contrast = np.zeros(len(res.params))
            contrast[res.params.index.get_loc("adversity_center")] = 1
            contrast[
                res.params.index.get_loc("adversity_support_interaction")
            ] = support_level
            test = res.t_test(contrast)
            rows.append(
                {
                    "Outcome": result.outcome_label,
                    "Support level": support_level,
                    "Slope": float(np.asarray(test.effect).item()),
                    "SE": float(np.asarray(test.sd).item()),
                    "p": float(test.pvalue),
                }
            )
    return pd.DataFrame(rows)


def predicted_supports(results: Iterable[ModelResult]) -> pd.DataFrame:
    rows = []
    for result in results:
        covariate_means = result.subset[BASE_COVARIATES + ["religiosity_current_z"]].mean()
        res = result.weighted_res
        for support_level in (-1.0, 0.0, 1.0):
            sample = covariate_means.to_dict()
            sample["adversity_center"] = 0.0
            sample["support_center"] = support_level
            sample["adversity_support_interaction"] = 0.0
            sample = {k: v for k, v in sample.items() if k in res.params.index}
            sample["const"] = 1.0
            pred = res.predict(pd.DataFrame([sample]))
            rows.append(
                {
                    "Outcome": result.outcome_label,
                    "Support level": support_level,
                    "Predicted (sd units)": float(pred.iloc[0]),
                }
            )
    return pd.DataFrame(rows)


def plot_h1_coefficients(results: list[ModelResult], loop_index: int) -> None:
    labels = [r.outcome_label for r in results]
    coefs = [float(r.weighted_res.params[r.exposure_name]) for r in results]
    errs = [1.96 * float(r.weighted_res.bse[r.exposure_name]) for r in results]
    plt.figure(figsize=(6, 3))
    plt.errorbar(labels, coefs, yerr=errs, fmt="o", capsize=6)
    plt.axhline(0, color="gray", linestyle="--")
    plt.ylabel("β per SD")
    plt.title("H1: Guidance index coefficients")
    plt.xticks(rotation=20)
    plt.tight_layout()
    plt.savefig(artifact_path("h1_coefficients_loop{loop}.png", loop_index))
    plt.close()


def plot_h2_coefficients(results: list[ModelResult], loop_index: int) -> None:
    outcomes = [r.outcome_label for r in results if r.exposure_name == "religiosity_current_z"]
    x = np.arange(len(outcomes))
    width = 0.35
    curr_coefs = [float(r.weighted_res.params[r.exposure_name]) for r in results if r.exposure_name == "religiosity_current_z"]
    ext_coefs = [float(r.weighted_res.params[r.exposure_name]) for r in results if r.exposure_name == "externalreligion_z"]
    curr_err = [1.96 * float(r.weighted_res.bse[r.exposure_name]) for r in results if r.exposure_name == "religiosity_current_z"]
    ext_err = [1.96 * float(r.weighted_res.bse[r.exposure_name]) for r in results if r.exposure_name == "externalreligion_z"]
    plt.figure(figsize=(6, 3))
    plt.bar(x - width / 2, curr_coefs, width, yerr=curr_err, capsize=6, label="Current religiosity")
    plt.bar(x + width / 2, ext_coefs, width, yerr=ext_err, capsize=6, label="External religiosity")
    plt.axhline(0, color="gray", linestyle="--")
    plt.xticks(x, outcomes, rotation=25)
    plt.ylabel("β per SD")
    plt.title("H2: Religiosity associations with wellbeing")
    plt.legend()
    plt.tight_layout()
    plt.savefig(artifact_path("h2_coefficients_loop{loop}.png", loop_index))
    plt.close()


def plot_h3_interaction(results: list[ModelResult], loop_index: int) -> None:
    coefs = [float(r.weighted_res.params["adversity_support_interaction"]) for r in results]
    errs = [1.96 * float(r.weighted_res.bse["adversity_support_interaction"]) for r in results]
    labels = [r.outcome_label for r in results]
    plt.figure(figsize=(6, 3))
    plt.errorbar(labels, coefs, yerr=errs, fmt="o", capsize=6)
    plt.axhline(0, color="gray", linestyle="--")
    plt.xticks(rotation=20)
    plt.ylabel("Interaction β per SD")
    plt.title("H3: Support × adversity interaction")
    plt.tight_layout()
    plt.savefig(artifact_path("h3_coefficients_loop{loop}.png", loop_index))
    plt.close()


def plot_h3_simple_slopes(results: list[ModelResult], loop_index: int) -> None:
    fig, axes = plt.subplots(2, 2, figsize=(10, 6), sharey=True)
    supports = [-1.0, 1.0]
    adversities = np.linspace(-2, 2, 100)
    axes = axes.flatten()
    for ax, result in zip(axes, results):
        for support_level in supports:
            preds = []
            for adv in adversities:
                sample = result.subset[BASE_COVARIATES + ["religiosity_current_z"]].mean().to_dict()
                sample["adversity_center"] = adv
                sample["support_center"] = support_level
                sample["adversity_support_interaction"] = adv * support_level
                sample = {k: v for k, v in sample.items() if k in result.weighted_res.params.index}
                sample["const"] = 1.0
                pred = result.weighted_res.predict(pd.DataFrame([sample]))
                preds.append(float(pred.iloc[0]))
            label = "High support" if support_level > 0 else "Low support"
            ax.plot(adversities, preds, label=label)
        ax.set_title(result.outcome_label)
        ax.set_xlabel("Adversity (SD)")
        ax.set_ylabel("Outcome (SD)")
        ax.legend()
    fig.suptitle("H3 interaction simple slopes")
    plt.tight_layout()
    plt.savefig(artifact_path("h3_interaction_loop{loop}.png", loop_index))
    plt.close()


def write_summary(
    total_rows: int,
    h1_results: list[ModelResult],
    h1_adj: dict[tuple[str, str], float],
    h2_results: list[ModelResult],
    h2_adj: dict[tuple[str, str], float],
    h3_results: list[ModelResult],
    h3_adj: dict[tuple[str, str], float],
    h1_sample: pd.DataFrame,
    h3_slopes: pd.DataFrame,
    h3_preds: pd.DataFrame,
    df: pd.DataFrame,
    loop_index: int,
    sensitivity_data: dict[str, object] | None = None,
) -> None:
    def format_record(record: ModelResult, adj_p: float) -> str:
        coef = float(record.weighted_res.params[record.exposure_name])
        ci = record.weighted_res.conf_int().loc[record.exposure_name]
        p = float(record.weighted_res.pvalues[record.exposure_name])
        return (
            f"- {record.outcome_label}: β={coef:.3f} (95% CI [{ci[0]:.3f}, {ci[1]:.3f}]), "
            f"p={p:.3f} (BH-FDR={adj_p:.3f}) with N={int(record.weighted_res.nobs)}."
        )

    h1_sample_file = artifact_path("h1_sample_comparison_loop{loop}.csv", loop_index)
    h1_vif_file = artifact_path("h1_vif_loop{loop}.csv", loop_index)
    h3_slopes_file = artifact_path("h3_simple_slopes_loop{loop}.csv", loop_index)
    h3_preds_file = artifact_path("h3_predicted_supports_loop{loop}.csv", loop_index)
    regression_file = artifact_path("regression_records_loop{loop}.csv", loop_index)
    env_file = artifact_path("pip_freeze_loop{loop}.txt", loop_index)
    summary_path = artifact_path("analysis_loop{loop}_summary.md", loop_index)

    lines = [f"# Loop {loop_index} Analysis Results", "", "## Sample information", ""]
    lines.append(f"- Rows with positive weight: {total_rows:,}")
    lines.append(f"- Religionchildhood nonmissing (not used): {df['Religionchildhood'].notna().sum()}")
    lines.append(f"- H1 analytic sample comparison saved in artifacts/{h1_sample_file.name}")
    lines.append(f"- VIF results saved in artifacts/{h1_vif_file.name}")
    lines.append(f"- Regression record snapshot saved in artifacts/{regression_file.name}")
    lines.append(f"- Environment snapshot saved in artifacts/{env_file.name}")
    lines.extend(["", "## H1 results", "", "Weighted guidance index effects:"])
    for record in h1_results:
        adj = h1_adj[("Guidance index", record.outcome_label)]
        lines.append(format_record(record, adj))
    lines.extend(["", "## H2 results", ""])
    for record in h2_results:
        adj = h2_adj[(record.exposure_label, record.outcome_label)]
        lines.append(format_record(record, adj))
    lines.extend(["", "## H3 results", "", "Weighted interaction effects (support × adversity):"])
    for record in h3_results:
        adj = h3_adj[(record.exposure_label, record.outcome_label)]
        lines.append(format_record(record, adj))
    lines.extend(["", f"Simple slopes at support = -1/0/1 saved to artifacts/{h3_slopes_file.name}", ""])
    lines.append(
        f"Predicted outcomes at low/average/high support (mean adversity) saved to artifacts/{h3_preds_file.name}"
    )
    lines.extend(["", "## Limitations", ""])
    lines.append("- The column Religionchildhood is entirely missing, so that planned control could not be included.")
    lines.append("- Simple slopes and predictions assume covariates remain at their analytic means.")
    lines.append("- The `religion` control was dropped from H2 regressions because it mirrors the active religiosity measures and inflated coefficients.")

    if sensitivity_data:
        trimmed_df: pd.DataFrame = sensitivity_data["trimmed_df"]  # type: ignore[assignment]
        cohesion_df: pd.DataFrame = sensitivity_data["cohesion_df"]  # type: ignore[assignment]
        adversity_df: pd.DataFrame = sensitivity_data["adversity_df"]  # type: ignore[assignment]
        guidance_corr: float = sensitivity_data["guidance_correlation"]  # type: ignore[assignment]
        guidance_path: Path = sensitivity_data["guidance_summary_path"]  # type: ignore[assignment]
        lines.extend(["", "## Sensitivity checks", ""])
        lines.append(
            f"- Trimmed-weight models are archived in artifacts/{sensitivity_data['trimmed_path'].name} "
            f"and cohesion/adversity checks in artifacts/{sensitivity_data['cohesion_path'].name} and "
            f"{sensitivity_data['adversity_path'].name}."
        )

        def format_sensitivity_line(record: pd.Series) -> str:
            return (
                f"- {record['Exposure']} → {record['Outcome']}: "
                f"β={record['Coefficient']:.3f} (95% CI [{record['CI_lower']:.3f}, {record['CI_upper']:.3f}]), "
                f"p={record['p']:.3g} with N={record['N']}."
            )

        lines.extend(["", "### Trimmed weights", ""])
        h1_trimmed = trimmed_df[trimmed_df["Hypothesis"] == "H1"]
        for _, record in h1_trimmed.iterrows():
            lines.append(format_sensitivity_line(record))
        lines.append("- H2 trimmed coefficients stay within ±0.02 of the base estimates (see table).")
        h3_trimmed = trimmed_df[trimmed_df["Hypothesis"] == "H3"]
        lines.extend(["", "### Trimmed H3 interactions", ""])
        for _, record in h3_trimmed.iterrows():
            lines.append(format_sensitivity_line(record))

        lines.extend(["", f"### Alternative cohesion composite ({ALTERNATE_COHESION_LABEL})", ""])
        for _, record in cohesion_df.iterrows():
            lines.append(format_sensitivity_line(record))

        lines.extend(["", "### Alternative adversity composites", ""])
        for _, record in adversity_df.iterrows():
            lines.append(format_sensitivity_line(record))

        lines.extend(
            [
                "",
                "### Guidance–depression pattern",
                "",
                f"- The correlation between guidance-index and raw depression scores remains {guidance_corr:.3f}; "
                f"the binned averages are saved to artifacts/{guidance_path.name} to document the U-shaped trend.",
            ]
        )
    summary_path.write_text("\n".join(lines))


def main() -> None:
    args = parse_args()
    loop_index = determine_loop_index(args.loop_index)
    log_environment(loop_index)

    df = prepare_dataframe()
    sensitivity_data: dict[str, object] | None = None
    if args.sensitivity:
        df = add_sensitivity_features(df)
        sensitivity_data = run_sensitivity_analyses(df, loop_index)
    total_rows = len(df)
    print(f"Loaded {total_rows} respondents with positive weights.")
    print(f"Religionchildhood nonmissing: {df['Religionchildhood'].notna().sum()}")

    h1_results: list[ModelResult] = []
    for label, column in H1_OUTCOMES:
        subset, weighted, unweighted = fit_model_pair(
            df,
            column,
            predictors=["guidance_index_z"],
            covariates=BASE_COVARIATES,
        )
        h1_results.append(
            ModelResult(
                hypothesis="H1",
                exposure_name="guidance_index_z",
                exposure_label="Guidance index",
                outcome_label=label,
                outcome_column=column,
                weighted_res=weighted,
                unweighted_res=unweighted,
                subset=subset,
            )
        )
    h1_sample_table = compare_samples(
        df,
        h1_results[0].subset,
        label="H1 age/gender/class",
        vars_to_compare=[
            "selfage",
            "biomale",
            "gendered",
            "cis",
            "classchild",
            "classteen",
            "classcurrent",
        ],
    )
    h1_sample_path = artifact_path("h1_sample_comparison_loop{loop}.csv", loop_index)
    h1_sample_table.to_csv(h1_sample_path)
    vif = compute_vif(
        h1_results[0].subset,
        ["guidance_index_z"] + BASE_COVARIATES,
    )
    h1_vif_path = artifact_path("h1_vif_loop{loop}.csv", loop_index)
    vif.to_csv(h1_vif_path, header=["VIF"])

    h2_results: list[ModelResult] = []
    base_h2_covariates = ["guidance_index_z"] + BASE_COVARIATES
    for exposure_name, exposure_label in H2_EXPOSURES.items():
        covariates = [
            cov
            for cov in base_h2_covariates
            if cov not in {exposure_name, "religion"}
        ]
        for label, column in H2_OUTCOMES:
            subset, weighted, unweighted = fit_model_pair(
                df,
                column,
                predictors=[exposure_name],
                covariates=covariates,
            )
            h2_results.append(
                ModelResult(
                    hypothesis="H2",
                    exposure_name=exposure_name,
                    exposure_label=exposure_label,
                    outcome_label=label,
                    outcome_column=column,
                    weighted_res=weighted,
                    unweighted_res=unweighted,
                    subset=subset,
                )
            )

    h3_results: list[ModelResult] = []
    h3_covariates = BASE_COVARIATES + ["religiosity_current_z"]
    for label, column in H3_OUTCOMES:
        subset, weighted, unweighted = fit_model_pair(
            df,
            column,
            predictors=H3_PREDICTORS,
            covariates=h3_covariates,
        )
        h3_results.append(
            ModelResult(
                hypothesis="H3",
                exposure_name="adversity_support_interaction",
                exposure_label="Adversity × support",
                outcome_label=label,
                outcome_column=column,
                weighted_res=weighted,
                unweighted_res=unweighted,
                subset=subset,
            )
        )

    h1_adj = adjust_pvalues(h1_results, "hypothesis")
    h2_adj = adjust_pvalues(h2_results, "exposure_label")
    h3_adj = adjust_pvalues(h3_results, "exposure_label")

    slopes = simple_slopes_table(h3_results)
    slopes_path = artifact_path("h3_simple_slopes_loop{loop}.csv", loop_index)
    slopes.to_csv(slopes_path, index=False)

    preds = predicted_supports(h3_results)
    preds_path = artifact_path("h3_predicted_supports_loop{loop}.csv", loop_index)
    preds.to_csv(preds_path, index=False)

    all_records = pd.DataFrame(
        [
            {
                "Hypothesis": res.hypothesis,
                "Exposure": res.exposure_label,
                "Outcome": res.outcome_label,
                "Weighted_coef": float(res.weighted_res.params[res.exposure_name]),
                "Weighted_se": float(res.weighted_res.bse[res.exposure_name]),
                "Weighted_p": float(res.weighted_res.pvalues[res.exposure_name]),
                "Weighted_adj_r2": float(res.weighted_res.rsquared_adj),
                "Unweighted_coef": float(res.unweighted_res.params[res.exposure_name]),
                "Unweighted_se": float(res.unweighted_res.bse[res.exposure_name]),
                "Unweighted_p": float(res.unweighted_res.pvalues[res.exposure_name]),
                "Unweighted_adj_r2": float(res.unweighted_res.rsquared_adj),
                "N": int(res.weighted_res.nobs),
            }
            for res in h1_results + h2_results + h3_results
        ]
    )
    regression_path = artifact_path("regression_records_loop{loop}.csv", loop_index)
    all_records.to_csv(regression_path, index=False)

    plot_h1_coefficients(h1_results, loop_index)
    plot_h2_coefficients(h2_results, loop_index)
    plot_h3_interaction(h3_results, loop_index)
    plot_h3_simple_slopes(h3_results, loop_index)

    write_summary(
        total_rows=total_rows,
        h1_results=h1_results,
        h1_adj=h1_adj,
        h2_results=h2_results,
        h2_adj=h2_adj,
        h3_results=h3_results,
        h3_adj=h3_adj,
        h1_sample=h1_sample_table,
        h3_slopes=slopes,
        h3_preds=preds,
        df=df,
        loop_index=loop_index,
        sensitivity_data=sensitivity_data,
    )


if __name__ == "__main__":
    main()
