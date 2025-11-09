#!/usr/bin/env python3
"""Alternative codings for the frozen PAP hypotheses (H1‑H3)."""

from __future__ import annotations

import argparse
import json
import math
from importlib import util
from pathlib import Path
from types import ModuleType
from typing import Any
import sys

import numpy as np
import pandas as pd
import statsmodels.api as sm
from statsmodels.miscmodels.ordinal_model import OrderedModel, OrderedResults

RUN_MODELS: ModuleType | None = None


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run robustness checks for H1–H3.")
    parser.add_argument(
        "--config",
        default="config/agent_config.yaml",
        help="Agent configuration YAML path.",
    )
    parser.add_argument(
        "--seed",
        type=int,
        help="Random seed (falls back to config=seed).",
    )
    parser.add_argument(
        "--draws",
        type=int,
        default=400,
        help="Draws for simulation-based effect summaries (H1 only).",
    )
    parser.add_argument(
        "--output-dir",
        default="outputs/robustness_loop052",
        help="Directory to write each robustness JSON.",
    )
    return parser.parse_args()


def load_run_models_module(repo_root: Path) -> ModuleType:
    spec_path = repo_root / "analysis" / "code" / "run_models.py"
    spec = util.spec_from_file_location("run_models", str(spec_path))
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load run_models module at {spec_path}.")
    module = util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)  # type: ignore[attr-defined]
    return module  # type: ignore[return-value]


def norm_cdf(x: float) -> float:
    return (1 + math.erf(x / math.sqrt(2))) / 2


def two_sided_pvalue(estimate: float, se: float) -> float:
    if se == 0 or math.isnan(estimate) or math.isnan(se):
        return float("nan")
    z = estimate / se
    return 2 * (1 - norm_cdf(abs(z)))


def build_context(
    args: argparse.Namespace, module: ModuleType
) -> tuple[ModuleType, pd.DataFrame, Any]:
    repo_root = Path(__file__).resolve().parents[2]
    config = module.load_config(module.resolve_repo_path(args.config))
    seed = args.seed if args.seed is not None else int(config.get("seed", 0))
    dataset_path = module.resolve_dataset_path(config["paths"]["raw_data"])
    codebook_path = module.resolve_repo_path(config["paths"]["codebook"])
    alias_map = module.load_codebook_alias_map(codebook_path)
    df_raw = module.load_analysis_frame(dataset_path, alias_map)
    prepared = module.prepare_variables(df_raw)
    ctx = module.RunContext(
        seed=seed,
        draws=args.draws,
        dataset_path=dataset_path,
        config_path=module.resolve_repo_path(args.config),
        command=(
            f"python analysis/code/robustness_checks.py --config {args.config} "
            f"--seed {seed} --draws {args.draws} --output-dir {args.output_dir}"
        ),
    )
    return module, prepared, ctx


def ordered_marginal_effect(
    result: OrderedResults,
    params: np.ndarray,
    exog_low: np.ndarray,
    exog_high: np.ndarray,
    levels: list[float],
    ctx: Any,
) -> dict[str, float]:
    assert RUN_MODELS is not None
    base = RUN_MODELS.expected_score_difference(
        result, params, exog_low, exog_high, levels
    )
    rng = np.random.default_rng(ctx.seed + 303)
    sim_params = RUN_MODELS.simulate_from_cov(
        rng, result.params.values, result.cov_params(), ctx.draws
    )
    samples = [
        RUN_MODELS.expected_score_difference(result, p, exog_low, exog_high, levels)
        for p in sim_params
    ]
    return RUN_MODELS.summarize_effect(samples, base)


def run_h1_high_low(prepared: pd.DataFrame, ctx: Any) -> dict[str, Any]:
    control_candidates = [
        "selfage",
        "biomale",
        "gendermale",
        "cis",
        "classchild_score",
    ]
    assert RUN_MODELS is not None
    available_controls, dropped_controls = RUN_MODELS.select_controls(
        prepared, control_candidates
    )
    cols = ["wz901dj_score", "externalreligion_ord"] + available_controls
    data = prepared[cols].dropna().copy()
    if data.empty:
        raise ValueError("H1 robustness sample empty after dropping missing.")
    high_threshold = RUN_MODELS.RELIGION_ORDER.index("very important")
    data = data.assign(
        external_high=(data["externalreligion_ord"] >= high_threshold).astype(float)
    )
    y_codes, levels = RUN_MODELS.encode_ordered_outcome(data["wz901dj_score"])
    exog = data[["external_high"] + available_controls].copy()
    model = OrderedModel(y_codes, exog, distr="logit")
    result = model.fit(method="bfgs", disp=False, maxiter=1000)
    exog_low = exog.copy()
    exog_low["external_high"] = 0
    exog_high = exog.copy()
    exog_high["external_high"] = 1
    effect_summary = ordered_marginal_effect(
        result,
        result.params.values,
        exog_low.to_numpy(),
        exog_high.to_numpy(),
        levels,
        ctx,
    )
    diagnostics = {
        "nobs": int(result.nobs),
        "llf": float(result.llf),
        "aic": float(result.aic),
        "bic": float(result.bic),
        "converged": bool(result.mle_retvals.get("converged", True)),
    }
    return {
        "hypothesis_id": "H1_high_low",
        "family": "wellbeing_robustness",
        "model": "ordered_logit",
        "outcome": "wz901dj_score",
        "predictor": "external_high",
        "controls": available_controls,
        "dropped_controls": dropped_controls,
        "n_analytic": diagnostics["nobs"],
        "effect_metric": "ΔE[depression score | high vs low religiosity importance]",
        "effect": effect_summary,
        "contrast_values": {"low": 0, "high": 1},
        "ordered_levels": levels,
        "parameters": result.params.to_dict(),
        "diagnostics": diagnostics,
        "seed": ctx.seed,
        "draws": ctx.draws,
        "dataset_path": str(ctx.dataset_path),
        "command": ctx.command,
        "notes": "Binary high/low religiosity predictor instead of the ordinal scale.",
        "phase": "robustness",
    }


def run_h2_continuous(prepared: pd.DataFrame, ctx: Any) -> dict[str, Any]:
    control_candidates = [
        "selfage",
        "biomale",
        "gendermale",
        "classcurrent_score",
        "classteen_score",
        "mentalillness",
    ]
    assert RUN_MODELS is not None
    available_controls, dropped_controls = RUN_MODELS.select_controls(
        prepared, control_candidates
    )
    cols = ["okq5xh8_ord", "pqo6jmj_score"] + available_controls
    data = prepared[cols].dropna()
    if data.empty:
        raise ValueError("H2 continuous sample empty after dropping missing.")
    y = data["okq5xh8_ord"]
    design_cols = ["pqo6jmj_score"] + available_controls
    exog = RUN_MODELS.add_constant(data[design_cols])
    model = sm.OLS(y, exog)
    result = model.fit(cov_type="HC1")
    coef = float(result.params["pqo6jmj_score"])
    se = float(result.bse["pqo6jmj_score"])
    ci_low, ci_high = result.conf_int().loc["pqo6jmj_score"].tolist()
    diagnostics = {
        "nobs": int(result.nobs),
        "r_squared": float(result.rsquared),
        "adj_r_squared": float(result.rsquared_adj),
    }
    return {
        "hypothesis_id": "H2_continuous_health",
        "family": "wellbeing_robustness",
        "model": "linear_regression",
        "outcome": "okq5xh8_ord",
        "predictor": "pqo6jmj_score",
        "controls": available_controls,
        "dropped_controls": dropped_controls,
        "n_analytic": diagnostics["nobs"],
        "effect_metric": "Δhealth score (0-4) per guidance point",
        "effect": {
            "estimate": coef,
            "se": se,
            "ci_lower": float(ci_low),
            "ci_upper": float(ci_high),
            "p_value": two_sided_pvalue(coef, se),
        },
        "diagnostics": diagnostics,
        "seed": ctx.seed,
        "dataset_path": str(ctx.dataset_path),
        "command": ctx.command,
        "notes": "Health coded as continuous 0-4 scale.",
        "phase": "robustness",
    }


def run_h3_teen_abuse(prepared: pd.DataFrame, ctx: Any) -> dict[str, Any]:
    control_candidates = [
        "selfage",
        "biomale",
        "gendermale",
        "siblingnumber",
        "classchild_score",
    ]
    assert RUN_MODELS is not None
    available_controls, dropped_controls = RUN_MODELS.select_controls(
        prepared, control_candidates
    )
    cols = ["self_love_score", "mds78zu_binary", "v1k988q_binary"] + available_controls
    data = prepared[cols].dropna()
    if data.empty:
        raise ValueError("H3 teen abuse sample empty after dropping missing.")
    y = data["self_love_score"]
    design_cols = ["mds78zu_binary", "v1k988q_binary"] + available_controls
    exog = RUN_MODELS.add_constant(data[design_cols])
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
        "hypothesis_id": "H3_teen_abuse_control",
        "family": "psychosocial_robustness",
        "model": "linear_regression",
        "outcome": "self_love_score",
        "predictor": "mds78zu_binary",
        "controls": ["v1k988q_binary"] + available_controls,
        "dropped_controls": dropped_controls,
        "n_analytic": diagnostics["nobs"],
        "effect_metric": "Mean difference in self-love (abuse vs none) controlling for teen abuse",
        "effect": {
            "estimate": coef,
            "se": se,
            "ci_lower": float(ci_low),
            "ci_upper": float(ci_high),
            "p_value": two_sided_pvalue(coef, se),
        },
        "diagnostics": diagnostics,
        "seed": ctx.seed,
        "dataset_path": str(ctx.dataset_path),
        "command": ctx.command,
        "notes": "Controls for teen-stage abuse exposures to gauge cumulative trajectories.",
        "phase": "robustness",
    }


def run_h3_no_perpetration(prepared: pd.DataFrame, ctx: Any) -> dict[str, Any]:
    subset = prepared.copy()
    perp_mask = subset["rapist"].notna() & (subset["rapist"] > 0)
    subset = subset.loc[~perp_mask]
    control_candidates = [
        "selfage",
        "biomale",
        "gendermale",
        "siblingnumber",
        "classchild_score",
    ]
    assert RUN_MODELS is not None
    available_controls, dropped_controls = RUN_MODELS.select_controls(
        subset, control_candidates
    )
    cols = ["self_love_score", "mds78zu_binary"] + available_controls
    data = subset[cols].dropna()
    if data.empty:
        raise ValueError("H3 restricted sample empty after dropping missing.")
    y = data["self_love_score"]
    design_cols = ["mds78zu_binary"] + available_controls
    exog = RUN_MODELS.add_constant(data[design_cols])
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
        "hypothesis_id": "H3_no_perpetration",
        "family": "psychosocial_robustness",
        "model": "linear_regression",
        "outcome": "self_love_score",
        "predictor": "mds78zu_binary",
        "controls": available_controls,
        "dropped_controls": dropped_controls,
        "n_analytic": diagnostics["nobs"],
        "effect_metric": "Mean self-love difference (abuse vs none) restricted to non-perpetrators",
        "effect": {
            "estimate": coef,
            "se": se,
            "ci_lower": float(ci_low),
            "ci_upper": float(ci_high),
            "p_value": two_sided_pvalue(coef, se),
        },
        "diagnostics": diagnostics,
        "seed": ctx.seed,
        "dataset_path": str(ctx.dataset_path),
        "command": ctx.command,
        "notes": "Sample excludes respondents who reported perpetrating any unwanted experience.",
        "phase": "robustness",
    }


def main() -> None:
    args = parse_args()
    repo_root = Path(__file__).resolve().parents[2]
    module = load_run_models_module(repo_root)
    module, prepared, ctx = build_context(args, module)
    global RUN_MODELS
    RUN_MODELS = module
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    jobs = [
        ("robustness_h1_high_low", run_h1_high_low),
        ("robustness_h2_continuous_health", run_h2_continuous),
        ("robustness_h3_teen_abuse", run_h3_teen_abuse),
        ("robustness_h3_no_perpetration", run_h3_no_perpetration),
    ]
    for label, runner in jobs:
        summary = runner(prepared, ctx)
        path = output_dir / f"{label}.json"
        path.write_text(json.dumps(summary, indent=2))
        print(f"Saved {label} summary to {path}")


if __name__ == "__main__":
    main()
