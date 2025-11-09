#!/usr/bin/env python3
"""Negative control check for PAP-confirmed hypotheses."""

from __future__ import annotations

import argparse
import json
import math
import sys
from importlib import util
from pathlib import Path
from types import ModuleType
from typing import Any

import statsmodels.api as sm


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run a negative control check.")
    parser.add_argument(
        "--config",
        default="config/agent_config.yaml",
        help="Agent configuration YAML path.",
    )
    parser.add_argument(
        "--seed",
        type=int,
        help="Seed for reproducibility (defaults to config value).",
    )
    parser.add_argument(
        "--output",
        default="outputs/negative_control.json",
        help="Path to write the summary JSON.",
    )
    return parser.parse_args()


def load_run_models_module(repo_root: Path) -> ModuleType:
    spec_path = repo_root / "analysis" / "code" / "run_models.py"
    spec = util.spec_from_file_location("run_models", str(spec_path))
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load run_models module at {spec_path}.")
    module = util.module_from_spec(spec)
    sys.modules[spec.name] = module  # register so dataclass decorator sees the module
    spec.loader.exec_module(module)  # type: ignore[attr-defined]
    return module  # type: ignore[return-value]


def norm_cdf(x: float) -> float:
    return (1 + math.erf(x / math.sqrt(2))) / 2


def two_sided_pvalue(estimate: float, se: float) -> float:
    if se == 0 or math.isnan(estimate) or math.isnan(se):
        return float("nan")
    z = estimate / se
    return 2 * (1 - norm_cdf(abs(z)))


def main() -> None:
    args = parse_args()
    repo_root = Path(__file__).resolve().parents[2]
    run_models = load_run_models_module(repo_root)

    config = run_models.load_config(run_models.resolve_repo_path(args.config))
    seed = args.seed if args.seed is not None else int(config.get("seed", 0))
    dataset_path = run_models.resolve_dataset_path(config["paths"]["raw_data"])
    codebook_path = run_models.resolve_repo_path(config["paths"]["codebook"])
    alias_map = run_models.load_codebook_alias_map(codebook_path)
    df_raw = run_models.load_analysis_frame(dataset_path, alias_map)
    prepared = run_models.prepare_variables(df_raw)

    predictor = "externalreligion_ord"
    outcome = "siblingnumber"
    controls = ["selfage", "biomale", "gendermale", "cis", "classchild_score"]
    selected = [predictor, outcome] + controls
    data = prepared[selected].dropna()
    exog_cols = [predictor] + controls
    exog = run_models.add_constant(data[exog_cols])
    y = data[outcome]
    model = sm.OLS(y, exog)
    result = model.fit(cov_type="HC1")

    coef = float(result.params[predictor])
    se = float(result.bse[predictor])
    ci_low, ci_high = result.conf_int().loc[predictor].tolist()
    p_value = two_sided_pvalue(coef, se)
    diagnostics = {
        "nobs": int(result.nobs),
        "r_squared": float(result.rsquared),
        "adj_r_squared": float(result.rsquared_adj),
    }

    summary: dict[str, Any] = {
        "hypothesis_id": "NC1",
        "family": "negative_control",
        "targeted": "N",
        "model": "linear_regression",
        "outcome": outcome,
        "predictor": predictor,
        "controls": controls,
        "n_analytic": diagnostics["nobs"],
        "effect_metric": "Sibling count change per one-point rise in religious importance",
        "effect": {
            "estimate": coef,
            "se": se,
            "ci_lower": float(ci_low),
            "ci_upper": float(ci_high),
            "p_value": p_value,
        },
        "diagnostics": diagnostics,
        "seed": seed,
        "dataset_path": str(dataset_path),
        "command": (
            f"python analysis/code/negative_control.py --config {args.config} "
            f"--seed {seed} --output {args.output}"
        ),
        "notes": "Falsification check without a theoretical link; expected null effect.",
        "phase": "analysis",
    }

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(summary, indent=2))
    print(f"Saved negative control summary to {output_path}")


if __name__ == "__main__":
    main()
