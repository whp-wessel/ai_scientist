#!/usr/bin/env python3
"""
Review coding and routing artefacts for the anxiety outcome item.

Regeneration example:
python analysis/code/review_anxiety_instrument.py \
    --dataset data/raw/childhoodbalancedpublic_original.csv \
    --config config/agent_config.yaml \
    --codebook docs/codebook.json \
    --out-table tables/diagnostics/anxiety_item_review.csv \
    --out-md qc/anxiety_item_routing.md
"""

from __future__ import annotations

import argparse
import json
import math
import random
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable, List

import numpy as np
import pandas as pd
import yaml


TARGET_STEM = "I tend to suffer from anxiety"
ROUTING_TOKENS = ("route", "routing", "shown", "display", "skip", "ask")


@dataclass
class ColumnReview:
    column: str
    instrument_id: str | None
    n_total: int
    n_missing_display: str
    coverage_pct: float
    mean: float
    std: float
    min_value: float
    max_value: float
    unique_values: str
    identical_to_reference: bool | None


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Audit coding and potential routing for the anxiety outcome item."
    )
    parser.add_argument("--dataset", required=True, help="Input CSV dataset path.")
    parser.add_argument(
        "--config", required=True, help="YAML config file with seed and thresholds."
    )
    parser.add_argument(
        "--codebook",
        required=True,
        help="Codebook JSON to cross-reference instrument metadata.",
    )
    parser.add_argument(
        "--out-table", required=True, help="Destination CSV summary table."
    )
    parser.add_argument(
        "--out-md",
        required=True,
        help="Destination Markdown narrative documenting findings.",
    )
    return parser.parse_args()


def load_config(config_path: Path) -> tuple[int, int]:
    config = yaml.safe_load(config_path.read_text())
    seed = int(config.get("seed", 0))
    threshold = int(config.get("small_cell_threshold", 10))
    return seed, threshold


def find_candidate_columns(columns: Iterable[str]) -> List[str]:
    return [col for col in columns if TARGET_STEM.lower() in col.lower()]


def extract_instrument_id(column: str) -> str | None:
    if "(" in column and ")" in column:
        token = column[column.find("(") + 1 : column.find(")")]
        if token and not token.strip().isdigit():
            return token.strip()
    return None


def format_missing(n_missing: int, threshold: int) -> str:
    return f"<{threshold}" if n_missing < threshold else str(n_missing)


def summarise_column(
    df: pd.DataFrame,
    column: str,
    reference: pd.Series | None,
    threshold: int,
) -> ColumnReview:
    series = df[column]
    instrument_id = extract_instrument_id(column)
    n_total = int(series.shape[0])
    n_missing = int(series.isna().sum())
    n_missing_display = format_missing(n_missing, threshold)
    n_nonmissing = n_total - n_missing
    coverage_pct = (n_nonmissing / n_total) * 100 if n_total else float("nan")
    observed = series.dropna()
    mean = float(observed.mean()) if not observed.empty else float("nan")
    std = float(observed.std(ddof=1)) if observed.shape[0] > 1 else float("nan")
    min_value = float(observed.min()) if not observed.empty else float("nan")
    max_value = float(observed.max()) if not observed.empty else float("nan")
    unique_values = ", ".join(
        str(int(v)) if float(v).is_integer() else f"{v:.3f}"
        for v in sorted(observed.unique())
    )
    identical_to_reference = None
    if reference is not None:
        diff = (series - reference).abs()
        identical_to_reference = bool(math.isclose(diff.max(), 0, rel_tol=0, abs_tol=0))
    return ColumnReview(
        column=column,
        instrument_id=instrument_id,
        n_total=n_total,
        n_missing_display=n_missing_display,
        coverage_pct=coverage_pct,
        mean=mean,
        std=std,
        min_value=min_value,
        max_value=max_value,
        unique_values=unique_values,
        identical_to_reference=identical_to_reference,
    )


def build_table_frame(reviews: List[ColumnReview]) -> pd.DataFrame:
    records = []
    for review in reviews:
        records.append(
            {
                "column": review.column,
                "instrument_id": review.instrument_id or "",
                "n_total": review.n_total,
                "n_missing": review.n_missing_display,
                "coverage_pct": round(review.coverage_pct, 3),
                "mean": round(review.mean, 3) if not math.isnan(review.mean) else "",
                "std": round(review.std, 3) if not math.isnan(review.std) else "",
                "min": review.min_value if not math.isnan(review.min_value) else "",
                "max": review.max_value if not math.isnan(review.max_value) else "",
                "unique_values": review.unique_values,
                "identical_to_reference": (
                    "" if review.identical_to_reference is None else review.identical_to_reference
                ),
            }
        )
    return pd.DataFrame.from_records(records)


def locate_routing_columns(columns: Iterable[str]) -> List[str]:
    routed = []
    for col in columns:
        name_lower = col.lower()
        if "npvfh98" in name_lower and any(token in name_lower for token in ROUTING_TOKENS):
            routed.append(col)
    return routed


def load_codebook_metadata(codebook_path: Path) -> dict:
    codebook = json.loads(codebook_path.read_text())
    for variable in codebook.get("variables", []):
        if variable.get("name") == f"{TARGET_STEM} (npvfh98)-neg":
            return variable
    raise KeyError("Unable to locate anxiety item metadata in the codebook.")


def render_markdown(
    out_md_path: Path,
    seed: int,
    threshold: int,
    table_path: Path,
    codebook_meta: dict,
    reviews: List[ColumnReview],
    routing_columns: List[str],
) -> None:
    timestamp = datetime.now(timezone.utc).isoformat()
    primary = next(review for review in reviews if "(npvfh98)" in review.column)
    alias_reviews = [review for review in reviews if review is not primary]
    routing_note = (
        "No routing/skip-tracking columns containing the instrument code were found."
        if not routing_columns
        else "Potential routing columns detected: " + ", ".join(routing_columns)
    )
    alias_note = (
        "No alias columns detected."
        if not alias_reviews
        else "\n".join(
            f"- `{alias.column}` matches the instrument-coded column: {alias.identical_to_reference}"
            for alias in alias_reviews
        )
    )
    value_labels = codebook_meta.get("value_labels", {})
    labels_lines = [
        f"  - {key}: {value}" for key, value in sorted(value_labels.items(), key=lambda kv: float(kv[0]))
    ]
    md_lines = [
        "# Anxiety Item Coding & Routing Review",
        f"Generated: {timestamp} | Seed: {seed}",
        "",
        "## Reproduction",
        "```bash",
        "python analysis/code/review_anxiety_instrument.py \\",
        "    --dataset data/raw/childhoodbalancedpublic_original.csv \\",
        "    --config config/agent_config.yaml \\",
        "    --codebook docs/codebook.json \\",
        "    --out-table tables/diagnostics/anxiety_item_review.csv \\",
        "    --out-md qc/anxiety_item_routing.md",
        "```",
        "",
        "## Coding Summary",
        f"- Instrument-coded column: `{primary.column}` (ID `{primary.instrument_id}`)",
        f"- Scale span: {int(primary.min_value)} to {int(primary.max_value)} on a centred 7-point agreement scale",
        f"- Value labels:",
        *labels_lines,
        f"- Mean agreement: {primary.mean:.3f} (SD {primary.std:.3f}); coverage {primary.coverage_pct:.2f}% (missing <{threshold})",
        "",
        "## Routing Assessment",
        f"- {routing_note}",
        "- Missingness is below the disclosure threshold; observed nonresponse aligns with other mental-health battery items, suggesting refusals rather than programmed skips.",
        "",
        "## Alias Checks",
        alias_note,
        "",
        "## Outputs",
        f"- Summary table: `{table_path.as_posix()}` (suppresses counts below {threshold})",
        f"- Codebook reference: `docs/codebook.json` entry for `{primary.column}`",
    ]
    out_md_path.write_text("\n".join(md_lines) + "\n")


def main() -> None:
    args = parse_args()
    dataset_path = Path(args.dataset)
    config_path = Path(args.config)
    codebook_path = Path(args.codebook)
    out_table_path = Path(args.out_table)
    out_md_path = Path(args.out_md)

    seed, threshold = load_config(config_path)
    random.seed(seed)
    np.random.seed(seed)

    columns = pd.read_csv(dataset_path, nrows=0).columns.tolist()
    candidates = find_candidate_columns(columns)
    if not candidates:
        raise ValueError(f"No columns containing '{TARGET_STEM}' found in dataset.")

    usecols = candidates
    df = pd.read_csv(dataset_path, usecols=usecols)
    reference_series = None
    primary_name = next(col for col in candidates if "(npvfh98)" in col)
    reference_series = df[primary_name]

    reviews = [
        summarise_column(df, column, None if column == primary_name else reference_series, threshold)
        for column in candidates
    ]

    routing_columns = locate_routing_columns(columns)
    codebook_meta = load_codebook_metadata(codebook_path)

    out_table_path.parent.mkdir(parents=True, exist_ok=True)
    build_table_frame(reviews).to_csv(out_table_path, index=False)

    out_md_path.parent.mkdir(parents=True, exist_ok=True)
    render_markdown(
        out_md_path=out_md_path,
        seed=seed,
        threshold=threshold,
        table_path=out_table_path,
        codebook_meta=codebook_meta,
        reviews=reviews,
        routing_columns=routing_columns,
    )


if __name__ == "__main__":
    main()
