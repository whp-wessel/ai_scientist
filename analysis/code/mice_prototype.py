"""Prototype multiple imputation workflow for key wellbeing and abuse items.

This script performs chained equations imputation using statsmodels' MICE implementation,
writing deterministic outputs seeded from the agent configuration. It produces:
- data/derived/childhoodbalancedpublic_mi_prototype.csv.gz: stacked imputed datasets
- analysis/imputation/mice_variable_map.json: original -> sanitized column names
- analysis/imputation/mice_imputation_summary.csv: aggregate diagnostics (small-cell safe)
- analysis/imputation/mice_prototype_summary.md: narrative summary with regeneration details
- analysis/imputation/mice_prototype_metadata.json: run metadata for reproducibility

Usage
-----
python analysis/code/mice_prototype.py \
    --dataset childhoodbalancedpublic_original.csv \
    --config config/agent_config.yaml \
    --seed 20251016 \
    --n-imputations 20 \
    --burn-in 10
"""

from __future__ import annotations

import argparse
import json
import math
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List

import numpy as np
import pandas as pd
import yaml
from statsmodels.imputation.mice import MICEData


DEFAULT_COLUMNS: List[str] = [
    "selfage",
    "gendermale",
    "biomale",
    "cis",
    "liberal",
    "education",
    "classchild",
    "classteen",
    "classcurrent",
    "networth",
    "mentalillness",
    "religion",
    "Religionchildhood",
    "monogamy",
    "I love myself (2l8994l)",
    "during ages *0-12*: your parents verbally or emotionally abused you (mds78zu)",
]

SMALL_CELL_THRESHOLD = 10


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Prototype multiple imputation workflow")
    parser.add_argument("--dataset", type=Path, required=True, help="Path to CSV dataset")
    parser.add_argument("--config", type=Path, default=Path("config/agent_config.yaml"))
    parser.add_argument("--output-dir", type=Path, default=Path("analysis/imputation"))
    parser.add_argument("--derived-dir", type=Path, default=Path("data/derived"))
    parser.add_argument("--seed", type=int, default=None, help="Random seed (overrides config)")
    parser.add_argument("--n-imputations", type=int, default=20)
    parser.add_argument("--burn-in", type=int, default=10)
    parser.add_argument(
        "--columns",
        nargs="*",
        default=None,
        help="Optional list of columns to include (defaults to curated set)",
    )
    return parser.parse_args()


def load_seed(config_path: Path, seed_override: int | None) -> int:
    if seed_override is not None:
        return seed_override
    config = yaml.safe_load(config_path.read_text())
    return int(config.get("seed", 0))


def sanitize_columns(columns: List[str]) -> Dict[str, str]:
    mapping: Dict[str, str] = {}
    reverse: Dict[str, int] = {}
    for col in columns:
        sanitized = re.sub(r"[^0-9A-Za-z]+", "_", col).strip("_").lower()
        if not sanitized:
            sanitized = "col"
        if sanitized[0].isdigit():
            sanitized = f"col_{sanitized}"
        if sanitized in reverse:
            reverse[sanitized] += 1
            sanitized = f"{sanitized}_{reverse[sanitized]}"
        else:
            reverse[sanitized] = 0
        mapping[col] = sanitized
    return mapping


def mask_small_cells(count: float) -> str:
    if math.isnan(count):
        return "NA"
    if count < SMALL_CELL_THRESHOLD:
        return "<10"
    return f"{int(round(count))}"


def main() -> None:
    args = parse_args()
    dataset_path = args.dataset
    output_dir = args.output_dir
    derived_dir = args.derived_dir
    output_dir.mkdir(parents=True, exist_ok=True)
    derived_dir.mkdir(parents=True, exist_ok=True)

    seed = load_seed(args.config, args.seed)
    np.random.seed(seed)

    columns = args.columns if args.columns else DEFAULT_COLUMNS
    df = pd.read_csv(dataset_path, usecols=columns)

    column_map = sanitize_columns(df.columns.tolist())
    df_sanitized = df.rename(columns=column_map)

    observed_counts = df_sanitized.notna().sum()
    valid_columns = observed_counts[observed_counts > 0].index.tolist()
    dropped_sanitized = sorted(set(df_sanitized.columns) - set(valid_columns))
    dropped_original = [orig for orig, sanit in column_map.items() if sanit in dropped_sanitized]
    if dropped_sanitized:
        df_sanitized = df_sanitized[valid_columns]

    mice_data = MICEData(df_sanitized)

    burn_in = max(args.burn_in, 0)
    for _ in range(burn_in):
        mice_data.update_all()

    imputations: List[pd.DataFrame] = []
    for i in range(args.n_imputations):
        mice_data.update_all()
        completed = mice_data.data.copy()
        completed["imputation_id"] = i + 1
        imputations.append(completed)

    stacked = pd.concat(imputations, ignore_index=True)
    derived_output_path = derived_dir / "childhoodbalancedpublic_mi_prototype.csv.gz"
    stacked.to_csv(derived_output_path, index=False)

    missing_counts = df.isna().sum()
    missing_fraction = (df.isna().sum() / len(df)).round(6)

    summary_records = []
    grouped = stacked.groupby("imputation_id")
    summary_basis = {orig: sanitized for orig, sanitized in column_map.items() if sanitized in df_sanitized.columns}
    for original_name, sanitized in summary_basis.items():
        col_means = grouped[sanitized].mean()
        col_stds = grouped[sanitized].std()
        summary_records.append(
            {
                "variable": original_name,
                "sanitized": sanitized,
                "missing_before_masked": mask_small_cells(float(missing_counts[original_name])),
                "missing_fraction": float(missing_fraction[original_name]),
                "mean_after": float(col_means.mean()),
                "sd_after": float(col_stds.mean()),
            }
        )

    summary_df = pd.DataFrame(summary_records)
    summary_df.to_csv(output_dir / "mice_imputation_summary.csv", index=False)

    mapping_path = output_dir / "mice_variable_map.json"
    mapping_path.write_text(json.dumps(column_map, indent=2))

    run_completed = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

    metadata = {
        "run_completed": run_completed,
        "dataset": str(dataset_path),
        "seed": seed,
        "n_imputations": args.n_imputations,
        "burn_in": burn_in,
        "columns": columns,
        "dropped_all_missing_columns": dropped_original,
        "derived_output": str(derived_output_path),
        "summary_output": str(output_dir / "mice_imputation_summary.csv"),
        "variable_map": str(mapping_path),
        "command": f"python analysis/code/mice_prototype.py --dataset {dataset_path} --config {args.config} --seed {seed} --n-imputations {args.n_imputations} --burn-in {burn_in}",
    }
    (output_dir / "mice_prototype_metadata.json").write_text(json.dumps(metadata, indent=2))

    summary_lines = [
        "# Multiple Imputation Prototype (Exploratory)",
        "",
        f"- Completed: {run_completed}",
        f"- Dataset: `{metadata['dataset']}`",
        f"- Seed: `{seed}`",
        f"- Imputations: {args.n_imputations}",
        f"- Burn-in iterations: {burn_in}",
        f"- Output (stacked imputations): `{metadata['derived_output']}`",
        f"- Summary table: `{metadata['summary_output']}`",
        "- All randomness seeded via NumPy global state.",
        "",
        "## Missingness (Counts masked <10)",
    ]

    if dropped_original:
        summary_lines.append("- Dropped columns with no observed values: " + ", ".join(dropped_original))

    for record in summary_records:
        summary_lines.append(
            f"- {record['variable']}: missing_before={record['missing_before_masked']}, missing_fraction={record['missing_fraction']:.5f}, mean_after={record['mean_after']:.3f}, sd_after={record['sd_after']:.3f}"
        )

    summary_lines.extend(
        [
            "",
            "## Regeneration",
            "```bash",
            metadata["command"],
            "```",
            "",
            "*Exploratory output — do not use for confirmatory analyses without a frozen PAP.*",
        ]
    )

    (output_dir / "mice_prototype_summary.md").write_text("\n".join(summary_lines))


if __name__ == "__main__":
    main()
