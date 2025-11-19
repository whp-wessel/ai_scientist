"""Produce pre-registered sensitivity results for the purity-culture project."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Iterable, List

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
TABLES_DIR = ROOT / "tables"
OUTPUT_SUMMARY = ROOT / "outputs" / "sensitivity_overview.json"

RELIGION_INTERACTION_TERMS = [
    "purity13_z",
    "purity0_z",
    "religion_practice_num_z",
    "purity13_religion_practice",
    "purity0_religion_practice",
]

THREE_WAY_TERMS = [
    "purity13_z",
    "parent_support_z",
    "gender_minority",
    "purity13_support",
    "purity13_x_gender_minority",
    "parent_support_x_gender_minority",
    "purity13_parent_support_gender_minority",
    "purity0_z",
]


def load_pipeline_module() -> Any:
    import importlib.util

    module_path = ROOT / "analysis" / "analysis_pipeline.py"
    spec = importlib.util.spec_from_file_location("analysis_pipeline", module_path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def save_csv(records: List[Dict[str, Any]], path: Path) -> None:
    df = pd.DataFrame(records)
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False)


def run_hyp1_parent_support(
    module: Any,
    df: pd.DataFrame,
    scenario: str,
    extra_features: Iterable[str] | None = None,
) -> List[Dict[str, Any]]:
    """Run the registered parental-support moderation for each outcome."""
    label, base_features, terms = module.hyp1_model_configs(df)[0]
    results: List[Dict[str, Any]] = []
    extra = list(extra_features) if extra_features is not None else []
    for outcome in ["self_love", "romantic_satisfaction", "anxiety"]:
        features = [*base_features, *extra]
        result = module.run_ols(outcome, features, df)
        summary = module.summarize_model(result, outcome, label, terms, df)
        for record in summary:
            record["scenario"] = scenario
        results.extend(summary)
    return results


def run_hyp2_gender_interactions(
    module: Any,
    df: pd.DataFrame,
    scenario: str,
    extra_features: Iterable[str] | None = None,
) -> List[Dict[str, Any]]:
    """Run the registered purity × gender-minority interaction models."""
    base_features = module.hyp2_base_features(df)
    extra = list(extra_features) if extra_features is not None else []
    results: List[Dict[str, Any]] = []
    for outcome in ["self_love", "romantic_satisfaction", "anxiety"]:
        # purity13 interaction
        features = [*base_features, *extra, "purity13_x_gender_minority"]
        result = module.run_ols(outcome, features, df)
        summary = module.summarize_model(result, outcome, "Hyp2_gender_purity13", module.HYP2_TERMS, df)
        for record in summary:
            record["scenario"] = scenario
        results.extend(summary)
        # purity0 interaction
        features = [*base_features, *extra, "purity0_x_gender_minority"]
        result = module.run_ols(outcome, features, df)
        summary = module.summarize_model(result, outcome, "Hyp2_gender_purity0", module.HYP2_TERMS, df)
        for record in summary:
            record["scenario"] = scenario
        results.extend(summary)
    return results


def run_gender_subgroup_moderation(
    module: Any,
    df: pd.DataFrame,
    subgroup_name: str,
    categories: Iterable[str],
) -> List[Dict[str, Any]]:
    subset = df[df["gender_category"].isin(categories)].copy()
    if subset.empty:
        return []
    summary = run_hyp1_parent_support(module, subset, f"subgroup_{subgroup_name}")
    for record in summary:
        record["subgroup_n"] = int(subset.shape[0])
    return summary


def run_parent_support_gender_minority_three_way(
    module: Any,
    df: pd.DataFrame,
    scenario: str,
) -> List[Dict[str, Any]]:
    """Estimate the purity × parent-support × gender-minority interaction."""
    subset = df.copy()
    subset["parent_support_x_gender_minority"] = (
        subset["parent_support_z"] * subset["gender_minority"]
    )
    subset["purity13_parent_support_gender_minority"] = (
        subset["purity13_z"] * subset["parent_support_z"] * subset["gender_minority"]
    )
    _, base_features, _ = module.hyp1_model_configs(subset)[0]
    features = [
        *base_features,
        "gender_minority",
        "purity13_x_gender_minority",
        "parent_support_x_gender_minority",
        "purity13_parent_support_gender_minority",
    ]
    records: List[Dict[str, Any]] = []
    for outcome in ["self_love", "romantic_satisfaction", "anxiety"]:
        result = module.run_ols(outcome, features, subset)
        summary = module.summarize_model(
            result,
            outcome,
            "Hyp1_parent_support_gender_minority",
            THREE_WAY_TERMS,
            subset,
        )
        for record in summary:
            record["scenario"] = scenario
        records.extend(summary)
    return records


def run_hyp1_component_checks(module: Any, df: pd.DataFrame, scenario: str) -> List[Dict[str, Any]]:
    """Evaluate the guidance- and humor-based parent-support interactions."""
    configs = module.hyp1_model_configs(df)
    records: List[Dict[str, Any]] = []
    for label, features, terms in configs:
        if label == "Hyp1_parent_support":
            continue
        for outcome in ["self_love", "romantic_satisfaction", "anxiety"]:
            result = module.run_ols(outcome, features, df)
            summary = module.summarize_model(result, outcome, label, terms, df)
            for record in summary:
                record["scenario"] = scenario
            records.extend(summary)
    return records


def run_religion_interactions(module: Any, df: pd.DataFrame, scenario: str) -> List[Dict[str, Any]]:
    """Test whether current religiosity moderates purity effects."""
    label, base_features, _ = module.hyp1_model_configs(df)[0]
    features = [*base_features, "religion_practice_num_z", "purity13_religion_practice", "purity0_religion_practice"]
    records: List[Dict[str, Any]] = []
    for outcome in ["self_love", "romantic_satisfaction", "anxiety"]:
        result = module.run_ols(outcome, features, df)
        summary = module.summarize_model(
            result,
            outcome,
            "Hyp1_religion_interaction",
            RELIGION_INTERACTION_TERMS,
            df,
        )
        for record in summary:
            record["scenario"] = scenario
        records.extend(summary)
    return records


def main() -> None:
    module = load_pipeline_module()
    df = module.prepare_analytic_sample()

    df["religion_practice_num_z"] = module.standardize(df["religion_practice_num"])
    df["purity13_religion_practice"] = df["purity13_z"] * df["religion_practice_num_z"]
    df["purity0_religion_practice"] = df["purity0_z"] * df["religion_practice_num_z"]

    records: List[Dict[str, Any]] = []
    overview: Dict[str, Any] = {}

    # 1. Exclude respondents who currently practice any religion.
    no_religion = df[df["religion_practice"] == "No"].copy()
    overview["no_religion_n"] = int(no_religion.shape[0])
    records.extend(run_hyp1_parent_support(module, no_religion, "no_current_religion"))
    records.extend(run_hyp2_gender_interactions(module, no_religion, "no_current_religion"))
    save_csv(records, TABLES_DIR / "regression_results_no_current_religion.csv")
    records.clear()

    # 1a. Focus on respondents who currently practice a religion.
    current_religion = df[df["religion_practice"] != "No"].copy()
    overview["current_religion_n"] = int(current_religion.shape[0])
    records.extend(run_hyp1_parent_support(module, current_religion, "current_religion"))
    records.extend(run_hyp2_gender_interactions(module, current_religion, "current_religion"))
    save_csv(records, TABLES_DIR / "regression_results_current_religion.csv")
    records.clear()

    # 2. Add aggregated childhood trauma/depression controls.
    trauma_df = df.copy()
    trauma_df["childhood_abuse_mean"] = trauma_df[["abuse_0_12", "abuse_13_18"]].mean(axis=1)
    trauma_df["childhood_depressed_mean"] = trauma_df[["depressed_0_12", "depressed_13_18"]].mean(axis=1)
    trauma_df["childhood_abuse_mean_z"] = module.standardize(trauma_df["childhood_abuse_mean"])
    trauma_df["childhood_depressed_mean_z"] = module.standardize(trauma_df["childhood_depressed_mean"])
    extra_covariates = ["childhood_abuse_mean_z", "childhood_depressed_mean_z"]
    overview["trauma_controls_n"] = int(trauma_df.shape[0])
    records.extend(
        run_hyp1_parent_support(module, trauma_df, "with_trauma_controls", extra_covariates)
    )
    records.extend(
        run_hyp2_gender_interactions(module, trauma_df, "with_trauma_controls", extra_covariates)
    )
    save_csv(records, TABLES_DIR / "regression_results_with_trauma_controls.csv")
    records.clear()

    # 3. Control for unconditional love memory in both windows.
    overview["unconditional_love_controls_n"] = int(df.shape[0])
    love_extra = ["unconditional_love_0_z", "unconditional_love_13_z"]
    records.extend(
        run_hyp1_parent_support(module, df, "with_unconditional_love_controls", love_extra)
    )
    records.extend(
        run_hyp2_gender_interactions(module, df, "with_unconditional_love_controls", love_extra)
    )
    save_csv(
        records,
        TABLES_DIR / "regression_results_with_unconditional_love_controls.csv",
    )
    records.clear()

    # 2a. Evaluate parental-support components alone.
    component_records = run_hyp1_component_checks(module, df, "support_components")
    save_csv(component_records, TABLES_DIR / "regression_results_parent_support_components.csv")

    # 2b. Model purity × current religiosity interactions.
    religion_records = run_religion_interactions(module, df, "religion_practice_interaction")
    save_csv(religion_records, TABLES_DIR / "regression_results_religion_interactions.csv")

    # 3. Compare trans vs nonbinary gender-minority respondents.
    trans_categories = {"Woman (trans)", "Man (trans)"}
    nonbinary_categories = {
        "Nonbinary/other (assigned female at birth)",
        "Nonbinary/other (assigned male at birth)",
    }
    overview["trans_n"] = int(df["gender_category"].isin(trans_categories).sum())
    overview["nonbinary_n"] = int(df["gender_category"].isin(nonbinary_categories).sum())
    subgroup_records: List[Dict[str, Any]] = []
    subgroup_records.extend(run_gender_subgroup_moderation(module, df, "trans", trans_categories))
    subgroup_records.extend(run_gender_subgroup_moderation(module, df, "nonbinary", nonbinary_categories))
    for record in subgroup_records:
        record["scenario"] = record.get("scenario", "subgroup")
    save_csv(subgroup_records, TABLES_DIR / "gender_minority_subgroups.csv")

    parent_support_gender_minority_records = run_parent_support_gender_minority_three_way(
        module,
        df,
        "parent_support_gender_minority",
    )
    save_csv(
        parent_support_gender_minority_records,
        TABLES_DIR / "regression_results_parent_support_gender_minority.csv",
    )

    OUTPUT_SUMMARY.parent.mkdir(parents=True, exist_ok=True)
    overview["notes"] = (
        "Tables contain Hyp1 parent-support and Hyp2 gender-minority interaction results for the registered "
        "slices, plus component-based models, religiosity-interaction tests, a parent-support × purity × "
        "gender-minority robustness check, and a version that controls for unconditional-love memories in both "
        "childhood windows."
    )
    OUTPUT_SUMMARY.write_text(json.dumps(overview, indent=2), encoding="utf-8")
    print("Sensitivity analysis complete. Tables saved under tables/ and outputs/.")


if __name__ == "__main__":
    main()
