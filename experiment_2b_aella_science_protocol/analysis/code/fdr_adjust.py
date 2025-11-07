#!/usr/bin/env python3
"""
Apply Benjamini–Hochberg false discovery rate adjustments to confirmatory results.

Reproducibility
---------------
Deterministic given identical inputs; no randomness is used. The global seed is read
from `config/agent_config.yaml` and logged for traceability.

Typical usage (after confirmatory models populate `analysis/results.csv`):

    python analysis/code/fdr_adjust.py \
        --results analysis/results.csv \
        --hypotheses analysis/hypotheses.csv \
        --family-scope confirmatory \
        --out analysis/results.csv

The script updates the `q_value` column for the targeted hypotheses and writes an
audit table to `tables/fdr_adjustment_confirmatory.csv` by default.
"""

from __future__ import annotations

import argparse
import csv
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List, Sequence, Tuple

import pandas as pd
import yaml

FALLBACK_Q = 0.05
AUDIT_DEFAULT = Path("tables/fdr_adjustment_confirmatory.csv")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Apply Benjamini–Hochberg FDR adjustments to confirmatory hypotheses."
    )
    parser.add_argument(
        "--results",
        default="analysis/results.csv",
        help="CSV containing confirmatory results with at least hypothesis_id and p_value.",
    )
    parser.add_argument(
        "--hypotheses",
        default="analysis/hypotheses.csv",
        help="Hypothesis registry CSV with family/status metadata.",
    )
    parser.add_argument(
        "--config",
        default="config/agent_config.yaml",
        help="Config YAML providing default q threshold and seed.",
    )
    parser.add_argument(
        "--status-filter",
        nargs="+",
        default=["in_PAP", "tested"],
        help="Hypothesis statuses to include (default: in_PAP and tested).",
    )
    parser.add_argument(
        "--family-scope",
        nargs="+",
        default=["confirmatory"],
        help=(
            "Families to adjust. Use 'confirmatory' to reinterpret as hypotheses with "
            "status in the filter; alternatively pass explicit family names."
        ),
    )
    parser.add_argument(
        "--out",
        default=None,
        help="Optional path to write updated results CSV. Defaults to overwrite input.",
    )
    parser.add_argument(
        "--audit-table",
        default=str(AUDIT_DEFAULT),
        help="Path for audit table documenting BH steps.",
    )
    parser.add_argument(
        "--log-level",
        default="INFO",
        help="Logging level (DEBUG, INFO, WARNING, ERROR).",
    )
    return parser.parse_args()


def configure_logging(level: str) -> None:
    logging.basicConfig(
        level=getattr(logging, level.upper(), logging.INFO),
        format="%(asctime)sZ [%(levelname)s] %(message)s",
    )


@dataclass(frozen=True)
class Config:
    seed: int
    fdr_q: float


def load_config(config_path: Path) -> Config:
    with config_path.open("r", encoding="utf-8") as fh:
        raw = yaml.safe_load(fh) or {}
    return Config(
        seed=int(raw.get("seed", 0)),
        fdr_q=float(raw.get("fdr_q", FALLBACK_Q)),
    )


def load_hypotheses(hypothesis_path: Path) -> pd.DataFrame:
    df = pd.read_csv(hypothesis_path)
    expected = {"id", "family", "status"}
    missing = expected - set(df.columns)
    if missing:
        raise ValueError(f"Hypothesis registry missing columns: {missing}")
    return df


def _family_labels(
    df: pd.DataFrame,
    family_scope: Sequence[str],
    status_filter: Sequence[str],
) -> pd.Series:
    if "confirmatory" in family_scope:
        mask = df["status"].isin(status_filter)
        return df.loc[mask, "family"]
    return df.loc[df["family"].isin(family_scope), "family"]


def load_results(results_path: Path) -> pd.DataFrame:
    df = pd.read_csv(results_path)
    expected = {"hypothesis_id", "p_value"}
    missing = expected - set(df.columns)
    if missing:
        raise ValueError(f"Results file missing required columns: {missing}")
    return df


def benjamini_hochberg(p_values: Sequence[float]) -> List[float]:
    """
    Compute BH-adjusted q-values. Ignores NaNs (returns NaN for those entries).
    """
    series = pd.Series(p_values, dtype="float64")
    valid = series.notna()
    p_valid = series[valid]
    if p_valid.empty:
        return series.tolist()

    ranked = p_valid.rank(method="first")
    m = float(len(p_valid))

    adjusted = pd.Series(index=p_valid.index, dtype="float64")
    prev = 1.0
    for idx, p in p_valid.sort_values(ascending=False).items():
        rank = ranked.loc[idx]
        candidate = (m / rank) * p
        prev = min(prev, candidate)
        adjusted.loc[idx] = prev

    series.loc[valid] = adjusted.clip(upper=1.0)
    return series.tolist()


def adjust_family(
    results: pd.DataFrame,
    hypothesis_ids: Iterable[str],
) -> Tuple[pd.Series, pd.DataFrame]:
    subset = results.set_index("hypothesis_id").loc[list(hypothesis_ids)]
    q_values = benjamini_hochberg(subset["p_value"])
    adjusted = subset.assign(q_value=q_values)
    audit = adjusted[["p_value", "q_value"]].copy()
    audit["rank"] = audit["p_value"].rank(method="first")
    audit["sorted_p_value"] = audit["p_value"].sort_values().values
    return adjusted["q_value"], audit


def write_audit_table(path: Path, rows: List[dict]) -> None:
    if not rows:
        logging.info("No rows to write to audit table at %s", path)
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "family",
        "hypothesis_id",
        "p_value",
        "q_value",
        "rank_within_family",
        "seed",
    ]
    with path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def main() -> None:
    args = parse_args()
    configure_logging(args.log_level)

    config = load_config(Path(args.config))
    logging.info("Loaded config seed=%s, fdr_q=%s", config.seed, config.fdr_q)

    results_path = Path(args.results)
    results = load_results(results_path)

    hypo_df = load_hypotheses(Path(args.hypotheses))
    eligible_mask = hypo_df["status"].isin(args.status_filter)
    eligible = hypo_df.loc[eligible_mask, ["id", "family"]].copy()

    target_families = args.family_scope
    if "confirmatory" in target_families:
        logging.info("Interpreting 'confirmatory' scope as statuses: %s", args.status_filter)
        family_labels = eligible
    else:
        family_labels = hypo_df.loc[hypo_df["family"].isin(target_families), ["id", "family"]]

    rows: List[dict] = []
    updated_results = results.copy()

    for family in family_labels["family"].unique():
        ids = family_labels.loc[family_labels["family"] == family, "id"]
        if ids.empty:
            continue
        missing_ids = [hid for hid in ids if hid not in set(results["hypothesis_id"])]
        if missing_ids:
            logging.warning("Skipping family %s due to missing hypotheses: %s", family, missing_ids)
            continue
        q_values, audit = adjust_family(results, ids)
        updated_results.loc[updated_results["hypothesis_id"].isin(ids), "q_value"] = q_values.values
        for hid, row in audit.iterrows():
            rows.append(
                {
                    "family": family,
                    "hypothesis_id": hid,
                    "p_value": row["p_value"],
                    "q_value": row["q_value"],
                    "rank_within_family": int(row["rank"]),
                    "seed": config.seed,
                }
            )

    out_path = Path(args.out) if args.out else results_path
    out_path.parent.mkdir(parents=True, exist_ok=True)
    updated_results.to_csv(out_path, index=False)
    logging.info("Wrote adjusted results to %s", out_path)

    audit_path = Path(args.audit_table)
    write_audit_table(audit_path, rows)
    logging.info("Wrote audit table to %s", audit_path)


if __name__ == "__main__":
    main()
