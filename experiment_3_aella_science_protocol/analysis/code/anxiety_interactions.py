#!/usr/bin/env python3
"""
Estimate CSA × moderator interactions for the anxiety outcome using OLS (HC3) and
ordinal logit specifications, and archive subgroup diagnostics.

Regeneration example:
python analysis/code/anxiety_interactions.py \
    --dataset data/clean/childhoodbalancedpublic_with_csa_indicator.csv \
    --config config/agent_config.yaml \
    --interactions CSA_score_indicator:cis_identity \
                 CSA_score_indicator:age_cohort \
                 CSA_score_indicator:classchild_collapsed \
    --out-table tables/diagnostics/anxiety_interactions.csv \
    --out-md qc/anxiety_subgroup_extensions.md \
    --seed 20251016
"""

from __future__ import annotations

import argparse
import random
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable, Dict, List, Sequence, Tuple

import numpy as np
import pandas as pd
import yaml
from patsy import dmatrix
from scipy import stats
from statsmodels.formula.api import ols
from statsmodels.miscmodels.ordinal_model import OrderedModel

DEFAULT_OUTCOME = "I tend to suffer from anxiety (npvfh98)-neg"
DEFAULT_PREDICTOR = "CSA_score_indicator"
DEFAULT_CONTROLS: Tuple[str, ...] = ("selfage", "gendermale", "classchild")


@dataclass(frozen=True)
class ModeratorSpec:
    """Configuration for constructing a moderator column."""

    name: str
    builder: Callable[[pd.DataFrame], pd.Series]
    label: str
    type: str  # "binary" or "categorical"
    drop_controls: Tuple[str, ...]


def build_cis_identity(df: pd.DataFrame) -> pd.Series:
    if "cis" not in df.columns:
        raise KeyError("Dataset missing required column 'cis' for cis_identity moderator.")
    mapping = {1: "Cis", 1.0: "Cis", 0: "Not cis", 0.0: "Not cis"}
    series = df["cis"].map(mapping)
    return series.astype("object")


def build_age_cohort(df: pd.DataFrame) -> pd.Series:
    if "selfage" not in df.columns:
        raise KeyError("Dataset missing required column 'selfage' for age_cohort moderator.")
    bins = [18, 30, 45, 60, 200]
    labels = ["18-29", "30-44", "45-59", "60+"]
    cohorts = pd.cut(
        df["selfage"],
        bins=bins,
        labels=labels,
        right=False,
        include_lowest=True,
    )
    return cohorts.astype("object")


def build_classchild_collapsed(df: pd.DataFrame) -> pd.Series:
    if "classchild" not in df.columns:
        raise KeyError(
            "Dataset missing required column 'classchild' for classchild_collapsed moderator."
        )
    bins = [-1, 1, 3, 7]
    labels = ["Lower (0-1)", "Middle (2-3)", "Upper (4-6)"]
    collapsed = pd.cut(
        df["classchild"],
        bins=bins,
        labels=labels,
        include_lowest=True,
    )
    return collapsed.astype("object")


MODERATOR_REGISTRY: Dict[str, ModeratorSpec] = {
    "cis_identity": ModeratorSpec(
        name="cis_identity",
        builder=build_cis_identity,
        label="Cisgender Identity",
        type="binary",
        drop_controls=(),
    ),
    "age_cohort": ModeratorSpec(
        name="age_cohort",
        builder=build_age_cohort,
        label="Age Cohort",
        type="categorical",
        drop_controls=("selfage",),
    ),
    "classchild_collapsed": ModeratorSpec(
        name="classchild_collapsed",
        builder=build_classchild_collapsed,
        label="Childhood Class (Collapsed)",
        type="categorical",
        drop_controls=("classchild",),
    ),
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Estimate CSA × moderator interactions for the anxiety outcome."
    )
    parser.add_argument("--dataset", required=True, help="Input CSV or Parquet dataset path.")
    parser.add_argument("--config", required=True, help="Config YAML with seed and thresholds.")
    parser.add_argument(
        "--interactions",
        nargs="+",
        required=True,
        help="Interaction specs in `predictor:moderator` format.",
    )
    parser.add_argument(
        "--out-table",
        required=True,
        help="Destination CSV for coefficient and subgroup diagnostics.",
    )
    parser.add_argument(
        "--out-md",
        required=True,
        help="Destination Markdown summary file.",
    )
    parser.add_argument(
        "--outcome",
        default=DEFAULT_OUTCOME,
        help="Outcome column capturing anxiety tendency (negatively keyed).",
    )
    parser.add_argument(
        "--predictor",
        default=DEFAULT_PREDICTOR,
        help="Primary predictor column (default: CSA_score_indicator).",
    )
    parser.add_argument(
        "--controls",
        nargs="*",
        default=list(DEFAULT_CONTROLS),
        help="Optional covariates to include (default: selfage, gendermale, classchild).",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=None,
        help="Override random seed (otherwise read from config).",
    )
    return parser.parse_args()


def load_config(path: Path) -> dict:
    config = yaml.safe_load(path.read_text())
    if not isinstance(config, dict):
        raise ValueError("Configuration file did not parse to a mapping.")
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


def enforce_cell_threshold(df: pd.DataFrame, columns: Sequence[str], threshold: int) -> None:
    counts = df.groupby(list(columns), dropna=False).size()
    below = counts[counts < threshold]
    if not below.empty:
        formatted = "; ".join(
            f"{dict(zip(columns, key))} -> {int(val)}" for key, val in below.items()
        )
        raise ValueError(
            f"Cell counts below suppression threshold {threshold}: {formatted}"
        )


def encode_outcome(series: pd.Series) -> tuple[pd.Series, List[float]]:
    levels = sorted(series.dropna().unique())
    mapping = {value: code for code, value in enumerate(levels)}
    encoded = series.map(mapping)
    if encoded.isna().any():
        raise ValueError("Outcome encoding produced missing values; check data integrity.")
    return encoded.astype(int), levels


def outcome_mean_ci(values: pd.Series) -> tuple[float, float, float, float]:
    n = len(values)
    mean = float(values.mean())
    std = float(values.std(ddof=1)) if n > 1 else 0.0
    se = float(std / np.sqrt(n)) if n > 1 else float("nan")
    ci_half = 1.96 * se if not np.isnan(se) else float("nan")
    return mean, std, se, ci_half


def render_markdown_table(df: pd.DataFrame) -> str:
    headers = list(df.columns)
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join(["---"] * len(headers)) + " |",
    ]
    for _, row in df.iterrows():
        values = [
            "" if pd.isna(val) else f"{val}"
            for val in row.tolist()
        ]
        lines.append("| " + " | ".join(values) + " |")
    return "\n".join(lines)


def prepare_moderator(df: pd.DataFrame, spec: ModeratorSpec) -> pd.Series:
    series = spec.builder(df)
    if series.isna().all():
        raise ValueError(f"Moderator `{spec.name}` produced only missing values.")
    return series


def build_design_formula(moderator: ModeratorSpec) -> str:
    if moderator.type == "categorical":
        return "predictor + C(moderator) + predictor:C(moderator)"
    if moderator.type == "binary":
        return "predictor + moderator + predictor:moderator"
    raise ValueError(f"Unsupported moderator type: {moderator.type}")


def fit_ols(
    data: pd.DataFrame, formula: str
) -> Tuple[pd.Series, pd.Series, pd.Series, int]:
    model = ols(f"outcome ~ {formula}", data=data).fit(cov_type="HC3")
    params = model.params
    ses = model.bse
    tvalues = model.tvalues
    df_resid = int(model.df_resid)
    return params, ses, tvalues, df_resid


def fit_ordinal_logit(
    endog: pd.Series, design: pd.DataFrame
) -> Tuple[pd.Series, pd.Series, pd.Series, int]:
    model = OrderedModel(endog, design, distr="logit")
    result = model.fit(method="bfgs", disp=False)
    if not bool(result.mle_retvals.get("converged", False)):
        raise RuntimeError("Ordinal logit model failed to converge.")
    params = result.params.loc[design.columns]
    ses = result.bse.loc[design.columns]
    z = params / ses
    return params, ses, z, int(result.nobs)


def summarise_coefficients(
    interaction_label: str,
    model_label: str,
    params: pd.Series,
    ses: pd.Series,
    stats_values: pd.Series,
    sample_size: int,
    seed: int,
    timestamp: str,
    df_denom: int | None,
) -> List[dict]:
    rows: List[dict] = []
    for term, estimate in params.items():
        se = float(ses[term])
        stat = float(stats_values[term])
        ci_half = 1.96 * se
        if df_denom is None:
            p_value = float(2 * stats.norm.sf(abs(stat)))
        else:
            p_value = float(2 * stats.t.sf(abs(stat), df=df_denom))
        rows.append(
            {
                "interaction": interaction_label,
                "type": "coefficient",
                "model": model_label,
                "term": term,
                "estimate": float(estimate),
                "se": se,
                "ci_low": float(estimate - ci_half),
                "ci_high": float(estimate + ci_half),
                "p_value": p_value,
                "statistic": stat,
                "df": df_denom if df_denom is not None else np.nan,
                "n_unweighted": sample_size,
                "n_weighted": float(sample_size),
                "moderator_level": "",
                "csa_level": "",
                "notes": "",
                "seed": seed,
                "generated_at": timestamp,
            }
        )
    return rows


def summarise_subgroups(
    interaction_label: str,
    predictor: str,
    moderator_name: str,
    df: pd.DataFrame,
    seed: int,
    timestamp: str,
) -> List[dict]:
    rows: List[dict] = []
    grouped = (
        df.groupby([predictor, moderator_name], dropna=False)["outcome"]
        .apply(list)
        .reset_index()
    )
    for _, row in grouped.iterrows():
        values = pd.Series(row["outcome"])
        n = len(values)
        mean, std, se, ci_half = outcome_mean_ci(values)
        rows.append(
            {
                "interaction": interaction_label,
                "type": "subgroup_mean",
                "model": "descriptive",
                "term": "outcome_mean",
                "estimate": mean,
                "se": se,
                "ci_low": mean - ci_half if not np.isnan(ci_half) else np.nan,
                "ci_high": mean + ci_half if not np.isnan(ci_half) else np.nan,
                "p_value": np.nan,
                "statistic": np.nan,
                "df": np.nan,
                "n_unweighted": n,
                "n_weighted": float(n),
                "moderator_level": str(row[moderator_name]),
                "csa_level": str(int(row[predictor])) if pd.notna(row[predictor]) else "nan",
                "notes": "",
                "seed": seed,
                "generated_at": timestamp,
            }
        )
    return rows


def build_markdown_summary(
    interaction_label: str,
    moderator_spec: ModeratorSpec,
    sample_size: int,
    outcome_levels: Sequence[float],
    coeff_table: pd.DataFrame,
    subgroup_table: pd.DataFrame,
) -> List[str]:
    lines = [
        f"## Interaction: `{interaction_label}`",
        "",
        f"- Moderator label: **{moderator_spec.label}**",
        f"- Sample (complete cases): {sample_size}",
        f"- Outcome levels analysed: {', '.join(str(x) for x in outcome_levels)}",
        "",
        "### Coefficients",
        render_markdown_table(
            coeff_table[
                [
                    "model",
                    "term",
                    "estimate",
                    "se",
                    "ci_low",
                    "ci_high",
                    "p_value",
                ]
            ].round(6)
        ),
        "",
        "### Subgroup Means (CSA level × Moderator level)",
        render_markdown_table(
            subgroup_table[
                [
                    "csa_level",
                    "moderator_level",
                    "estimate",
                    "se",
                    "n_unweighted",
                ]
            ].round(6)
        ),
        "",
    ]
    return lines


def main() -> None:
    args = parse_args()

    dataset_path = Path(args.dataset)
    config_path = Path(args.config)
    out_table_path = Path(args.out_table)
    out_md_path = Path(args.out_md)

    config = load_config(config_path)
    seed = int(args.seed if args.seed is not None else config.get("seed", 20251016))
    threshold = int(config.get("small_cell_threshold", 10))
    seed_everything(seed)

    df = load_dataset(dataset_path)
    outcome_name = args.outcome
    predictor_name = args.predictor

    if outcome_name not in df.columns:
        raise KeyError(f"Outcome column `{outcome_name}` not found in dataset.")
    if predictor_name not in df.columns:
        raise KeyError(f"Predictor column `{predictor_name}` not found in dataset.")

    requested_controls = list(args.controls)

    outputs: List[dict] = []
    md_sections: List[str] = [
        "# CSA–Anxiety Interaction Diagnostics",
        f"Generated: {datetime.now(timezone.utc).isoformat()} | Seed: {seed}",
        "",
        f"- Dataset: `{dataset_path}`",
        f"- Outcome: `{outcome_name}`",
        f"- Predictor: `{predictor_name}`",
        "",
    ]

    for spec_str in args.interactions:
        try:
            predictor, moderator_name = spec_str.split(":")
        except ValueError as exc:
            raise ValueError(
                f"Interaction specification `{spec_str}` must follow `predictor:moderator`."
            ) from exc

        if predictor != predictor_name:
            raise ValueError(
                f"Predictor mismatch in `{spec_str}` (expected `{predictor_name}`)."
            )
        if moderator_name not in MODERATOR_REGISTRY:
            valid = ", ".join(sorted(MODERATOR_REGISTRY))
            raise KeyError(
                f"Moderator `{moderator_name}` not registered. Available: {valid}."
            )

        moderator_spec = MODERATOR_REGISTRY[moderator_name]
        df[moderator_spec.name] = prepare_moderator(df, moderator_spec)

        required_columns = [
            outcome_name,
            predictor_name,
            moderator_spec.name,
            *requested_controls,
        ]
        missing = [col for col in required_columns if col not in df.columns]
        if missing:
            raise KeyError(f"Required columns missing: {', '.join(missing)}")

        working = df.loc[:, required_columns].dropna().copy()
        enforce_cell_threshold(
            working,
            columns=[predictor_name, moderator_spec.name],
            threshold=threshold,
        )

        interaction_label = f"{predictor_name}:{moderator_spec.name}"
        timestamp = datetime.now(timezone.utc).isoformat()

        controls = [
            control for control in requested_controls if control not in moderator_spec.drop_controls
        ]

        # Prepare modelling frame with simplified column names.
        framing = working.rename(
            columns={
                outcome_name: "outcome",
                predictor_name: "predictor",
                moderator_spec.name: "moderator",
            }
        ).copy()

        # Ensure numeric predictor/control types for modelling.
        framing["predictor"] = framing["predictor"].astype(float)
        for control in controls:
            if control not in framing.columns:
                continue
            framing[control] = framing[control].astype(float)

        outcome_encoded, outcome_levels = encode_outcome(framing["outcome"])
        framing["outcome"] = framing["outcome"].astype(float)

        design_formula = build_design_formula(moderator_spec)
        if controls:
            design_formula = design_formula + " + " + " + ".join(controls)

        # OLS with HC3 covariance.
        ols_params, ols_ses, ols_tvalues, df_resid = fit_ols(framing, design_formula)
        outputs.extend(
            summarise_coefficients(
                interaction_label=interaction_label,
                model_label="ols_hc3",
                params=ols_params,
                ses=ols_ses,
                stats_values=ols_tvalues,
                sample_size=len(framing),
                seed=seed,
                timestamp=timestamp,
                df_denom=df_resid,
            )
        )

        # Ordinal logit (logistic link).
        design_matrix = dmatrix(
            design_formula,
            data=framing,
            return_type="dataframe",
        )
        if "Intercept" in design_matrix.columns:
            design_matrix = design_matrix.drop(columns="Intercept")
        design_matrix = design_matrix.astype(float)
        ord_params, ord_ses, ord_zscores, n_obs = fit_ordinal_logit(
            endog=outcome_encoded,
            design=design_matrix,
        )
        outputs.extend(
            summarise_coefficients(
                interaction_label=interaction_label,
                model_label="ordinal_logit",
                params=ord_params,
                ses=ord_ses,
                stats_values=ord_zscores,
                sample_size=n_obs,
                seed=seed,
                timestamp=timestamp,
                df_denom=None,
            )
        )

        outputs.extend(
            summarise_subgroups(
                interaction_label=interaction_label,
                predictor=predictor_name,
                moderator_name=moderator_spec.name,
                df=working.assign(outcome=working[outcome_name]),
                seed=seed,
                timestamp=timestamp,
            )
        )

        coeff_frame = pd.DataFrame(
            [row for row in outputs if row["interaction"] == interaction_label and row["type"] == "coefficient"]
        )
        subgroup_frame = pd.DataFrame(
            [row for row in outputs if row["interaction"] == interaction_label and row["type"] == "subgroup_mean"]
        )
        md_sections.extend(
            build_markdown_summary(
                interaction_label=interaction_label,
                moderator_spec=moderator_spec,
                sample_size=len(framing),
                outcome_levels=outcome_levels,
                coeff_table=coeff_frame,
                subgroup_table=subgroup_frame,
            )
        )

    out_table_path.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(outputs).to_csv(out_table_path, index=False)

    md_sections.extend(
        [
            "## Reproducibility",
            f"- Command: `python analysis/code/anxiety_interactions.py --dataset {dataset_path} "
            f"--config {config_path} --interactions {' '.join(args.interactions)} "
            f"--out-table {out_table_path} --out-md {out_md_path}"
            + (f" --seed {seed}`" if args.seed is not None else "`"),
        ]
    )
    out_md_path.parent.mkdir(parents=True, exist_ok=True)
    out_md_path.write_text("\n".join(md_sections))


if __name__ == "__main__":
    main()
