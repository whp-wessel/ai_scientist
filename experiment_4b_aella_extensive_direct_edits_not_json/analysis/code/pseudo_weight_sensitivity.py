#!/usr/bin/env python3
"""Explore how pseudo weights with varying design effects shift the confirmatory estimates."""

from __future__ import annotations

import argparse
import json
import math
from importlib import util
from pathlib import Path
from types import ModuleType
import sys

import numpy as np
import pandas as pd


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Pseudo-weight sensitivity for H1–H3")
    parser.add_argument(
        "--config",
        default="config/agent_config.yaml",
        help="Agent configuration YAML path.",
    )
    parser.add_argument(
        "--scenarios",
        nargs="+",
        type=float,
        default=[1.0, 1.25, 1.5],
        help="Design-effect multipliers to simulate (1.0 ↔ SRS).",
    )
    parser.add_argument(
        "--seed",
        type=int,
        help="Deterministic seed (falls back to config seed).",
    )
    parser.add_argument(
        "--draws",
        type=int,
        default=400,
        help="Number of draws for simulation-based summaries (H1).",
    )
    parser.add_argument(
        "--output-dir",
        default="outputs/sensitivity_pseudo_weights",
        help="Directory for pseudo-weight JSON summaries.",
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


def build_context(
    args: argparse.Namespace, module: ModuleType
) -> tuple[pd.DataFrame, module.RunContext, Path]:
    repo_root = Path(__file__).resolve().parents[2]
    config = module.load_config(module.resolve_repo_path(args.config))
    seed = args.seed if args.seed is not None else int(config.get("seed", 0))
    dataset_path = module.resolve_dataset_path(config["paths"]["raw_data"])
    codebook_path = module.resolve_repo_path(config["paths"]["codebook"])
    alias_map = module.load_codebook_alias_map(codebook_path)
    df_raw = module.load_analysis_frame(dataset_path, alias_map)
    prepared = module.prepare_variables(df_raw)
    base_command = (
        f"python analysis/code/pseudo_weight_sensitivity.py --config {args.config} "
        f"--seed {seed} --draws {args.draws} --output-dir {args.output_dir} "
        f"--scenarios {' '.join(str(s) for s in args.scenarios)}"
    )
    ctx = module.RunContext(
        seed=seed,
        draws=args.draws,
        dataset_path=dataset_path,
        config_path=module.resolve_repo_path(args.config),
        command=base_command,
    )
    outputs_dir = module.resolve_repo_path(Path(args.output_dir))
    outputs_dir.mkdir(parents=True, exist_ok=True)
    return prepared, ctx, outputs_dir


def generate_weights(n: int, deff: float, rng: np.random.Generator) -> pd.Series:
    cv2 = max(deff - 1, 0.0)
    sigma = math.sqrt(math.log1p(cv2))
    mu = -0.5 * sigma**2
    if sigma == 0:
        return pd.Series(np.ones(n), dtype=float)
    samples = np.exp(mu + sigma * rng.standard_normal(n))
    return pd.Series(samples, dtype=float)


def summarize_weights(weights: pd.Series) -> dict[str, float]:
    mean = float(weights.mean())
    std = float(weights.std(ddof=0))
    return {
        "mean": mean,
        "std": std,
        "min": float(weights.min()),
        "max": float(weights.max()),
        "cv": float(std / mean) if mean else 0.0,
    }


def run_scenario(
    module: ModuleType,
    prepared: pd.DataFrame,
    base_ctx: module.RunContext,
    outputs_dir: Path,
    scenario_idx: int,
    deff: float,
) -> Path:
    rng_seed = base_ctx.seed + scenario_idx
    rng = np.random.default_rng(rng_seed)
    scenario_df = prepared.copy()
    scenario_df["pseudo_weight"] = generate_weights(len(scenario_df), deff, rng)
    weight_summary = summarize_weights(scenario_df["pseudo_weight"])
    sum_weights = scenario_df["pseudo_weight"].sum()
    sum_sq = (scenario_df["pseudo_weight"] ** 2).sum()
    n_effective = float(sum_weights**2 / sum_sq) if sum_sq > 0 else 0.0
    scenario_command = f"{base_ctx.command} --design-effect {deff:.2f}"
    ctx = module.RunContext(
        seed=base_ctx.seed,
        draws=base_ctx.draws,
        dataset_path=base_ctx.dataset_path,
        config_path=base_ctx.config_path,
        command=scenario_command,
    )
    results = []
    runners = [
        ("H1", module.run_h1),
        ("H2", module.run_h2),
        ("H3", module.run_h3),
    ]
    for hyp_id, runner in runners:
        result = runner(scenario_df, ctx, weight_col="pseudo_weight")
        result["design_effect"] = deff
        result["scenario"] = "pseudo_weight"
        result["weight_seed"] = rng_seed
        results.append(result)
    payload = {
        "scenario_id": f"pseudo_weights_deff_{int(deff * 100):03d}",
        "design_effect": deff,
        "seed": base_ctx.seed,
        "rng_seed": rng_seed,
        "n": int(len(scenario_df)),
        "weight_summary": weight_summary,
        "n_effective": n_effective,
        "command": scenario_command,
        "results": results,
    }
    output_path = outputs_dir / f"{payload['scenario_id']}.json"
    output_path.write_text(json.dumps(payload, indent=2))
    print(f"Saved pseudo-weight scenario {deff:.2f} to {output_path}")
    return output_path


def main() -> None:
    args = parse_args()
    repo_root = Path(__file__).resolve().parents[2]
    module = load_run_models_module(repo_root)
    prepared, ctx, outputs_dir = build_context(args, module)
    for idx, deff in enumerate(args.scenarios):
        run_scenario(module, prepared, ctx, outputs_dir, idx, deff)


if __name__ == "__main__":
    main()
