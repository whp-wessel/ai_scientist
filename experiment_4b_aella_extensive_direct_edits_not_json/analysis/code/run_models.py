#!/usr/bin/env python3
"""Run PAP-listed models (H1–H3) with deterministic, survey-aware settings.

Purpose
-------
Implements the modeling commands referenced in `analysis/pre_analysis_plan.md`.
The script ingests the raw survey CSV plus metadata config, prepares variables,
fits the appropriate model per hypothesis, and writes exploratory JSON outputs
under `outputs/` (confirmatory tables remain blocked until the PAP is frozen).

Usage
-----
python analysis/code/run_models.py \
  --hypothesis all \
  --config config/agent_config.yaml \
  --seed 20251016 \
  --output-prefix outputs/run_models_loop003 \
  --draws 400
"""

from __future__ import annotations

import argparse
import json
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, List, Sequence

import numpy as np
import pandas as pd
import statsmodels.api as sm
from statsmodels.miscmodels.ordinal_model import OrderedModel, OrderedResults
import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]

RELIGION_ORDER = [
    "not at all important",
    "slightly important",
    "moderately important",
    "very important",
    "absolutely essentially important",
]

HEALTH_ORDER = ["poor", "fair", "good", "very good", "excellent"]

LIKERT_VALUES = [-3.0, -2.0, -1.0, 0.0, 1.0, 2.0, 3.0]

REQUIRED_ALIASES = [
    "wz901dj",
    "externalreligion",
    "pqo6jmj",
    "okq5xh8",
    "mds78zu",
    "2l8994l",
    "selfage",
    "biomale",
    "gendermale",
    "cis",
    "classchild",
    "classcurrent",
    "classteen",
    "siblingnumber",
    "mentalillness",
    "v1k988q",
    "rapist",
]


@dataclass
class RunContext:
    seed: int
    draws: int
    dataset_path: Path
    config_path: Path
    command: str


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Execute PAP models (H1–H3).")
    parser.add_argument(
        "--hypothesis",
        default="H1",
        help="Target hypothesis ID (H1, H2, H3, or 'all').",
    )
    parser.add_argument(
        "--config",
        default="config/agent_config.yaml",
        help="Path to agent configuration YAML.",
    )
    parser.add_argument(
        "--seed",
        type=int,
        help="Random seed (defaults to config value).",
    )
    parser.add_argument(
        "--output-prefix",
        default="outputs/run_models",
        help="Prefix for JSON outputs (per hypothesis).",
    )
    parser.add_argument(
        "--draws",
        type=int,
        default=400,
        help="Number of parameter draws for simulation-based CIs.",
    )
    return parser.parse_args()


def load_config(path: Path) -> dict[str, Any]:
    resolved = resolve_repo_path(path)
    data = yaml.safe_load(resolved.read_text())
    if not isinstance(data, dict):
        raise ValueError("Config file must be a YAML mapping.")
    data["_resolved_path"] = resolved
    return data


def resolve_repo_path(path_like: str | Path) -> Path:
    candidate = Path(path_like)
    if not candidate.is_absolute():
        candidate = (REPO_ROOT / candidate).resolve()
    return candidate


def resolve_dataset_path(raw_path: str) -> Path:
    candidate = resolve_repo_path(raw_path)
    if candidate.exists():
        return candidate
    alt = REPO_ROOT / "data" / "raw" / raw_path
    if alt.exists():
        return alt.resolve()
    raise FileNotFoundError(
        f"Survey dataset not found at '{raw_path}' or 'data/raw/{raw_path}'."
    )


def load_codebook_alias_map(codebook_path: Path) -> dict[str, str]:
    data = json.loads(codebook_path.read_text())
    mapping: dict[str, str] = {}
    for entry in data.get("variables", []):
        alias = entry.get("name")
        if not alias:
            continue
        source = entry.get("source_column") or alias
        mapping[alias] = source
    return mapping


def required_raw_columns(alias_map: dict[str, str]) -> list[str]:
    cols = []
    for alias in REQUIRED_ALIASES:
        source = alias_map.get(alias, alias)
        cols.append(source)
    return sorted(set(cols))


def load_analysis_frame(dataset_path: Path, alias_map: dict[str, str]) -> pd.DataFrame:
    usecols = required_raw_columns(alias_map)
    df_raw = pd.read_csv(dataset_path, usecols=usecols, low_memory=False)
    df = pd.DataFrame()
    for alias in REQUIRED_ALIASES:
        source = alias_map.get(alias, alias)
        if source not in df_raw.columns:
            raise KeyError(f"Required column '{source}' not present in dataset.")
        df[alias] = df_raw[source]
    return df


def encode_ordered_text(series: pd.Series, order: Sequence[str]) -> pd.Series:
    mapping = {label: idx for idx, label in enumerate(order)}
    result = pd.Series(np.nan, index=series.index, dtype=float)
    mask = series.notna()
    if mask.any():
        lowered = series[mask].astype(str).str.strip().str.lower()
        result.loc[mask] = lowered.map(mapping)
    return result


def ordinal_numeric_or_text(series: pd.Series, order: Sequence[str]) -> pd.Series:
    numeric = pd.to_numeric(series, errors="coerce")
    total = int(series.notna().sum())
    numeric_valid = int(numeric.notna().sum())
    if total > 0 and numeric_valid / total >= 0.9:
        return numeric
    return encode_ordered_text(series, order)


def encode_health(series: pd.Series) -> pd.Series:
    mapping = {label: idx for idx, label in enumerate(HEALTH_ORDER)}
    result = pd.Series(np.nan, index=series.index, dtype=float)
    mask = series.notna()
    if mask.any():
        lowered = series[mask].astype(str).str.strip().str.lower()
        result.loc[mask] = lowered.map(mapping)
    return result


def numeric_series(series: pd.Series) -> pd.Series:
    return pd.to_numeric(series, errors="coerce")


def select_controls(
    df: pd.DataFrame, candidates: Sequence[str]
) -> tuple[list[str], list[str]]:
    available: list[str] = []
    dropped: list[str] = []
    for col in candidates:
        if col not in df.columns:
            dropped.append(col)
            continue
        if df[col].notna().any():
            available.append(col)
        else:
            dropped.append(col)
    return available, dropped


def likert_binary(series: pd.Series) -> pd.Series:
    """Map -3..3 Likert scale to binary indicator (1=positive/yes, 0=negative)."""
    numeric = numeric_series(series)
    out = pd.Series(np.nan, index=numeric.index, dtype=float)
    out.loc[numeric > 0] = 1.0
    out.loc[numeric < 0] = 0.0
    return out


def prepare_variables(df: pd.DataFrame) -> pd.DataFrame:
    prepared = df.copy()
    prepared["selfage"] = numeric_series(prepared["selfage"])
    prepared["biomale"] = numeric_series(prepared["biomale"])
    prepared["gendermale"] = numeric_series(prepared["gendermale"])
    prepared["cis"] = numeric_series(prepared["cis"])
    prepared["wz901dj_score"] = numeric_series(prepared["wz901dj"])
    prepared["externalreligion_ord"] = ordinal_numeric_or_text(
        prepared["externalreligion"], RELIGION_ORDER
    )
    prepared["pqo6jmj_score"] = numeric_series(prepared["pqo6jmj"])
    prepared["okq5xh8_ord"] = encode_health(prepared["okq5xh8"])
    prepared["mds78zu_score"] = numeric_series(prepared["mds78zu"])
    prepared["mds78zu_binary"] = likert_binary(prepared["mds78zu"])
    prepared["self_love_score"] = numeric_series(prepared["2l8994l"])
    prepared["classchild_score"] = numeric_series(prepared["classchild"])
    prepared["classcurrent_score"] = numeric_series(prepared["classcurrent"])
    prepared["classteen_score"] = numeric_series(prepared["classteen"])
    prepared["siblingnumber"] = numeric_series(prepared["siblingnumber"])
    prepared["mentalillness"] = numeric_series(prepared["mentalillness"])
    prepared["v1k988q_score"] = numeric_series(prepared["v1k988q"])
    prepared["v1k988q_binary"] = likert_binary(prepared["v1k988q_score"])
    prepared["rapist"] = numeric_series(prepared["rapist"])
    return prepared


def extract_weights(
    data: pd.DataFrame, weight_col: str | None
) -> pd.Series | None:
    if not weight_col:
        return None
    if weight_col not in data.columns:
        raise KeyError(f"Weight column '{weight_col}' not present in data subset.")
    weights = pd.to_numeric(data[weight_col], errors="coerce")
    if weights.isna().any():
        raise ValueError(f"Weight column '{weight_col}' contains missing values.")
    return weights.astype(float)


def encode_ordered_outcome(series: pd.Series) -> tuple[pd.Series, list[float]]:
    non_missing = series.dropna()
    if non_missing.empty:
        raise ValueError("Outcome has no valid observations after cleaning.")
    ordered_levels = sorted(non_missing.unique())
    level_map = {value: idx for idx, value in enumerate(ordered_levels)}
    codes = series.map(level_map).astype(int)
    return codes, ordered_levels


def add_constant(exog: pd.DataFrame) -> pd.DataFrame:
    return sm.add_constant(exog, has_constant="add")


def simulate_from_cov(
    rng: np.random.Generator, mean: np.ndarray, cov: np.ndarray, draws: int
) -> np.ndarray:
    cov = np.asarray(cov)
    try:
        return rng.multivariate_normal(mean=mean, cov=cov, size=draws)
    except np.linalg.LinAlgError:
        diag = np.clip(np.diag(cov), a_min=1e-9, a_max=None)
        return rng.multivariate_normal(mean=mean, cov=np.diag(diag), size=draws)


def expected_score_difference(
    result: OrderedResults,
    params: np.ndarray,
    exog_low: np.ndarray,
    exog_high: np.ndarray,
    levels: list[float],
) -> float:
    probs_low = result.model.predict(params, exog_low, which="prob")
    probs_high = result.model.predict(params, exog_high, which="prob")
    level_values = np.asarray(levels, dtype=float)
    expected_low = np.dot(probs_low, level_values)
    expected_high = np.dot(probs_high, level_values)
    return float(np.mean(expected_high - expected_low))


def probability_difference(
    result: OrderedResults,
    params: np.ndarray,
    exog_low: np.ndarray,
    exog_high: np.ndarray,
    target_codes: Sequence[int],
) -> float:
    probs_low = result.model.predict(params, exog_low, which="prob")
    probs_high = result.model.predict(params, exog_high, which="prob")
    low_total = probs_low[:, target_codes].sum(axis=1)
    high_total = probs_high[:, target_codes].sum(axis=1)
    return float(np.mean(high_total - low_total))


def summarize_effect(samples: list[float], point_estimate: float) -> dict[str, float]:
    if samples:
        se = float(np.std(samples, ddof=1))
        ci_low, ci_high = np.percentile(samples, [2.5, 97.5])
    else:
        se = math.nan
        ci_low = math.nan
        ci_high = math.nan
    return {
        "estimate": point_estimate,
        "se": se,
        "ci_lower": float(ci_low),
        "ci_upper": float(ci_high),
    }


def run_h1(
    df: pd.DataFrame, ctx: RunContext, weight_col: str | None = None
) -> dict[str, Any]:
    base_cols = ["wz901dj_score", "externalreligion_ord"]
    control_candidates = [
        "selfage",
        "biomale",
        "gendermale",
        "cis",
        "classchild_score",
    ]
    available_controls, dropped_controls = select_controls(df, control_candidates)
    cols = base_cols + available_controls
    if weight_col and weight_col not in cols:
        cols.append(weight_col)
    data = df[cols].dropna()
    if data.empty:
        raise ValueError("H1 data frame is empty after dropping missing values.")
    y_codes, levels = encode_ordered_outcome(data["wz901dj_score"])
    design_cols = ["externalreligion_ord"] + available_controls
    exog = data[design_cols].copy()
    weights = extract_weights(data, weight_col)
    model_kwargs: dict[str, Any] = {"distr": "logit"}
    if weights is not None:
        model_kwargs["weights"] = weights
    model = OrderedModel(y_codes, exog, **model_kwargs)
    result = model.fit(method="bfgs", disp=False, maxiter=1000)
    exog_low = exog.copy()
    exog_high = exog.copy()
    low_value = RELIGION_ORDER.index("not at all important")
    high_value = RELIGION_ORDER.index("very important")
    exog_low["externalreligion_ord"] = low_value
    exog_high["externalreligion_ord"] = high_value
    exog_low_mat = exog_low.to_numpy()
    exog_high_mat = exog_high.to_numpy()
    base_effect = expected_score_difference(
        result, result.params.values, exog_low_mat, exog_high_mat, levels
    )
    rng = np.random.default_rng(ctx.seed + 101)
    sim_params = simulate_from_cov(rng, result.params.values, result.cov_params(), ctx.draws)
    samples = [
        expected_score_difference(result, params, exog_low_mat, exog_high_mat, levels)
        for params in sim_params
    ]
    effect_summary = summarize_effect(samples, base_effect)
    diagnostics = {
        "nobs": int(result.nobs),
        "llf": float(result.llf),
        "aic": float(result.aic),
        "bic": float(result.bic),
        "converged": bool(result.mle_retvals.get("converged", True)),
    }
    return {
        "hypothesis_id": "H1",
        "family": "wellbeing",
        "model": "ordered_logit",
        "outcome": "wz901dj_score",
        "predictor": "externalreligion_ord",
        "controls": available_controls,
        "dropped_controls": dropped_controls,
        "n_analytic": diagnostics["nobs"],
        "effect_metric": "ΔE[depression score | religion very important vs not important]",
        "effect": effect_summary,
        "contrast_values": {"low": low_value, "high": high_value},
        "ordered_levels": levels,
        "parameters": result.params.to_dict(),
        "diagnostics": diagnostics,
        "seed": ctx.seed,
        "draws": ctx.draws,
        "dataset_path": str(ctx.dataset_path),
        "command": ctx.command,
        "phase": "pap_draft_exploratory",
    }


def run_h2(
    df: pd.DataFrame, ctx: RunContext, weight_col: str | None = None
) -> dict[str, Any]:
    base_cols = ["okq5xh8_ord", "pqo6jmj_score"]
    control_candidates = [
        "selfage",
        "biomale",
        "gendermale",
        "classcurrent_score",
        "classteen_score",
        "mentalillness",
    ]
    available_controls, dropped_controls = select_controls(df, control_candidates)
    cols = base_cols + available_controls
    if weight_col and weight_col not in cols:
        cols.append(weight_col)
    data = df[cols].dropna()
    if data.empty:
        raise ValueError("H2 data frame is empty after dropping missing values.")
    y_codes, levels = encode_ordered_outcome(data["okq5xh8_ord"])
    design_cols = ["pqo6jmj_score"] + available_controls
    exog = data[design_cols].copy()
    weights = extract_weights(data, weight_col)
    model_kwargs: dict[str, Any] = {"distr": "logit"}
    if weights is not None:
        model_kwargs["weights"] = weights
    model = OrderedModel(y_codes, exog, **model_kwargs)
    result = model.fit(method="bfgs", disp=False, maxiter=1000)
    observed_vals = sorted(set(data["pqo6jmj_score"].dropna().unique()))
    q1 = data["pqo6jmj_score"].quantile(0.25)
    q3 = data["pqo6jmj_score"].quantile(0.75)
    low_value = nearest_value(q1, observed_vals)
    high_value = nearest_value(q3, observed_vals)
    exog_low = exog.copy()
    exog_high = exog.copy()
    exog_low["pqo6jmj_score"] = low_value
    exog_high["pqo6jmj_score"] = high_value
    exog_low_mat = exog_low.to_numpy()
    exog_high_mat = exog_high.to_numpy()
    threshold_code = HEALTH_ORDER.index("very good")
    high_cat_codes = [idx for idx, value in enumerate(levels) if value >= threshold_code]
    base_effect = probability_difference(
        result, result.params.values, exog_low_mat, exog_high_mat, high_cat_codes
    )
    rng = np.random.default_rng(ctx.seed + 202)
    sim_params = simulate_from_cov(rng, result.params.values, result.cov_params(), ctx.draws)
    samples = [
        probability_difference(result, params, exog_low_mat, exog_high_mat, high_cat_codes)
        for params in sim_params
    ]
    effect_summary = summarize_effect(samples, base_effect)
    diagnostics = {
        "nobs": int(result.nobs),
        "llf": float(result.llf),
        "aic": float(result.aic),
        "bic": float(result.bic),
        "converged": bool(result.mle_retvals.get("converged", True)),
    }
    return {
        "hypothesis_id": "H2",
        "family": "wellbeing",
        "model": "ordered_logit",
        "outcome": "okq5xh8_ord",
        "predictor": "pqo6jmj_score",
        "controls": available_controls,
        "dropped_controls": dropped_controls,
        "n_analytic": diagnostics["nobs"],
        "effect_metric": "ΔPr(health ∈ {very good, excellent}) | guidance Q3 vs Q1",
        "effect": effect_summary,
        "contrast_values": {"low": low_value, "high": high_value},
        "ordered_levels": levels,
        "parameters": result.params.to_dict(),
        "diagnostics": diagnostics,
        "seed": ctx.seed,
        "draws": ctx.draws,
        "dataset_path": str(ctx.dataset_path),
        "command": ctx.command,
        "phase": "pap_draft_exploratory",
    }


def nearest_value(target: float, observed: Sequence[float]) -> float:
    arr = np.array(sorted(observed))
    idx = (np.abs(arr - target)).argmin()
    return float(arr[idx])


def run_h3(
    df: pd.DataFrame, ctx: RunContext, weight_col: str | None = None
) -> dict[str, Any]:
    cols = [
        "self_love_score",
        "mds78zu_binary",
        "selfage",
        "biomale",
        "gendermale",
        "siblingnumber",
        "classchild_score",
    ]
    if weight_col and weight_col not in cols:
        cols.append(weight_col)
    data = df[cols].dropna()
    y = data["self_love_score"]
    exog = add_constant(
        data[
            [
                "mds78zu_binary",
                "selfage",
                "biomale",
                "gendermale",
                "siblingnumber",
                "classchild_score",
            ]
        ]
    )
    weights = extract_weights(data, weight_col)
    if weights is not None:
        model = sm.WLS(y, exog, weights=weights)
    else:
        model = sm.OLS(y, exog)
    result = model.fit(cov_type="HC1")
    coef = float(result.params["mds78zu_binary"])
    se = float(result.bse["mds78zu_binary"])
    ci_low, ci_high = result.conf_int().loc["mds78zu_binary"].tolist()
    diagnostics = {
        "nobs": int(result.nobs),
        "r_squared": float(result.rsquared),
        "adj_r_squared": float(result.rsquared_adj),
    }
    return {
        "hypothesis_id": "H3",
        "family": "psychosocial",
        "model": "linear_regression",
        "outcome": "self_love_score",
        "predictor": "mds78zu_binary",
        "controls": [
            "selfage",
            "biomale",
            "gendermale",
            "siblingnumber",
            "classchild_score",
        ],
        "n_analytic": diagnostics["nobs"],
        "effect_metric": "Mean difference in self-love score (abuse vs none)",
        "effect": {
            "estimate": coef,
            "se": se,
            "ci_lower": float(ci_low),
            "ci_upper": float(ci_high),
        },
        "parameters": result.params.to_dict(),
        "diagnostics": diagnostics,
        "seed": ctx.seed,
        "dataset_path": str(ctx.dataset_path),
        "command": ctx.command,
        "phase": "pap_draft_exploratory",
    }


def select_hypotheses(arg_value: str) -> list[str]:
    if arg_value.lower() == "all":
        return ["H1", "H2", "H3"]
    return [arg_value.upper()]


def main():
    args = parse_args()
    config = load_config(args.config)
    seed = args.seed if args.seed is not None else int(config.get("seed", 0))
    dataset_path = resolve_dataset_path(config["paths"]["raw_data"])
    codebook_path = resolve_repo_path(config["paths"]["codebook"])
    alias_map = load_codebook_alias_map(codebook_path)
    df_raw = load_analysis_frame(dataset_path, alias_map)
    prepared = prepare_variables(df_raw)
    ctx = RunContext(
        seed=seed,
        draws=args.draws,
        dataset_path=dataset_path,
        config_path=resolve_repo_path(args.config),
        command="python analysis/code/run_models.py "
        f"--hypothesis {args.hypothesis} --config {args.config} "
        f"--seed {seed} --draws {args.draws} --output-prefix {args.output_prefix}",
    )
    outputs_dir = resolve_repo_path(Path(args.output_prefix).parent)
    outputs_dir.mkdir(parents=True, exist_ok=True)
    prefix = resolve_repo_path(args.output_prefix)
    hyp_ids = select_hypotheses(args.hypothesis)
    runners = {"H1": run_h1, "H2": run_h2, "H3": run_h3}
    for hyp_id in hyp_ids:
        if hyp_id not in runners:
            raise ValueError(f"Unsupported hypothesis '{hyp_id}'.")
        result = runners[hyp_id](prepared, ctx)
        out_path = Path(f"{prefix}_{hyp_id}.json")
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(json.dumps(result, indent=2))
        print(f"Saved {hyp_id} results to {out_path}")


if __name__ == "__main__":
    main()
