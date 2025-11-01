
#!/usr/bin/env python3
"""Executable analysis runner for PAP hypotheses (HYP-001 through HYP-003).

The runner prepares hypothesis-specific datasets, applies disclosure-controls,
supports multiply imputed analyses (Rubin pooling), and emits reproducible
tables/metadata bundles. All randomness is seeded via the agent configuration.

Regeneration examples:
    python analysis/code/run_pap_models.py \
        --hypotheses HYP-001 HYP-002 HYP-003 \
        --mode exploratory \
        --dataset childhoodbalancedpublic_original.csv \
        --mi-dataset data/derived/childhoodbalancedpublic_mi_prototype.csv.gz \
        --config config/agent_config.yaml \
        --seed 20251016
"""
from __future__ import annotations

import argparse
import json
import math
import random
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Tuple

import numpy as np
import pandas as pd
import yaml
from scipy import stats
import statsmodels.api as sm
from statsmodels.miscmodels.ordinal_model import OrderedModel

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_DATASET = "childhoodbalancedpublic_original.csv"
DEFAULT_MI_DATASET = REPO_ROOT / "data" / "derived" / "childhoodbalancedpublic_mi_prototype.csv.gz"
DEFAULT_MI_MAP = REPO_ROOT / "analysis" / "imputation" / "mice_variable_map.json"
DEFAULT_CONFIG = REPO_ROOT / "config" / "agent_config.yaml"
DEFAULT_OUTPUT_DIR = REPO_ROOT / "tables"
SMALL_CELL_THRESHOLD = 10


@dataclass
class RunConfig:
    seed: int
    dataset: Path
    mode: str
    hypotheses: List[str]
    output_dir: Path
    cell_threshold: int = SMALL_CELL_THRESHOLD
    config_path: Optional[Path] = None
    mi_dataset: Optional[Path] = None
    mi_mapping: Optional[Path] = None
    mi_column_map: Optional[Dict[str, str]] = None


@dataclass
class PreparedData:
    df: pd.DataFrame
    outcome_col: str
    level_order: List[str]
    predictors: List[str]
    metadata: Dict[str, object]


@dataclass
class MIPreparedData:
    imputation_ids: List[int]
    frames: List[pd.DataFrame]
    outcome_col: str
    predictors: List[str]
    metadata: Dict[str, object]
    level_order: Optional[List[str]] = None


def load_project_seed(config_path: Path) -> Optional[int]:
    try:
        with config_path.open("r", encoding="utf-8") as fh:
            cfg = yaml.safe_load(fh)
        if isinstance(cfg, dict) and "seed" in cfg:
            return int(cfg["seed"])
    except FileNotFoundError:
        return None
    except Exception as exc:  # pragma: no cover - defensive log
        print(f"Warning: failed to read seed from {config_path}: {exc}")
    return None


def set_global_seed(seed: int) -> None:
    random.seed(seed)
    np.random.seed(seed)


def serialize_metadata(value):
    if isinstance(value, dict):
        return {str(k): serialize_metadata(v) for k, v in value.items()}
    if isinstance(value, list):
        return [serialize_metadata(v) for v in value]
    if isinstance(value, tuple):
        return [serialize_metadata(v) for v in value]
    if isinstance(value, (np.integer,)):
        return int(value)
    if isinstance(value, (np.floating,)):
        val = float(value)
        if math.isnan(val):
            return None
        if math.isinf(val):
            return "inf" if val > 0 else "-inf"
        return val
    if isinstance(value, Path):
        return str(value)
    return value


def pool_mi_parameters(
    params_list: List[pd.Series],
    cov_list: List[pd.DataFrame],
    alpha: float = 0.05,
) -> Tuple[pd.DataFrame, pd.Series, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    if not params_list:
        raise ValueError("No parameter estimates provided for pooling")

    index = params_list[0].index
    m = len(params_list)

    param_matrix = np.vstack([params.loc[index].values for params in params_list])
    beta_bar = param_matrix.mean(axis=0)

    cov_mats = [cov.loc[index, index].values for cov in cov_list]
    within_cov = sum(cov_mats) / m

    if m > 1:
        diffs = param_matrix - beta_bar
        between_cov = sum(np.outer(diff, diff) for diff in diffs) / (m - 1)
    else:
        between_cov = np.zeros_like(within_cov)

    total_cov = within_cov + (1 + 1 / m) * between_cov
    se = np.sqrt(np.clip(np.diag(total_cov), a_min=0.0, a_max=None))
    stats_values = np.divide(beta_bar, se, out=np.zeros_like(beta_bar), where=se > 0)

    dfs = []
    for k in range(len(beta_bar)):
        w = within_cov[k, k]
        b = between_cov[k, k]
        if w == 0 and b == 0:
            dfs.append(float("inf"))
            continue
        if w == 0:
            dfs.append(float(m - 1))
            continue
        lambda_k = ((1 + 1 / m) * b / w) if w != 0 else float("inf")
        if lambda_k == 0:
            dfs.append(float("inf"))
        else:
            dfs.append(float((m - 1) * (1 + 1 / lambda_k) ** 2))

    dfs_array = np.array(dfs, dtype=float)
    crits = np.array(
        [
            stats.t.ppf(1 - alpha / 2, df) if np.isfinite(df) else stats.norm.ppf(1 - alpha / 2)
            for df in dfs_array
        ]
    )
    p_values = np.array(
        [
            2 * stats.t.sf(abs(stat_val), df)
            if np.isfinite(df)
            else 2 * (1 - stats.norm.cdf(abs(stat_val)))
            for stat_val, df in zip(stats_values, dfs_array)
        ]
    )
    ci_low = beta_bar - crits * se
    ci_high = beta_bar + crits * se

    summary_df = pd.DataFrame(
        {
            "term": index,
            "estimate": beta_bar,
            "std_error": se,
            "df": dfs_array,
            "stat": stats_values,
            "p_value": p_values,
            "ci_low": ci_low,
            "ci_high": ci_high,
        }
    )

    pooled_params = pd.Series(beta_bar, index=index)
    pooled_cov = pd.DataFrame(total_cov, index=index, columns=index)
    within_cov_df = pd.DataFrame(within_cov, index=index, columns=index)
    between_cov_df = pd.DataFrame(between_cov, index=index, columns=index)

    return summary_df, pooled_params, pooled_cov, within_cov_df, between_cov_df


def prepare_hyp001_mi(
    mi_df: pd.DataFrame,
    cell_threshold: int,
    column_map: Optional[Dict[str, str]] = None,
) -> MIPreparedData:
    outcome_col = "i_love_myself_2l8994l"
    predictor_col = "during_ages_0_12_your_parents_verbally_or_emotionally_abused_you_mds78zu"
    control_cols = ["selfage", "gendermale", "education"]

    required = ["imputation_id", outcome_col, predictor_col, *control_cols]
    missing = [col for col in required if col not in mi_df.columns]
    if missing:
        raise ValueError(f"Missing required columns for HYP-001: {', '.join(missing)}")

    frames: List[pd.DataFrame] = []
    imputation_ids: List[int] = []
    n_per_imputation: List[int] = []
    abuse_levels: Optional[List[float]] = None
    reference_counts: Optional[pd.Series] = None
    control_mean_totals = {col: 0.0 for col in control_cols}

    grouped = mi_df.groupby("imputation_id", sort=True)
    for imp_id, imp_df in grouped:
        subset = imp_df[required].dropna().copy()
        if subset.empty:
            continue
        subset = subset.rename(
            columns={
                outcome_col: "self_love",
                predictor_col: "abuse",
            }
        )
        for col in ["self_love", "abuse", *control_cols]:
            subset[col] = pd.to_numeric(subset[col], errors="coerce")
        subset = subset.dropna()
        if subset.empty:
            continue

        counts = subset["abuse"].value_counts()
        if (counts < cell_threshold).any():
            raise ValueError(
                f"Abuse frequency level below disclosure threshold in imputation {imp_id}"
            )
        if abuse_levels is None:
            abuse_levels = sorted(counts.index.astype(float).tolist())
        if reference_counts is None:
            reference_counts = counts.sort_index()

        imputation_ids.append(int(imp_id))
        n_per_imputation.append(int(len(subset)))
        for col in control_cols:
            control_mean_totals[col] += float(subset[col].mean())

        frames.append(subset[["self_love", "abuse", *control_cols]])

    if not frames:
        raise ValueError("No usable observations found for HYP-001 after preparation")

    m = len(frames)
    control_means = {col: control_mean_totals[col] / m for col in control_cols}
    abuse_levels = abuse_levels or []

    inverse_map = column_map or {}
    metadata = {
        "hypothesis": "HYP-001",
        "outcome_column": inverse_map.get(outcome_col, outcome_col),
        "predictor_column": inverse_map.get(predictor_col, predictor_col),
        "control_columns": [inverse_map.get(col, col) for col in control_cols],
        "prepared_outcome": "self_love",
        "prepared_predictor": "abuse",
        "n_per_imputation": n_per_imputation,
        "abuse_levels": abuse_levels,
        "control_means": control_means,
        "cell_threshold": cell_threshold,
    }
    if reference_counts is not None:
        metadata["abuse_level_counts_first_imputation"] = {
            str(level): int(count) for level, count in reference_counts.items()
        }

    return MIPreparedData(
        imputation_ids=imputation_ids,
        frames=frames,
        outcome_col="self_love",
        predictors=["abuse", *control_cols],
        metadata=metadata,
    )


def fit_mi_linear(prepped: MIPreparedData, alpha: float = 0.05) -> Tuple[pd.DataFrame, pd.DataFrame, Dict[str, object]]:
    params_list: List[pd.Series] = []
    cov_list: List[pd.DataFrame] = []

    for frame in prepped.frames:
        y = frame[prepped.outcome_col].astype(float)
        X = sm.add_constant(frame[prepped.predictors])
        result = sm.OLS(y, X).fit(cov_type="HC1")
        params_list.append(result.params)
        cov_list.append(result.cov_params())

    summary_df, pooled_params, pooled_cov, within_cov, between_cov = pool_mi_parameters(
        params_list, cov_list, alpha
    )
    summary_df.insert(1, "model", "mi_linear")

    control_means = prepped.metadata.get("control_means", {})
    abuse_levels = prepped.metadata.get("abuse_levels", [])
    finite_dfs = summary_df["df"].replace([np.inf], np.nan).dropna()
    df_reference = float(finite_dfs.min()) if not finite_dfs.empty else float("inf")

    predictions = []
    for level in abuse_levels:
        x_map = {"const": 1.0}
        for predictor in prepped.predictors:
            if predictor == "abuse":
                x_map[predictor] = float(level)
            else:
                x_map[predictor] = float(control_means.get(predictor, 0.0))
        x_vector = np.array([x_map.get(name, 0.0) for name in pooled_params.index], dtype=float)
        mean = float(np.dot(x_vector, pooled_params.values))
        variance = float(np.dot(x_vector, np.dot(pooled_cov.values, x_vector)))
        variance = max(variance, 0.0)
        se = math.sqrt(variance)
        crit = stats.t.ppf(0.975, df_reference) if np.isfinite(df_reference) else stats.norm.ppf(0.975)
        ci_low = mean - crit * se
        ci_high = mean + crit * se
        predictions.append(
            {
                "abuse_level": float(level),
                "predicted_self_love": mean,
                "std_error": se,
                "ci_low": ci_low,
                "ci_high": ci_high,
            }
        )

    predictions_df = pd.DataFrame(predictions)

    metadata = prepped.metadata.copy()
    metadata.update(
        {
            "n_imputations": len(params_list),
            "pooled_params": {term: float(val) for term, val in pooled_params.items()},
            "pooled_variance": {
                term: float(pooled_cov.loc[term, term]) for term in pooled_params.index
            },
            "within_variance_diag": {
                term: float(within_cov.loc[term, term]) for term in pooled_params.index
            },
            "between_variance_diag": {
                term: float(between_cov.loc[term, term]) for term in pooled_params.index
            },
            "degrees_of_freedom": {
                row.term: (None if not np.isfinite(row.df) else float(row.df))
                for row in summary_df.itertuples()
            },
            "prediction_controls_at": {k: float(v) for k, v in control_means.items()},
            "prediction_df_reference": None if not np.isfinite(df_reference) else float(df_reference),
            "alpha": alpha,
        }
    )

    return summary_df, predictions_df, metadata


def prepare_hyp002_mi(
    mi_df: pd.DataFrame,
    cell_threshold: int,
    column_map: Optional[Dict[str, str]] = None,
) -> MIPreparedData:
    outcome_col = "networth"
    predictor_col = "classchild"
    control_cols = ["selfage", "gendermale", "education"]

    required = ["imputation_id", outcome_col, predictor_col, *control_cols]
    missing = [col for col in required if col not in mi_df.columns]
    if missing:
        raise ValueError(f"Missing required columns for HYP-002: {', '.join(missing)}")

    networth_levels = sorted({int(round(val)) for val in mi_df[outcome_col].dropna().unique()})
    networth_labels = [str(level) for level in networth_levels]
    classchild_levels = sorted({int(round(val)) for val in mi_df[predictor_col].dropna().unique()})

    frames: List[pd.DataFrame] = []
    imputation_ids: List[int] = []
    n_per_imputation: List[int] = []
    control_mean_totals = {col: 0.0 for col in control_cols}
    reference_counts: Optional[pd.Series] = None

    label_map = {level: str(level) for level in networth_levels}

    grouped = mi_df.groupby("imputation_id", sort=True)
    for imp_id, imp_df in grouped:
        subset = imp_df[required].dropna().copy()
        if subset.empty:
            continue
        subset["networth_category"] = pd.Categorical(
            subset[outcome_col].round().astype(int).map(label_map),
            categories=networth_labels,
            ordered=True,
        )
        for col in [predictor_col, *control_cols]:
            subset[col] = pd.to_numeric(subset[col], errors="coerce")
        subset = subset.dropna()
        if subset.empty:
            continue

        counts = subset["networth_category"].value_counts()
        if (counts < cell_threshold).any():
            raise ValueError(
                f"Net worth category below disclosure threshold in imputation {imp_id}"
            )
        if reference_counts is None:
            reference_counts = counts.sort_index()

        imputation_ids.append(int(imp_id))
        n_per_imputation.append(int(len(subset)))
        for col in control_cols:
            control_mean_totals[col] += float(subset[col].mean())

        frames.append(
            subset[["networth_category", predictor_col, *control_cols]].rename(
                columns={predictor_col: "classchild"}
            )
        )

    if not frames:
        raise ValueError("No usable observations found for HYP-002 after preparation")

    m = len(frames)
    control_means = {col: control_mean_totals[col] / m for col in control_cols}

    inverse_map = column_map or {}
    metadata = {
        "hypothesis": "HYP-002",
        "outcome_column": inverse_map.get(outcome_col, outcome_col),
        "predictor_column": inverse_map.get(predictor_col, predictor_col),
        "control_columns": [inverse_map.get(col, col) for col in control_cols],
        "prepared_outcome": "networth_category",
        "prepared_predictor": "classchild",
        "n_per_imputation": n_per_imputation,
        "networth_levels": networth_levels,
        "networth_labels": networth_labels,
        "classchild_levels": classchild_levels,
        "control_means": control_means,
        "cell_threshold": cell_threshold,
    }
    if reference_counts is not None:
        metadata["networth_counts_first_imputation"] = {
            label: int(count) for label, count in reference_counts.items()
        }

    return MIPreparedData(
        imputation_ids=imputation_ids,
        frames=frames,
        outcome_col="networth_category",
        predictors=["classchild", *control_cols],
        metadata=metadata,
        level_order=networth_labels,
    )


def fit_mi_ordered_logit(
    prepped: MIPreparedData, alpha: float = 0.05
) -> Tuple[pd.DataFrame, pd.DataFrame, Dict[str, object]]:
    params_list: List[pd.Series] = []
    cov_list: List[pd.DataFrame] = []
    results: List[object] = []

    for frame in prepped.frames:
        outcome = frame[prepped.outcome_col]
        exog = frame[prepped.predictors].astype(float)
        model = OrderedModel(outcome, exog, distr="logit")
        result = model.fit(method="bfgs", disp=False, maxiter=1000, cov_type="HC1")
        params_list.append(result.params)
        cov_list.append(result.cov_params())
        results.append(result)

    summary_df, pooled_params, pooled_cov, within_cov, between_cov = pool_mi_parameters(
        params_list, cov_list, alpha
    )
    summary_df.insert(1, "model", "mi_ordered_logit")

    class_levels = prepped.metadata.get("classchild_levels", [])
    control_means = prepped.metadata.get("control_means", {})
    predictor_order = prepped.predictors

    prob_accum: Optional[np.ndarray] = None
    for result in results:
        rows = []
        for level in class_levels:
            row = {"classchild": float(level)}
            for control in predictor_order:
                if control == "classchild":
                    continue
                row[control] = float(control_means.get(control, 0.0))
            rows.append(row)
        pred_df = pd.DataFrame(rows)[predictor_order]
        probabilities = result.model.predict(result.params, exog=pred_df, which="prob")
        prob_accum = probabilities if prob_accum is None else prob_accum + probabilities

    prob_avg = prob_accum / len(results)
    prob_df = pd.DataFrame(prob_avg, columns=prepped.level_order)
    prob_df.insert(0, "classchild_level", class_levels)

    metadata = prepped.metadata.copy()
    metadata.update(
        {
            "n_imputations": len(results),
            "pooled_params": {term: float(val) for term, val in pooled_params.items()},
            "pooled_variance": {
                term: float(pooled_cov.loc[term, term]) for term in pooled_params.index
            },
            "within_variance_diag": {
                term: float(within_cov.loc[term, term]) for term in pooled_params.index
            },
            "between_variance_diag": {
                term: float(between_cov.loc[term, term]) for term in pooled_params.index
            },
            "degrees_of_freedom": {
                row.term: (None if not np.isfinite(row.df) else float(row.df))
                for row in summary_df.itertuples()
            },
            "prediction_controls_at": {k: float(v) for k, v in control_means.items()},
            "alpha": alpha,
        }
    )

    return summary_df, prob_df, metadata


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def df_to_markdown(df: pd.DataFrame) -> str:
    headers = list(df.columns)
    header_line = "| " + " | ".join(headers) + " |"
    separator = "| " + " | ".join(["---"] * len(headers)) + " |"
    lines = [header_line, separator]
    for _, row in df.iterrows():
        formatted = []
        for col in headers:
            val = row[col]
            if isinstance(val, (float, np.floating)):
                formatted.append(f"{float(val):.4f}")
            else:
                formatted.append(str(val))
        lines.append("| " + " | ".join(formatted) + " |")
    return "\n".join(lines)


def save_mi_table_bundle(
    tables: List[Tuple[str, pd.DataFrame, str]],
    metadata: Dict[str, object],
    output_dir: Path,
    mode: str,
    stem_base: str,
) -> List[Path]:
    ensure_dir(output_dir)
    timestamp = datetime.now(timezone.utc).isoformat()
    output_paths: List[Path] = []

    for suffix, table, title in tables:
        csv_path = output_dir / f"{stem_base}_{suffix}.csv"
        md_path = output_dir / f"{stem_base}_{suffix}.md"
        table_out = table.copy()
        for col in table_out.select_dtypes(include=[np.number]).columns:
            table_out[col] = table_out[col].astype(float)
        table_out.to_csv(csv_path, index=False)
        note = f"# {mode.title()} — {title}\n\nGenerated: {timestamp}\n\n"
        md_path.write_text(note + df_to_markdown(table_out), encoding="utf-8")
        output_paths.extend([csv_path, md_path])

    metadata_record = metadata.copy()
    metadata_record.update(
        {
            "mode": mode,
            "generated": timestamp,
            "outputs": [str(path.relative_to(REPO_ROOT)) for path in output_paths],
        }
    )
    meta_path = output_dir / f"{stem_base}_metadata.json"
    meta_path.write_text(json.dumps(serialize_metadata(metadata_record), indent=2), encoding="utf-8")
    output_paths.append(meta_path)
    return output_paths


def save_outputs(
    coeffs: pd.DataFrame,
    probs: pd.DataFrame,
    metadata: Dict[str, object],
    output_dir: Path,
    mode: str,
) -> List[Path]:
    ensure_dir(output_dir)
    timestamp = datetime.now(timezone.utc).isoformat()
    stem = f"{mode}_hyp003_ordered_logit"

    coeff_csv = output_dir / f"{stem}_coefficients.csv"
    coeff_md = output_dir / f"{stem}_coefficients.md"
    probs_csv = output_dir / f"{stem}_predicted_probabilities.csv"
    probs_md = output_dir / f"{stem}_predicted_probabilities.md"
    meta_json = output_dir / f"{stem}_metadata.json"

    coeffs.to_csv(coeff_csv, index=False)
    probs.to_csv(probs_csv, index=False)

    coeff_note = (
        f"# {mode.title()} — HYP-003 Ordered Logit Coefficients\n\n"
        f"Generated: {timestamp}\n\n"
        "All estimates assume simple random sampling with unit weights. "
        "Robust standard errors use the HC1 estimator."
    )
    probs_note = (
        f"# {mode.title()} — HYP-003 Category Probabilities\n\n"
        f"Generated: {timestamp}\n\n"
        "Predicted probabilities evaluated at sample means of numeric covariates."
    )

    coeff_md.write_text(coeff_note + "\n\n" + df_to_markdown(coeffs), encoding="utf-8")
    probs_md.write_text(probs_note + "\n\n" + df_to_markdown(probs), encoding="utf-8")

    metadata_record = dict(metadata)
    metadata_record.update(
        {
            "mode": mode,
            "generated": timestamp,
            "outputs": [
                str(coeff_csv.relative_to(REPO_ROOT)),
                str(coeff_md.relative_to(REPO_ROOT)),
                str(probs_csv.relative_to(REPO_ROOT)),
                str(probs_md.relative_to(REPO_ROOT)),
            ],
        }
    )
    meta_json.write_text(json.dumps(metadata_record, indent=2), encoding="utf-8")

    return [coeff_csv, coeff_md, probs_csv, probs_md, meta_json]


def prepare_hyp003(df: pd.DataFrame, cell_threshold: int) -> PreparedData:
    outcome_raw = "monogamy"
    religion_col = "Do you *currently* actively practice a religion? (902tbll)"
    age_col = "selfage"
    gender_col = "gendermale"
    relationship_candidates = [
        "Are you in a romantic relationship?",
        "Relationships_RelationshipStatus_Binary",
    ]

    required_columns: List[str] = [outcome_raw, religion_col, age_col, gender_col]
    missing_required = [col for col in required_columns if col not in df.columns]
    if missing_required:
        raise ValueError(
            "Missing required columns for HYP-003: " + ", ".join(missing_required)
        )

    use_rel_col: Optional[str] = None
    for candidate in relationship_candidates:
        if candidate in df.columns:
            series = df[candidate]
            if series.notna().sum() >= cell_threshold:
                use_rel_col = candidate
                break
    controls: List[str] = [age_col, gender_col]
    relationship_note: Optional[str] = None
    if use_rel_col:
        controls.append("relationship_status")
        rel_values = df[use_rel_col]
        if rel_values.dtype.kind in {"O", "U"}:
            rel_clean = rel_values.str.strip().str.lower()
            mapping = {"yes": 1, "no": 0}
            rel_numeric = rel_clean.map(mapping)
        else:
            rel_numeric = rel_values
        if rel_numeric.notna().sum() < cell_threshold:
            relationship_note = (
                f"Control {use_rel_col} dropped due to insufficient non-missing observations"
            )
        else:
            df = df.assign(relationship_status=rel_numeric)
    else:
        relationship_note = (
            "No relationship status control available with ≥ cell_threshold observations; "
            "model omits this control for now"
        )

    working = df[[outcome_raw, religion_col, age_col, gender_col]].copy()
    if "relationship_status" in df.columns:
        working = pd.concat([working, df[["relationship_status"]]], axis=1)

    working = working.dropna()

    outcome_map = {
        2.0: "full_monogamy",
        1.0: "leaning_monogamy",
        -1.0: "leaning_nonmonogamy",
        -2.0: "full_nonmonogamy",
    }
    working = working.assign(monogamy_category=working[outcome_raw].map(outcome_map))
    if working["monogamy_category"].isna().any():
        working = working.dropna(subset=["monogamy_category"])
    category_order = [
        "full_nonmonogamy",
        "leaning_nonmonogamy",
        "leaning_monogamy",
        "full_monogamy",
    ]

    collapse_applied = False
    counts = working["monogamy_category"].value_counts()
    if counts.min() < cell_threshold:
        collapse_applied = True
        collapse_map = {
            "full_nonmonogamy": "nonmonogamy",
            "leaning_nonmonogamy": "nonmonogamy",
            "leaning_monogamy": "leaning_monogamy",
            "full_monogamy": "full_monogamy",
        }
        working = working.assign(
            monogamy_category=working["monogamy_category"].map(collapse_map)
        )
        category_order = ["nonmonogamy", "leaning_monogamy", "full_monogamy"]
        post_counts = working["monogamy_category"].value_counts()
        if post_counts.min() < cell_threshold:
            raise ValueError(
                "Outcome categories still below disclosure threshold after collapsing"
            )

    religion_levels = [
        "No",
        "Yes, slightly",
        "Yes, moderately",
        "Yes, very seriously",
    ]
    working["religion_practice"] = pd.Categorical(
        working[religion_col], categories=religion_levels, ordered=True
    )
    working = working[working["religion_practice"].notna()]

    if working.empty:
        raise ValueError("No observations remain after preparing HYP-003 data")

    crosstab = pd.crosstab(
        working["monogamy_category"], working["religion_practice"], dropna=False
    )
    if (crosstab < cell_threshold).any().any():
        raise ValueError(
            "At least one outcome x predictor cell violates disclosure threshold"
        )

    working["monogamy_category"] = pd.Categorical(
        working["monogamy_category"], categories=category_order, ordered=True
    )

    predictors: List[str] = ["religion_practice", age_col, gender_col]
    if "relationship_status" in working.columns:
        predictors.append("relationship_status")

    metadata: Dict[str, object] = {
        "hypothesis": "HYP-003",
        "n_observations": int(len(working)),
        "cell_threshold": cell_threshold,
        "collapse_applied": collapse_applied,
        "relationship_control": use_rel_col,
        "relationship_note": relationship_note,
        "outcome_counts": counts.to_dict(),
        "crosstab": crosstab.to_dict(),
    }

    return PreparedData(
        df=working,
        outcome_col="monogamy_category",
        level_order=category_order,
        predictors=predictors,
        metadata=metadata,
    )


def fit_ordered_logit(prepped: PreparedData) -> Tuple[object, List[str]]:
    df = prepped.df
    outcome = df[prepped.outcome_col]

    dummy_cols = pd.get_dummies(
        df["religion_practice"], prefix="religion", drop_first=True
    )
    numeric_cols = []
    if "selfage" in prepped.predictors:
        numeric_cols.append("selfage")
    if "gendermale" in prepped.predictors:
        numeric_cols.append("gendermale")
    if "relationship_status" in df.columns and "relationship_status" in prepped.predictors:
        numeric_cols.append("relationship_status")
    exog_parts = [dummy_cols]
    if numeric_cols:
        exog_parts.append(df[numeric_cols])
    exog = pd.concat(exog_parts, axis=1).astype(float)

    model = OrderedModel(outcome, exog, distr="logit")
    result = model.fit(method="bfgs", disp=False, maxiter=1000, cov_type="HC1")
    exog_cols = list(exog.columns)
    return result, exog_cols


def extract_coefficients(result) -> pd.DataFrame:
    params = result.params
    bse = result.bse
    z_scores = params / bse
    p_values = 2 * (1 - stats.norm.cdf(np.abs(z_scores)))
    ci_low = params - stats.norm.ppf(0.975) * bse
    ci_high = params + stats.norm.ppf(0.975) * bse

    df = pd.DataFrame(
        {
            "term": params.index,
            "estimate": params.values,
            "std_error": bse,
            "z": z_scores,
            "p_value": p_values,
            "ci_low": ci_low,
            "ci_high": ci_high,
        }
    )
    df.insert(1, "model", "ordered_logit")
    return df


def compute_probabilities(result, exog_cols: Iterable[str], prepped: PreparedData) -> pd.DataFrame:
    df = prepped.df
    prediction_levels = df["religion_practice"].cat.categories
    ref_means: Dict[str, float] = {
        "selfage": float(df["selfage"].mean()),
        "gendermale": float(df["gendermale"].mean()),
    }
    if "relationship_status" in df.columns and "relationship_status" in prepped.predictors:
        ref_means["relationship_status"] = float(df["relationship_status"].mean())

    rows = []
    for level in prediction_levels:
        row_dict = {k: v for k, v in ref_means.items()}
        row_dict["religion_practice"] = level
        rows.append(row_dict)
    pred_df = pd.DataFrame(rows)
    pred_df["religion_practice"] = pd.Categorical(
        pred_df["religion_practice"],
        categories=df["religion_practice"].cat.categories,
        ordered=True,
    )

    dummy = pd.get_dummies(
        pred_df["religion_practice"], prefix="religion", drop_first=True
    )
    numeric_cols = [col for col in ref_means.keys()]
    exog_parts = [dummy]
    if numeric_cols:
        exog_parts.append(pred_df[numeric_cols])
    exog_pred = pd.concat(exog_parts, axis=1)
    exog_pred = exog_pred.reindex(columns=list(exog_cols), fill_value=0.0)
    exog_pred = exog_pred.astype(float)

    probs = result.model.predict(result.params, exog=exog_pred, which="prob")
    prob_df = pd.DataFrame(probs, columns=prepped.level_order)
    prob_df.insert(0, "religion_practice", list(prediction_levels))
    return prob_df


def run_hyp001(config: RunConfig, mi_df: pd.DataFrame) -> Dict[str, object]:
    prepped = prepare_hyp001_mi(mi_df, config.cell_threshold, config.mi_column_map)
    summary_df, predictions_df, metadata = fit_mi_linear(prepped)
    if config.mi_dataset is not None:
        metadata["mi_dataset"] = str(config.mi_dataset.relative_to(REPO_ROOT))
    if config.mi_mapping is not None:
        metadata["mi_mapping"] = str(config.mi_mapping.relative_to(REPO_ROOT))

    stem = f"{config.mode}_hyp001_mi_linear"
    outputs = save_mi_table_bundle(
        [
            ("coefficients", summary_df, "HYP-001 MI Linear Coefficients"),
            ("predicted_means", predictions_df, "HYP-001 Predicted Self-Love by Abuse Level"),
        ],
        metadata,
        config.output_dir,
        config.mode,
        stem,
    )
    n_per_imp = metadata.get("n_per_imputation", [])
    avg_n = int(round(float(np.mean(n_per_imp)))) if n_per_imp else None
    return {
        "outputs": [str(path.relative_to(REPO_ROOT)) for path in outputs],
        "n_obs": avg_n,
        "n_imputations": metadata.get("n_imputations"),
        "n_per_imputation": n_per_imp,
    }


def run_hyp002(config: RunConfig, mi_df: pd.DataFrame) -> Dict[str, object]:
    prepped = prepare_hyp002_mi(mi_df, config.cell_threshold, config.mi_column_map)
    summary_df, prob_df, metadata = fit_mi_ordered_logit(prepped)
    if config.mi_dataset is not None:
        metadata["mi_dataset"] = str(config.mi_dataset.relative_to(REPO_ROOT))
    if config.mi_mapping is not None:
        metadata["mi_mapping"] = str(config.mi_mapping.relative_to(REPO_ROOT))

    stem = f"{config.mode}_hyp002_mi_ordered_logit"
    outputs = save_mi_table_bundle(
        [
            ("coefficients", summary_df, "HYP-002 MI Ordered-Logit Coefficients"),
            (
                "predicted_probabilities",
                prob_df,
                "HYP-002 Predicted Net-Worth Probabilities by Childhood Class",
            ),
        ],
        metadata,
        config.output_dir,
        config.mode,
        stem,
    )
    n_per_imp = metadata.get("n_per_imputation", [])
    avg_n = int(round(float(np.mean(n_per_imp)))) if n_per_imp else None
    return {
        "outputs": [str(path.relative_to(REPO_ROOT)) for path in outputs],
        "n_obs": avg_n,
        "n_imputations": metadata.get("n_imputations"),
        "n_per_imputation": n_per_imp,
    }


def run_hyp003(config: RunConfig, df: pd.DataFrame) -> Dict[str, object]:
    prepared = prepare_hyp003(df, config.cell_threshold)
    result, exog_cols = fit_ordered_logit(prepared)
    coeffs = extract_coefficients(result)
    probs = compute_probabilities(result, exog_cols, prepared)
    outputs = save_outputs(coeffs, probs, prepared.metadata, config.output_dir, config.mode)
    return {
        "outputs": [str(path.relative_to(REPO_ROOT)) for path in outputs],
        "n_obs": prepared.metadata.get("n_observations"),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run PAP analyses for specified hypotheses.")
    parser.add_argument("--hypotheses", nargs="+", default=["HYP-003"], help="Hypothesis IDs to run.")
    parser.add_argument("--dataset", default=DEFAULT_DATASET, help="Dataset path (relative or absolute).")
    parser.add_argument("--mi-dataset", default=str(DEFAULT_MI_DATASET), help="Stacked multiply-imputed dataset path.")
    parser.add_argument("--mi-mapping", default=str(DEFAULT_MI_MAP), help="Imputation variable map (original -> sanitized).")
    parser.add_argument("--config", default=str(DEFAULT_CONFIG), help="Agent config YAML with seed.")
    parser.add_argument("--seed", type=int, default=None, help="Override random seed.")
    parser.add_argument("--mode", choices=["exploratory", "confirmatory"], default="exploratory")
    parser.add_argument(
        "--output-dir",
        default=str(DEFAULT_OUTPUT_DIR),
        help="Directory for result artifacts.",
    )
    parser.add_argument(
        "--cell-threshold",
        type=int,
        default=SMALL_CELL_THRESHOLD,
        help="Disclosure control minimum cell count.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    config_path = Path(args.config)
    config_seed = load_project_seed(config_path) if config_path.exists() else None
    seed = args.seed if args.seed is not None else config_seed
    if seed is None:
        raise ValueError("Seed must be provided via --seed or config file.")
    set_global_seed(seed)

    dataset_path = Path(args.dataset)
    if not dataset_path.is_absolute():
        dataset_path = REPO_ROOT / dataset_path
    if not dataset_path.exists():
        raise FileNotFoundError(f"Dataset not found: {dataset_path}")

    df = pd.read_csv(dataset_path, low_memory=False)

    output_dir = Path(args.output_dir)
    if not output_dir.is_absolute():
        output_dir = REPO_ROOT / output_dir

    hypotheses = [h.upper() for h in args.hypotheses]
    mi_needed = any(h in {"HYP-001", "HYP-002"} for h in hypotheses)

    mi_df: Optional[pd.DataFrame] = None
    mi_dataset_path: Optional[Path] = None
    mi_mapping_path: Optional[Path] = None
    mi_column_map: Optional[Dict[str, str]] = None

    if mi_needed:
        mi_dataset_path = Path(args.mi_dataset)
        if not mi_dataset_path.is_absolute():
            mi_dataset_path = REPO_ROOT / mi_dataset_path
        if not mi_dataset_path.exists():
            raise FileNotFoundError(f"MI dataset not found: {mi_dataset_path}")
        mi_df = pd.read_csv(mi_dataset_path, low_memory=False)

        mi_mapping_path = Path(args.mi_mapping)
        if not mi_mapping_path.is_absolute():
            mi_mapping_path = REPO_ROOT / mi_mapping_path
        if mi_mapping_path.exists():
            mapping_raw = json.loads(mi_mapping_path.read_text(encoding="utf-8"))
            if isinstance(mapping_raw, dict):
                # mapping is original -> sanitized; invert
                mi_column_map = {sanitized: original for original, sanitized in mapping_raw.items()}
            else:
                mi_column_map = None
        else:
            mi_column_map = None

    run_config = RunConfig(
        seed=seed,
        dataset=dataset_path,
        mode=args.mode,
        hypotheses=hypotheses,
        output_dir=output_dir,
        cell_threshold=args.cell_threshold,
        config_path=config_path if config_path.exists() else None,
        mi_dataset=mi_dataset_path,
        mi_mapping=mi_mapping_path if mi_mapping_path and mi_mapping_path.exists() else None,
        mi_column_map=mi_column_map,
    )

    summary: Dict[str, object] = {
        "dataset": str(run_config.dataset.relative_to(REPO_ROOT)),
        "mode": run_config.mode,
        "seed": run_config.seed,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "hypotheses": run_config.hypotheses,
        "executed": [],
    }

    for hyp in run_config.hypotheses:
        if hyp == "HYP-001":
            if mi_df is None:
                raise ValueError("MI dataset required for HYP-001 but not provided")
            result = run_hyp001(run_config, mi_df)
            summary["executed"].append({"hypothesis": hyp, **result})
        elif hyp == "HYP-002":
            if mi_df is None:
                raise ValueError("MI dataset required for HYP-002 but not provided")
            result = run_hyp002(run_config, mi_df)
            summary["executed"].append({"hypothesis": hyp, **result})
        elif hyp == "HYP-003":
            result = run_hyp003(run_config, df)
            summary["executed"].append({"hypothesis": hyp, **result})
        else:
            raise NotImplementedError(f"Hypothesis {hyp} not yet implemented")

    manifest_path = run_config.output_dir / f"{run_config.mode}_pap_run_summary.json"
    ensure_dir(run_config.output_dir)
    manifest_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")

    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
