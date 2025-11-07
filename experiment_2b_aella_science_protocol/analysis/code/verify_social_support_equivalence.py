#!/usr/bin/env python3
"""
Assess equivalence between social-support items identified by instrument codes.

Regeneration example:
python analysis/code/verify_social_support_equivalence.py \
    --dataset data/clean/childhoodbalancedpublic_with_csa_indicator.csv \
    --out-summary tables/social_support_equivalence_summary.csv \
    --out-distribution tables/social_support_equivalence_distributions.csv \
    --out-overlap tables/social_support_instrument_overlap.csv \
    --config config/agent_config.yaml \
    --columns \
    "In general, people in my *current* social circles tend treat me really well (tmt46e6)" \
    "In general, people in my *current* social circles tend to treat me really well (71mn55g)"
"""

from __future__ import annotations

import argparse
import json
import random
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List, Sequence, Tuple

import numpy as np
import pandas as pd
import yaml


@dataclass
class Config:
    seed: int = 0
    small_cell_threshold: int = 10


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Verify whether social support items with different instrument codes align."
    )
    parser.add_argument("--dataset", required=True, help="Input CSV dataset path.")
    parser.add_argument(
        "--out-summary",
        required=True,
        help="Destination CSV for item-level coverage/scale summary.",
    )
    parser.add_argument(
        "--out-distribution",
        required=True,
        help="Destination CSV for response distributions (suppressed where needed).",
    )
    parser.add_argument(
        "--out-overlap",
        required=True,
        help="Destination CSV for overlap matrix of non-missing responses.",
    )
    parser.add_argument(
        "--columns",
        nargs="+",
        required=True,
        help="Column names representing instrument variants to compare.",
    )
    parser.add_argument(
        "--config", required=False, help="Optional config YAML capturing seed/threshold."
    )
    return parser.parse_args()


def load_config(path: str | None) -> Config:
    if path is None:
        return Config()
    config_path = Path(path)
    data = yaml.safe_load(config_path.read_text())
    return Config(
        seed=int(data.get("seed", 0)),
        small_cell_threshold=int(data.get("small_cell_threshold", 10)),
    )


def set_seed(seed: int) -> None:
    random.seed(seed)
    np.random.seed(seed)


def sanitise_columns(columns: Iterable[str]) -> List[str]:
    seen = set()
    ordered: List[str] = []
    for col in columns:
        if col not in seen:
            seen.add(col)
            ordered.append(col)
    return ordered


def parse_prompt_and_code(variable: str) -> Tuple[str, str]:
    if "(" in variable and variable.endswith(")"):
        prompt, code = variable.rsplit("(", 1)
        return prompt.strip(), code.rstrip(")").strip()
    return variable, ""


def build_summary(df: pd.DataFrame, columns: Sequence[str]) -> pd.DataFrame:
    rows = []
    total = len(df)
    for col in columns:
        available = missing = unique = scale_min = scale_max = None
        instrument_code = ""
        prompt = col
        if col in df.columns:
            series = df[col]
            available = int(series.notna().sum())
            missing = total - available
            unique = int(series.nunique(dropna=True))
            if available:
                valid = series.dropna()
                scale_min = float(valid.min())
                scale_max = float(valid.max())
            prompt, instrument_code = parse_prompt_and_code(col)
        else:
            missing = total
            available = 0
            unique = 0
        rows.append(
            {
                "variable": col,
                "prompt": prompt,
                "instrument_code": instrument_code,
                "available_obs": available,
                "missing_obs": missing,
                "missing_pct": round(missing / total, 6) if total else None,
                "unique_values": unique,
                "scale_min": scale_min,
                "scale_max": scale_max,
            }
        )
    return pd.DataFrame(rows)


def suppress(count: int, threshold: int) -> str | int:
    if count < threshold:
        return f"<{threshold}"
    return count


def build_distribution(
    df: pd.DataFrame, columns: Sequence[str], threshold: int
) -> pd.DataFrame:
    frames = []
    for col in columns:
        if col not in df.columns:
            continue
        series = df[col]
        total = int(series.notna().sum())
        if total == 0:
            continue
        counts = series.value_counts(dropna=True).sort_index()
        for value, count in counts.items():
            safe_count = suppress(int(count), threshold)
            pct = None
            if isinstance(safe_count, int) and total:
                pct = round(safe_count / total, 6)
            frames.append(
                {
                    "variable": col,
                    "response_value": float(value),
                    "count": safe_count,
                    "share_within_nonmissing": pct,
                    "nonmissing_total": total,
                }
            )
    return pd.DataFrame(frames)


def build_overlap(df: pd.DataFrame, columns: Sequence[str]) -> pd.DataFrame:
    if len(columns) != 2:
        raise ValueError("Overlap table currently implemented for two columns.")
    a, b = columns
    flags = pd.DataFrame(
        {
            a: df[a].notna() if a in df.columns else False,
            b: df[b].notna() if b in df.columns else False,
        }
    )
    overlap = (
        flags.value_counts()
        .rename("count")
        .reset_index()
        .sort_values(["count"], ascending=False)
    )
    overlap["both_nonmissing"] = overlap[a] & overlap[b]
    overlap.rename(
        columns={a: f"{a}|nonmissing", b: f"{b}|nonmissing"}, inplace=True
    )
    return overlap


def write_metadata(out_path: Path, command: str, config: Config) -> None:
    metadata = {
        "regeneration_command": command,
        "seed": config.seed,
        "small_cell_threshold": config.small_cell_threshold,
    }
    meta_path = out_path.with_suffix(out_path.suffix + ".meta.json")
    meta_path.write_text(json.dumps(metadata, indent=2))


def main() -> None:
    args = parse_args()
    config = load_config(args.config)
    set_seed(config.seed)

    dataset_path = Path(args.dataset)
    summary_path = Path(args.out_summary)
    dist_path = Path(args.out_distribution)
    overlap_path = Path(args.out_overlap)

    columns = sanitise_columns(args.columns)
    df = pd.read_csv(dataset_path, low_memory=False)

    summary = build_summary(df, columns)
    distribution = build_distribution(df, columns, config.small_cell_threshold)
    overlap = build_overlap(df, columns)

    summary_path.parent.mkdir(parents=True, exist_ok=True)
    summary.to_csv(summary_path, index=False)

    distribution_path = dist_path
    distribution_path.parent.mkdir(parents=True, exist_ok=True)
    distribution.to_csv(distribution_path, index=False)

    overlap_path.parent.mkdir(parents=True, exist_ok=True)
    overlap.to_csv(overlap_path, index=False)

    command = (
        "python analysis/code/verify_social_support_equivalence.py "
        f"--dataset {dataset_path} "
        f"--out-summary {summary_path} "
        f"--out-distribution {distribution_path} "
        f"--out-overlap {overlap_path} "
        f"--config {args.config} "
        + " ".join(f'--columns "{col}"' for col in columns)
    )
    write_metadata(summary_path, command, config)


if __name__ == "__main__":
    main()
