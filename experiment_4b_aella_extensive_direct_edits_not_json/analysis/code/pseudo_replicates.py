#!/usr/bin/env python3
"""Estimate replicate-based uncertainty by sequentially omitting pseudo-clusters."""

from __future__ import annotations

import argparse
import json
from importlib import util
from pathlib import Path
from types import ModuleType
from typing import Any
import sys

import math
import numpy as np
import pandas as pd


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Pseudo-replicate estimator for H1–H3.")
    parser.add_argument(
        "--config",
        default="config/agent_config.yaml",
        help="Agent configuration YAML.",
    )
    parser.add_argument(
        "--k",
        type=int,
        default=6,
        help="Number of pseudo-clusters to cycle through for jackknife replicates.",
    )
    parser.add_argument(
        "--seed",
        type=int,
        help="Seed for deterministic cluster assignment (defaults to config seed).",
    )
    parser.add_argument(
        "--output-dir",
        default="outputs/sensitivity_replicates",
        help="Directory for replicate summaries.",
    )
    parser.add_argument(
        "--results",
        default="analysis/results.csv",
        help="Confirmatory results CSV for base estimates.",
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
) -> tuple[pd.DataFrame, module.RunContext, dict[str, float], Path]:
    repo_root = Path(__file__).resolve().parents[2]
    config = module.load_config(module.resolve_repo_path(args.config))
    seed = args.seed if args.seed is not None else int(config.get("seed", 0))
    dataset_path = module.resolve_dataset_path(config["paths"]["raw_data"])
    codebook_path = module.resolve_repo_path(config["paths"]["codebook"])
    alias_map = module.load_codebook_alias_map(codebook_path)
    df_raw = module.load_analysis_frame(dataset_path, alias_map)
    prepared = module.prepare_variables(df_raw)
    base_command = (
        f"python analysis/code/pseudo_replicates.py --config {args.config} --seed {seed} "
        f"--k {args.k} --output-dir {args.output_dir}"
    )
    ctx = module.RunContext(
        seed=seed,
        draws=400,
        dataset_path=dataset_path,
        config_path=module.resolve_repo_path(args.config),
        command=base_command,
    )
    base_results = pd.read_csv(module.resolve_repo_path(args.results))
    base_lookup = {
        row["hypothesis_id"]: float(row["estimate"])
        for _, row in base_results[
            base_results["targeted"].astype(str).str.upper() == "Y"
        ].iterrows()
    }
    outputs_dir = module.resolve_repo_path(Path(args.output_dir))
    outputs_dir.mkdir(parents=True, exist_ok=True)
    return prepared, ctx, base_lookup, outputs_dir


def assign_clusters(prepared: pd.DataFrame, k: int) -> pd.Series:
    combined = (
        prepared[["classchild_score", "classcurrent_score"]]
        .fillna(0.0)
        .sum(axis=1)
    )
    ranks = combined.rank(method="first") - 1
    return (ranks.astype(int) % k).astype(int)


def run_replicate(
    module: ModuleType,
    prepared: pd.DataFrame,
    ctx: module.RunContext,
    cluster_id: int,
    k: int,
) -> dict[str, Any]:
    subset = prepared[prepared["_cluster_id"] != cluster_id].copy()
    command = f"{ctx.command} --replicate {cluster_id + 1} (k={k})"
    local_ctx = module.RunContext(
        seed=ctx.seed,
        draws=ctx.draws,
        dataset_path=ctx.dataset_path,
        config_path=ctx.config_path,
        command=command,
    )
    results = {
        "H1": module.run_h1(subset, local_ctx),
        "H2": module.run_h2(subset, local_ctx),
        "H3": module.run_h3(subset, local_ctx),
    }
    return {
        "cluster_left_out": int(cluster_id),
        "n_used": int(len(subset)),
        "results": results,
        "command": command,
    }


def aggregate_replicates(
    replicate_outputs: list[dict[str, Any]],
    base_estimates: dict[str, float],
    k: int,
) -> dict[str, Any]:
    hypothesis_data: dict[str, dict[str, Any]] = {}
    for hyp in base_estimates:
        hypothesis_data[hyp] = {
            "base_estimate": base_estimates[hyp],
            "replicates": [],
        }
    for rep in replicate_outputs:
        for hyp, result in rep["results"].items():
            hypothesis_data[hyp]["replicates"].append(
                {
                    "replicate": rep["cluster_left_out"] + 1,
                    "cluster_left_out": rep["cluster_left_out"],
                    "estimate": result["effect"]["estimate"],
                    "n_used": rep["n_used"],
                    "command": result["command"],
                }
            )
    for hyp, content in hypothesis_data.items():
        estimates = [row["estimate"] for row in content["replicates"]]
        theta_bar = content["base_estimate"]
        var_rep = sum((x - theta_bar) ** 2 for x in estimates) / max(k - 1, 1)
        hypothesis_data[hyp]["replicate_variance"] = var_rep
        hypothesis_data[hyp]["replicate_se"] = math.sqrt(var_rep)
    return hypothesis_data


def main() -> None:
    args = parse_args()
    repo_root = Path(__file__).resolve().parents[2]
    module = load_run_models_module(repo_root)
    prepared, ctx, base_estimates, outputs_dir = build_context(args, module)
    prepared["_cluster_id"] = assign_clusters(prepared, args.k)
    cluster_summary = (
        prepared["_cluster_id"]
        .value_counts()
        .sort_index()
        .rename("size")
        .to_dict()
    )
    replicate_outputs = []
    for cluster in sorted(prepared["_cluster_id"].unique()):
        replicate_outputs.append(run_replicate(module, prepared, ctx, cluster, args.k))
    aggregated = aggregate_replicates(replicate_outputs, base_estimates, args.k)
    payload = {
        "seed": ctx.seed,
        "k": args.k,
        "cluster_summary": {int(k): int(v) for k, v in cluster_summary.items()},
        "replicate_outputs": replicate_outputs,
        "aggregated": aggregated,
        "command": ctx.command,
    }
    output_path = outputs_dir / "sensitivity_replicates_summary.json"
    output_path.write_text(json.dumps(payload, indent=2))
    print(f"Wrote pseudo-replicates summary to {output_path}")


if __name__ == "__main__":
    main()
