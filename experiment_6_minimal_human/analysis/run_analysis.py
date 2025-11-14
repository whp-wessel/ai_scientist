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
    summary_path.write_text("\n".join(lines))


def main() -> None:
    args = parse_args()
    loop_index = determine_loop_index(args.loop_index)
    log_environment(loop_index)

    df = prepare_dataframe()
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
    )


if __name__ == "__main__":
    main()
