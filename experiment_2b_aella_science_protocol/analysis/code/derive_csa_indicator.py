#!/usr/bin/env python3
"""
Derive a binary CSA exposure indicator and validate its distribution with suppression.

Regeneration example:
python analysis/code/derive_csa_indicator.py \
    --dataset data/raw/childhoodbalancedpublic_original.csv \
    --out-dataset data/clean/childhoodbalancedpublic_with_csa_indicator.csv \
    --out-distribution tables/csa_indicator_distribution.csv \
    --config config/agent_config.yaml \
    --codebook-in docs/codebook.json \
    --codebook-out docs/codebook.json
"""

from __future__ import annotations

import argparse
import json
import random
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Tuple

import numpy as np
import pandas as pd
import yaml


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Create CSA exposure indicator (CSA_score > 0) and distribution table."
    )
    parser.add_argument("--dataset", required=True, help="Input CSV dataset path.")
    parser.add_argument(
        "--out-dataset",
        required=True,
        help="Destination CSV for dataset with CSA_score_indicator.",
    )
    parser.add_argument(
        "--out-distribution",
        required=True,
        help="Destination CSV summarising CSA_score_indicator distribution.",
    )
    parser.add_argument("--config", required=True, help="Path to agent_config.yaml.")
    parser.add_argument(
        "--codebook-in",
        required=True,
        help="Input codebook JSON file to extend with indicator metadata.",
    )
    parser.add_argument(
        "--codebook-out",
        required=True,
        help="Output codebook JSON file including indicator metadata.",
    )
    return parser.parse_args()


def load_config(path: Path) -> Tuple[int, int]:
    config = yaml.safe_load(path.read_text())
    seed = int(config.get("seed", 0))
    threshold = int(config.get("small_cell_threshold", 10))
    return seed, threshold


def suppress_count(count: int, threshold: int, total: int) -> Tuple[str, str, str]:
    if count == 0 or count >= threshold:
        pct = f"{(count / total) * 100:.2f}%"
        return str(count), pct, "ok"
    upper_pct = (threshold / total) * 100
    return f"<{threshold}", f"<{upper_pct:.2f}%", "suppressed"


def enrich_codebook(
    codebook_path: Path,
    output_path: Path,
    indicator_stats: Dict[str, float],
    seed: int,
) -> None:
    codebook = json.loads(codebook_path.read_text())
    variables = codebook.setdefault("variables", [])
    existing = {entry.get("name"): entry for entry in variables}

    indicator_entry = existing.get("CSA_score_indicator")
    summary_stats = {
        "count": float(indicator_stats["count"]),
        "mean": float(indicator_stats["mean"]),
        "std": float(indicator_stats["std"]),
        "min": float(indicator_stats["min"]),
        "q1": float(indicator_stats["q1"]),
        "median": float(indicator_stats["median"]),
        "q3": float(indicator_stats["q3"]),
        "max": float(indicator_stats["max"]),
        "n_missing": int(indicator_stats["n_missing"]),
        "unique": int(indicator_stats["unique"]),
    }

    note = (
        f"Binary indicator derived {datetime.now(timezone.utc).isoformat()} | "
        f"Seed {seed} | Source analysis/code/derive_csa_indicator.py (CSA_score > 0)."
    )

    if indicator_entry is None:
        variables.append(
            {
                "name": "CSA_score_indicator",
                "label": "Any childhood sexual abuse exposure (CSA_score>0)",
                "question_text": None,
                "analysis_role": "predictor",
                "type": "binary",
                "storage": "float64",
                "allowed_values": [0, 1],
                "value_labels": {"0": "No reported exposure", "1": "Reported exposure"},
                "missing_codes": [],
                "summary_stats": summary_stats,
                "notes": note,
            }
        )
    else:
        indicator_entry.update(
            {
                "label": "Any childhood sexual abuse exposure (CSA_score>0)",
                "analysis_role": "predictor",
                "type": "binary",
                "storage": "float64",
                "allowed_values": [0, 1],
                "value_labels": {
                    "0": "No reported exposure",
                    "1": "Reported exposure",
                },
                "missing_codes": [],
                "summary_stats": summary_stats,
                "notes": note,
            }
        )

    previous_regeneration = codebook.get("regeneration")
    codebook["regeneration"] = {
        "command": (
            "python analysis/code/derive_csa_indicator.py "
            "--dataset data/raw/childhoodbalancedpublic_original.csv "
            "--out-dataset data/clean/childhoodbalancedpublic_with_csa_indicator.csv "
            "--out-distribution tables/csa_indicator_distribution.csv "
            "--config config/agent_config.yaml "
            "--codebook-in docs/codebook.json "
            "--codebook-out docs/codebook.json"
        ),
        "seed": seed,
        "created_by": "analysis/code/derive_csa_indicator.py",
    }
    if previous_regeneration:
        history = codebook.setdefault("regeneration_history", [])
        history.append(previous_regeneration)

    output_path.write_text(json.dumps(codebook, indent=2))


def main() -> None:
    args = parse_args()

    dataset_path = Path(args.dataset)
    out_dataset_path = Path(args.out_dataset)
    out_distribution_path = Path(args.out_distribution)
    config_path = Path(args.config)
    codebook_in_path = Path(args.codebook_in)
    codebook_out_path = Path(args.codebook_out)

    seed, threshold = load_config(config_path)
    random.seed(seed)
    np.random.seed(seed)

    df = pd.read_csv(dataset_path, low_memory=False)
    if "CSA_score" not in df.columns:
        raise ValueError("CSA_score column missing from dataset.")

    indicator = np.where(
        df["CSA_score"].notna(), (df["CSA_score"] > 0).astype(float), np.nan
    )
    df["CSA_score_indicator"] = indicator

    out_dataset_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out_dataset_path, index=False)

    total = int(df.shape[0])
    counts = df["CSA_score_indicator"].value_counts(dropna=False).sort_index()
    distribution_rows = []
    for level, count in counts.items():
        if pd.isna(level):
            level_label = "NaN"
        else:
            level_label = int(level)
        display_count, percent, status = (
            ("N/A", "N/A", "missing")
            if pd.isna(level)
            else suppress_count(int(count), threshold, total)
        )
        distribution_rows.append(
            {
                "CSA_score_indicator": level_label,
                "count": display_count,
                "percent": percent,
                "status": status,
            }
        )

    out_distribution_path.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(distribution_rows).to_csv(out_distribution_path, index=False)

    series = df["CSA_score_indicator"]
    indicator_stats = {
        "count": float(series.count()),
        "mean": float(series.mean(skipna=True)),
        "std": float(series.std(skipna=True)),
        "min": float(series.min(skipna=True)),
        "q1": float(series.quantile(0.25)),
        "median": float(series.median(skipna=True)),
        "q3": float(series.quantile(0.75)),
        "max": float(series.max(skipna=True)),
        "n_missing": int(series.isna().sum()),
        "unique": int(series.nunique(dropna=True)),
    }

    enrich_codebook(codebook_in_path, codebook_out_path, indicator_stats, seed)


if __name__ == "__main__":
    main()
