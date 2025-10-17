#!/usr/bin/env python3
"""Executable analysis runner for PAP hypotheses.

Current focus: HYP-003 ordered-logit specification under the SRS assumption.
The script prepares data, applies disclosure safeguards, and fits the
pre-specified model with robust standard errors. Outputs are tagged as
exploratory until the PAP is frozen.

Regenerate (example):
    python analysis/code/run_pap_models.py \
        --hypotheses HYP-003 \
        --mode exploratory \
        --dataset childhoodbalancedpublic_original.csv \
        --config config/agent_config.yaml \
        --seed 20251016
"""
from __future__ import annotations

import argparse
import json
import random
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Tuple

import numpy as np
import pandas as pd
import yaml
from statsmodels.miscmodels.ordinal_model import OrderedModel

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_DATASET = "childhoodbalancedpublic_original.csv"
DEFAULT_CONFIG = REPO_ROOT / "config" / "agent_config.yaml"
DEFAULT_OUTPUT_DIR = REPO_ROOT / "tables"
SMALL_CELL_THRESHOLD = 10


@dataclass
class RunConfig:
    seed: int
    dataset: Path
    mode: str
    hypotheses: List[str]
    output_dir: Path
    cell_threshold: int = SMALL_CELL_THRESHOLD
    config_path: Optional[Path] = None


def load_project_seed(config_path: Path) -> Optional[int]:
    try:
        with config_path.open("r", encoding="utf-8") as fh:
            cfg = yaml.safe_load(fh)
        if isinstance(cfg, dict) and "seed" in cfg:
            return int(cfg["seed"])
    except FileNotFoundError:
        return None
    except Exception as exc:  # pragma: no cover - defensive log
        print(f"Warning: failed to read seed from {config_path}: {exc}")
    return None


def set_global_seed(seed: int) -> None:
    random.seed(seed)
    np.random.seed(seed)


@dataclass
class PreparedData:
    df: pd.DataFrame
    outcome_col: str
    level_order: List[str]
    predictors: List[str]
    metadata: Dict[str, object]


def prepare_hyp003(df: pd.DataFrame, cell_threshold: int) -> PreparedData:
    outcome_raw = "monogamy"
    religion_col = "Do you *currently* actively practice a religion? (902tbll)"
    age_col = "selfage"
    gender_col = "gendermale"
    relationship_candidates = [
        "Are you in a romantic relationship?",
        "Relationships_RelationshipStatus_Binary",
    ]

    required_columns: List[str] = [outcome_raw, religion_col, age_col, gender_col]
    missing_required = [col for col in required_columns if col not in df.columns]
    if missing_required:
        raise ValueError(
            "Missing required columns for HYP-003: " + ", ".join(missing_required)
        )

    use_rel_col: Optional[str] = None
    for candidate in relationship_candidates:
        if candidate in df.columns:
            series = df[candidate]
            if series.notna().sum() >= cell_threshold:
                use_rel_col = candidate
                break
    controls: List[str] = [age_col, gender_col]
    relationship_note: Optional[str] = None
    if use_rel_col:
        controls.append("relationship_status")
        rel_values = df[use_rel_col]
        if rel_values.dtype.kind in {"O", "U"}:
            rel_clean = rel_values.str.strip().str.lower()
            mapping = {"yes": 1, "no": 0}
            rel_numeric = rel_clean.map(mapping)
        else:
            rel_numeric = rel_values
        if rel_numeric.notna().sum() < cell_threshold:
            relationship_note = (
                f"Control {use_rel_col} dropped due to insufficient non-missing observations"
            )
        else:
            df = df.assign(relationship_status=rel_numeric)
    else:
        relationship_note = (
            "No relationship status control available with ≥ cell_threshold observations; "
            "model omits this control for now"
        )

    working = df[[outcome_raw, religion_col, age_col, gender_col]].copy()
    if "relationship_status" in df.columns:
        working = pd.concat([working, df[["relationship_status"]]], axis=1)

    # Drop rows with missing values in required fields
    working = working.dropna()

    # Map outcome to ordered categories
    outcome_map = {
        2.0: "full_monogamy",
        1.0: "leaning_monogamy",
        -1.0: "leaning_nonmonogamy",
        -2.0: "full_nonmonogamy",
    }
    working = working.assign(monogamy_category=working[outcome_raw].map(outcome_map))
    if working["monogamy_category"].isna().any():
        working = working.dropna(subset=["monogamy_category"])
    category_order = [
        "full_nonmonogamy",
        "leaning_nonmonogamy",
        "leaning_monogamy",
        "full_monogamy",
    ]

    # Disclosure control: collapse non-monogamy categories if needed
    collapse_applied = False
    counts = working["monogamy_category"].value_counts()
    if counts.min() < cell_threshold:
        collapse_applied = True
        collapse_map = {
            "full_nonmonogamy": "nonmonogamy",
            "leaning_nonmonogamy": "nonmonogamy",
            "leaning_monogamy": "leaning_monogamy",
            "full_monogamy": "full_monogamy",
        }
        working = working.assign(
            monogamy_category=working["monogamy_category"].map(collapse_map)
        )
        category_order = ["nonmonogamy", "leaning_monogamy", "full_monogamy"]
        post_counts = working["monogamy_category"].value_counts()
        if post_counts.min() < cell_threshold:
            raise ValueError(
                "Outcome categories still below disclosure threshold after collapsing"
            )

    # Predictor coding
    religion_levels = [
        "No",
        "Yes, slightly",
        "Yes, moderately",
        "Yes, very seriously",
    ]
    working["religion_practice"] = pd.Categorical(
        working[religion_col], categories=religion_levels, ordered=True
    )
    working = working[working["religion_practice"].notna()]

    if working.empty:
        raise ValueError("No observations remain after preparing HYP-003 data")

    # Small cell suppression check across outcome x predictor
    crosstab = pd.crosstab(
        working["monogamy_category"], working["religion_practice"], dropna=False
    )
    if (crosstab < cell_threshold).any().any():
        raise ValueError(
            "At least one outcome x predictor cell violates disclosure threshold"
        )

    # Encode outcome as ordered categorical
    working["monogamy_category"] = pd.Categorical(
        working["monogamy_category"], categories=category_order, ordered=True
    )

    predictors: List[str] = ["religion_practice", age_col, gender_col]
    if "relationship_status" in working.columns:
        predictors.append("relationship_status")

    metadata: Dict[str, object] = {
        "hypothesis": "HYP-003",
        "n_observations": int(len(working)),
        "cell_threshold": cell_threshold,
        "collapse_applied": collapse_applied,
        "relationship_control": use_rel_col,
        "relationship_note": relationship_note,
        "outcome_counts": counts.to_dict(),
        "crosstab": crosstab.to_dict(),
    }

    return PreparedData(
        df=working,
        outcome_col="monogamy_category",
        level_order=category_order,
        predictors=predictors,
        metadata=metadata,
    )


def fit_ordered_logit(prepped: PreparedData) -> Tuple[object, List[str]]:
    df = prepped.df
    outcome = df[prepped.outcome_col]

    dummy_cols = pd.get_dummies(
        df["religion_practice"], prefix="religion", drop_first=True
    )
    numeric_cols = []
    if "selfage" in prepped.predictors:
        numeric_cols.append("selfage")
    if "gendermale" in prepped.predictors:
        numeric_cols.append("gendermale")
    if "relationship_status" in df.columns and "relationship_status" in prepped.predictors:
        numeric_cols.append("relationship_status")
    exog_parts = [dummy_cols]
    if numeric_cols:
        exog_parts.append(df[numeric_cols])
    exog = pd.concat(exog_parts, axis=1)
    exog = exog.astype(float)

    model = OrderedModel(outcome, exog, distr="logit")
    result = model.fit(method="bfgs", disp=False, maxiter=1000, cov_type="HC1")
    exog_cols = list(exog.columns)
    return result, exog_cols


def extract_coefficients(result) -> pd.DataFrame:
    params = result.params
    bse = result.bse
    z_scores = params / bse
    from scipy import stats

    p_values = 2 * (1 - stats.norm.cdf(np.abs(z_scores)))
    ci_low = params - stats.norm.ppf(0.975) * bse
    ci_high = params + stats.norm.ppf(0.975) * bse

    df = pd.DataFrame(
        {
            "term": params.index,
            "estimate": params.values,
            "std_error": bse,
            "z": z_scores,
            "p_value": p_values,
            "ci_low": ci_low,
            "ci_high": ci_high,
        }
    )
    df.insert(1, "model", "ordered_logit")
    return df


def compute_probabilities(result, exog_cols: Iterable[str], prepped: PreparedData) -> pd.DataFrame:
    df = prepped.df
    prediction_levels = df["religion_practice"].cat.categories
    ref_means: Dict[str, float] = {
        "selfage": float(df["selfage"].mean()),
        "gendermale": float(df["gendermale"].mean()),
    }
    if "relationship_status" in df.columns:
        ref_means["relationship_status"] = float(df["relationship_status"].mean())

    rows = []
    for level in prediction_levels:
        row_dict = {k: v for k, v in ref_means.items()}
        row_dict["religion_practice"] = level
        rows.append(row_dict)
    pred_df = pd.DataFrame(rows)
    pred_df["religion_practice"] = pd.Categorical(
        pred_df["religion_practice"],
        categories=df["religion_practice"].cat.categories,
        ordered=True,
    )

    dummy = pd.get_dummies(
        pred_df["religion_practice"], prefix="religion", drop_first=True
    )
    numeric_cols = [col for col in ref_means.keys()]
    exog_parts = [dummy]
    if numeric_cols:
        exog_parts.append(pred_df[numeric_cols])
    exog_pred = pd.concat(exog_parts, axis=1)
    exog_pred = exog_pred.reindex(columns=list(exog_cols), fill_value=0.0)
    exog_pred = exog_pred.astype(float)

    probs = result.model.predict(result.params, exog=exog_pred, which="prob")
    prob_df = pd.DataFrame(probs, columns=prepped.level_order)
    prob_df.insert(0, "religion_practice", prediction_levels)
    return prob_df


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def df_to_markdown(df: pd.DataFrame) -> str:
    headers = list(df.columns)
    header_line = "| " + " | ".join(headers) + " |"
    separator = "| " + " | ".join(["---"] * len(headers)) + " |"
    lines = [header_line, separator]
    for _, row in df.iterrows():
        formatted = []
        for col in headers:
            val = row[col]
            if isinstance(val, (float, np.floating)):
                formatted.append(f"{float(val):.4f}")
            else:
                formatted.append(str(val))
        lines.append("| " + " | ".join(formatted) + " |")
    return "\n".join(lines)


def save_outputs(
    coeffs: pd.DataFrame,
    probs: pd.DataFrame,
    metadata: Dict[str, object],
    output_dir: Path,
    mode: str,
) -> List[Path]:
    ensure_dir(output_dir)
    timestamp = datetime.now(timezone.utc).isoformat()
    stem = f"{mode}_hyp003_ordered_logit"

    coeff_csv = output_dir / f"{stem}_coefficients.csv"
    coeff_md = output_dir / f"{stem}_coefficients.md"
    probs_csv = output_dir / f"{stem}_predicted_probabilities.csv"
    probs_md = output_dir / f"{stem}_predicted_probabilities.md"
    meta_json = output_dir / f"{stem}_metadata.json"

    coeffs.to_csv(coeff_csv, index=False)
    probs.to_csv(probs_csv, index=False)

    coeff_note = (
        f"# {mode.title()} — HYP-003 Ordered Logit Coefficients\n\n"
        f"Generated: {timestamp}\n\n"
        "All estimates assume simple random sampling with unit weights. "
        "Robust standard errors use the HC1 estimator."
    )
    probs_note = (
        f"# {mode.title()} — HYP-003 Category Probabilities\n\n"
        f"Generated: {timestamp}\n\n"
        "Predicted probabilities evaluated at sample means of numeric covariates."
    )

    coeff_md.write_text(coeff_note + "\n\n" + df_to_markdown(coeffs), encoding="utf-8")
    probs_md.write_text(probs_note + "\n\n" + df_to_markdown(probs), encoding="utf-8")

    metadata_record = dict(metadata)
    metadata_record.update(
        {
            "mode": mode,
            "generated": timestamp,
            "outputs": [
                str(coeff_csv.relative_to(REPO_ROOT)),
                str(coeff_md.relative_to(REPO_ROOT)),
                str(probs_csv.relative_to(REPO_ROOT)),
                str(probs_md.relative_to(REPO_ROOT)),
            ],
        }
    )
    meta_json.write_text(json.dumps(metadata_record, indent=2), encoding="utf-8")

    return [coeff_csv, coeff_md, probs_csv, probs_md, meta_json]


def run_hyp003(config: RunConfig, df: pd.DataFrame) -> Dict[str, object]:
    prepared = prepare_hyp003(df, config.cell_threshold)
    result, exog_cols = fit_ordered_logit(prepared)
    coeffs = extract_coefficients(result)
    probs = compute_probabilities(result, exog_cols, prepared)
    outputs = save_outputs(coeffs, probs, prepared.metadata, config.output_dir, config.mode)
    return {
        "outputs": [str(path.relative_to(REPO_ROOT)) for path in outputs],
        "n_obs": prepared.metadata.get("n_observations"),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run PAP analyses for specified hypotheses.")
    parser.add_argument("--hypotheses", nargs="+", default=["HYP-003"], help="Hypothesis IDs to run.")
    parser.add_argument("--dataset", default=DEFAULT_DATASET, help="Dataset path (relative or absolute).")
    parser.add_argument("--config", default=str(DEFAULT_CONFIG), help="Agent config YAML with seed.")
    parser.add_argument("--seed", type=int, default=None, help="Override random seed.")
    parser.add_argument("--mode", choices=["exploratory", "confirmatory"], default="exploratory")
    parser.add_argument(
        "--output-dir",
        default=str(DEFAULT_OUTPUT_DIR),
        help="Directory for result artifacts.",
    )
    parser.add_argument(
        "--cell-threshold",
        type=int,
        default=SMALL_CELL_THRESHOLD,
        help="Disclosure control minimum cell count.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    config_path = Path(args.config)
    config_seed = load_project_seed(config_path) if config_path.exists() else None
    seed = args.seed if args.seed is not None else config_seed
    if seed is None:
        raise ValueError("Seed must be provided via --seed or config file.")
    set_global_seed(seed)

    dataset_path = Path(args.dataset)
    if not dataset_path.is_absolute():
        dataset_path = REPO_ROOT / dataset_path
    if not dataset_path.exists():
        raise FileNotFoundError(f"Dataset not found: {dataset_path}")

    df = pd.read_csv(dataset_path, low_memory=False)

    run_config = RunConfig(
        seed=seed,
        dataset=dataset_path,
        mode=args.mode,
        hypotheses=[h.upper() for h in args.hypotheses],
        output_dir=Path(args.output_dir) if Path(args.output_dir).is_absolute() else REPO_ROOT / args.output_dir,
        cell_threshold=args.cell_threshold,
        config_path=config_path if config_path.exists() else None,
    )

    summary: Dict[str, object] = {
        "dataset": str(run_config.dataset.relative_to(REPO_ROOT)),
        "mode": run_config.mode,
        "seed": run_config.seed,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "hypotheses": run_config.hypotheses,
        "executed": [],
    }

    for hyp in run_config.hypotheses:
        if hyp == "HYP-003":
            result = run_hyp003(run_config, df)
            summary["executed"].append({"hypothesis": hyp, **result})
        else:
            raise NotImplementedError(f"Hypothesis {hyp} not yet implemented")

    manifest_path = run_config.output_dir / f"{run_config.mode}_pap_run_summary.json"
    ensure_dir(run_config.output_dir)
    manifest_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")

    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
