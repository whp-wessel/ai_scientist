#!/usr/bin/env python3
"""
Evaluate differential item functioning (DIF) for the anxiety item across CSA exposure
and gender using an ordinal logistic model.

Regeneration example:
python analysis/code/test_anxiety_dif.py \
    --dataset data/clean/childhoodbalancedpublic_with_csa_indicator.csv \
    --config config/agent_config.yaml \
    --outcome "I tend to suffer from anxiety (npvfh98)-neg" \
    --csa CSA_score_indicator \
    --group gender \
    --group-value-column gendermale \
    --out-table tables/diagnostics/anxiety_dif.csv \
    --out-md qc/anxiety_dif.md
"""

from __future__ import annotations

import argparse
import logging
import random
from datetime import datetime, timezone
from pathlib import Path
from typing import List

import numpy as np
import pandas as pd
import yaml
from scipy import stats
from statsmodels.miscmodels.ordinal_model import OrderedModel


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Fit ordinal logistic models for the anxiety item and test CSA by gender DIF."
        )
    )
    parser.add_argument("--dataset", required=True, help="Input CSV or Parquet dataset.")
    parser.add_argument("--config", required=True, help="YAML config with seed info.")
    parser.add_argument(
        "--outcome",
        default="I tend to suffer from anxiety (npvfh98)-neg",
        help="Ordinal outcome column capturing anxiety tendency (neg-coded).",
    )
    parser.add_argument(
        "--csa",
        default="CSA_score_indicator",
        help="Binary CSA exposure indicator (1 = exposure).",
    )
    parser.add_argument(
        "--group",
        default="gender",
        help="Human-readable label for the focal grouping variable.",
    )
    parser.add_argument(
        "--group-value-column",
        default="gendermale",
        help="Column containing binary group membership (1 = focal group).",
    )
    parser.add_argument(
        "--covariates",
        nargs="*",
        default=[],
        help="Optional covariate columns included in both models.",
    )
    parser.add_argument(
        "--out-table",
        required=True,
        help="Destination CSV for DIF statistics.",
    )
    parser.add_argument(
        "--out-md",
        required=True,
        help="Destination Markdown summary file.",
    )
    parser.add_argument(
        "--log-level",
        default="INFO",
        help="Logging verbosity (DEBUG, INFO, WARNING, ERROR).",
    )
    return parser.parse_args()


def configure_logging(level: str) -> None:
    logging.basicConfig(
        level=getattr(logging, level.upper(), logging.INFO),
        format="%(asctime)s %(levelname)s %(message)s",
    )


def load_config(path: Path) -> dict:
    config = yaml.safe_load(path.read_text())
    if not isinstance(config, dict):
        raise ValueError("Configuration file must parse to a dictionary.")
    return config


def seed_everything(seed: int) -> None:
    random.seed(seed)
    np.random.seed(seed)


def load_dataset(path: Path) -> pd.DataFrame:
    if path.suffix.lower() == ".csv":
        return pd.read_csv(path, low_memory=False)
    if path.suffix.lower() in {".parquet", ".pq"}:
        return pd.read_parquet(path)
    raise ValueError(f"Unsupported dataset format: {path.suffix}")


def validate_columns(df: pd.DataFrame, columns: List[str]) -> None:
    missing = [col for col in columns if col not in df.columns]
    if missing:
        joined = ", ".join(missing)
        raise ValueError(f"Dataset missing required columns: {joined}")


def enforce_cell_threshold(
    df: pd.DataFrame, cols: List[str], threshold: int
) -> None:
    counts = df.groupby(cols, dropna=False).size()
    below = counts[counts < threshold]
    if not below.empty:
        formatted = "; ".join(
            f"{dict(zip(cols, key))} -> {int(val)}" for key, val in below.items()
        )
        raise ValueError(
            f"Cell counts below suppression threshold {threshold}: {formatted}"
        )


def prepare_outcome(series: pd.Series) -> tuple[pd.Series, List[float]]:
    ordered_levels = sorted(series.dropna().unique())
    mapping = {value: code for code, value in enumerate(ordered_levels)}
    encoded = series.map(mapping)
    if encoded.isna().any():
        raise ValueError("Outcome encoding resulted in missing values.")
    return encoded.astype(int), ordered_levels


def build_exog_matrix(
    df: pd.DataFrame, csa_col: str, group_col: str, covariates: List[str]
) -> pd.DataFrame:
    exog = df[[csa_col, group_col]].astype(float).copy()
    exog[f"{csa_col}_x_{group_col}"] = exog[csa_col] * exog[group_col]
    for cov in covariates:
        exog[cov] = df[cov].astype(float)
    return exog


def fit_ordered_model(endog: pd.Series, exog: pd.DataFrame) -> OrderedModel:
    model = OrderedModel(endog, exog, distr="logit")
    result = model.fit(method="bfgs", disp=False)
    if not bool(result.mle_retvals.get("converged", False)):
        raise RuntimeError("Ordinal model failed to converge.")
    return result


def summarise_coefficients(
    result, exog_columns: List[str], seed: int, timestamp: str
) -> pd.DataFrame:
    rows = []
    params = result.params
    bse = result.bse
    z_scores = params / bse
    for col in exog_columns:
        estimate = float(params[col])
        se = float(bse[col])
        z = float(z_scores[col])
        p_value = float(2 * stats.norm.sf(abs(z)))
        ci_half = 1.96 * se
        rows.append(
            {
                "type": "coefficient",
                "model": "full",
                "term": col,
                "estimate": estimate,
                "se": se,
                "z": z,
                "ci_low": estimate - ci_half,
                "ci_high": estimate + ci_half,
                "p_value": p_value,
                "statistic": np.nan,
                "df": np.nan,
                "n_obs": int(result.nobs),
                "seed": seed,
                "generated_at": timestamp,
                "notes": "",
            }
        )
    return pd.DataFrame(rows)


def lr_test(
    base_result, full_result, interaction_col: str, seed: int, timestamp: str
) -> pd.DataFrame:
    lr_stat = float(2 * (full_result.llf - base_result.llf))
    df_diff = int(len(full_result.model.exog_names) - len(base_result.model.exog_names))
    if df_diff <= 0:
        raise ValueError("Full model does not add parameters over the base model.")
    p_value = float(stats.chi2.sf(lr_stat, df_diff))
    return pd.DataFrame(
        [
            {
                "type": "lr_test",
                "model": "full_vs_base",
                "term": interaction_col,
                "estimate": np.nan,
                "se": np.nan,
                "z": np.nan,
                "ci_low": np.nan,
                "ci_high": np.nan,
                "p_value": p_value,
                "statistic": lr_stat,
                "df": df_diff,
                "n_obs": int(full_result.nobs),
                "seed": seed,
                "generated_at": timestamp,
                "notes": "Likelihood-ratio test of interaction term.",
            }
        ]
    )


def subgroup_summary(
    df: pd.DataFrame, outcome: str, csa_col: str, group_col: str
) -> pd.DataFrame:
    summary = (
        df.groupby([csa_col, group_col], dropna=False)[outcome]
        .agg(["count", "mean", "std"])
        .reset_index()
        .rename(
            columns={
                "count": "n",
                "mean": "outcome_mean",
                "std": "outcome_sd",
            }
        )
    )
    summary["outcome_mean"] = summary["outcome_mean"].astype(float)
    summary["outcome_sd"] = summary["outcome_sd"].astype(float)
    summary["n"] = summary["n"].astype(int)
    return summary


def write_markdown(
    path: Path,
    seed: int,
    timestamp: str,
    outcome: str,
    csa_label: str,
    group_label: str,
    interaction_col: str,
    coef_df: pd.DataFrame,
    lr_df: pd.DataFrame,
    subgroup_df: pd.DataFrame,
    command: str,
) -> None:
    interaction_row = coef_df.loc[coef_df["term"] == interaction_col].iloc[0]
    lr_row = lr_df.iloc[0]
    md_lines = [
        "# Anxiety Item DIF (CSA \u00d7 Gender)",
        f"Generated: {timestamp} | Seed: {seed}",
        "",
        f"- Outcome: `{outcome}`",
        f"- CSA indicator: `{csa_label}`",
        f"- Group variable: `{group_label}`",
        "",
        "## Model Specification",
        "- Ordinal logistic (logit link) with thresholds for 7 response categories.",
        "- Baseline model: CSA + group (no interaction).",
        "- Full model: CSA + group + CSA\u00d7group interaction.",
        "",
        "## Interaction Effect",
        f"- Estimate: {interaction_row['estimate']:.3f} (SE = {interaction_row['se']:.3f})",
        f"- z = {interaction_row['z']:.3f}, p = {interaction_row['p_value']:.4f}",
        f"- 95% CI: [{interaction_row['ci_low']:.3f}, {interaction_row['ci_high']:.3f}]",
        "",
        "## Likelihood-Ratio Test",
        f"- LR statistic = {lr_row['statistic']:.3f} on {int(lr_row['df'])} df, "
        f"p = {lr_row['p_value']:.4f}",
        "",
        "## Subgroup Means (complete cases)",
    ]
    md_lines.append("")
    md_lines.append("| CSA | Gender (1=focal) | n | Mean | SD |")
    md_lines.append("|---|---|---|---|---|")
    for _, row in subgroup_df.iterrows():
        n_val = int(row["n"])
        md_lines.append(
            f"| {int(row[csa_label])} | {int(row[group_label])} | "
            f"{n_val} | {row['outcome_mean']:.3f} | {row['outcome_sd']:.3f} |"
        )
    md_lines.extend(
        [
            "",
            "## Interpretation",
            "- The interaction term captures differential item functioning (DIF); "
            "non-zero values indicate CSA-related shifts differ by gender.",
            "- Likelihood-ratio test compares models with and without the interaction.",
            "",
            "## Reproducibility",
            f"- Command: `{command}`",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(md_lines))


def main() -> None:
    args = parse_args()
    configure_logging(args.log_level)

    dataset_path = Path(args.dataset)
    config_path = Path(args.config)
    out_table_path = Path(args.out_table)
    out_md_path = Path(args.out_md)
    outcome_col = args.outcome
    csa_col = args.csa
    group_col = args.group_value_column
    covariates = args.covariates

    config = load_config(config_path)
    seed = int(config.get("seed", 0))
    threshold = int(config.get("small_cell_threshold", 10))
    seed_everything(seed)

    df = load_dataset(dataset_path)
    required = [outcome_col, csa_col, group_col, *covariates]
    validate_columns(df, required)

    working = df[required].dropna()
    if working.empty:
        raise ValueError("No complete cases available for DIF analysis.")

    enforce_cell_threshold(working, [csa_col, group_col], threshold)

    encoded_outcome, ordered_levels = prepare_outcome(working[outcome_col])
    logging.info("Outcome levels mapped as %s", ordered_levels)

    exog_full = build_exog_matrix(working, csa_col, group_col, covariates)
    interaction_col = f"{csa_col}_x_{group_col}"
    exog_base = exog_full.drop(columns=[interaction_col])

    model_base = fit_ordered_model(encoded_outcome, exog_base)
    model_full = fit_ordered_model(encoded_outcome, exog_full)

    timestamp = datetime.now(timezone.utc).isoformat()

    coef_df = summarise_coefficients(
        model_full, list(exog_full.columns), seed, timestamp
    )
    lr_df = lr_test(model_base, model_full, interaction_col, seed, timestamp)

    results_df = pd.concat([coef_df, lr_df], ignore_index=True)
    out_table_path.parent.mkdir(parents=True, exist_ok=True)
    results_df.to_csv(out_table_path, index=False)

    subgroup_df = subgroup_summary(
        working.assign(**{outcome_col: working[outcome_col]}),
        outcome_col,
        csa_col,
        group_col,
    )

    command = (
        f"python analysis/code/test_anxiety_dif.py --dataset {dataset_path} "
        f"--config {config_path} --outcome \"{outcome_col}\" --csa {csa_col} "
        f"--group {args.group} --group-value-column {group_col} "
        f"--out-table {out_table_path} --out-md {out_md_path}"
    )
    if covariates:
        covs = " ".join(covariates)
        command += f" --covariates {covs}"

    write_markdown(
        out_md_path,
        seed,
        timestamp,
        outcome_col,
        csa_col,
        group_col,
        interaction_col,
        coef_df,
        lr_df,
        subgroup_df,
        command,
    )


if __name__ == "__main__":
    main()
