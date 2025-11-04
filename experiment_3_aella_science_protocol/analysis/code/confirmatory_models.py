#!/usr/bin/env python3
"""
Execute pre-registered confirmatory models for the childhood balanced public survey.

Reproducibility
--------------
All randomness is seeded by `config/agent_config.yaml` (seed=20251016).
Regenerate provisional confirmatory estimates via:

    python analysis/code/confirmatory_models.py \
        --dataset data/clean/childhoodbalancedpublic_with_csa_indicator.csv \
        --config config/agent_config.yaml \
        --survey-design docs/survey_design.yaml \
        --results-csv analysis/results.csv \
        --hypotheses HYP-001 HYP-003

The script is deterministic given identical inputs and environment.
"""

from __future__ import annotations

import argparse
import logging
import random
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Iterable, List, Sequence

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf
import yaml

RESULT_COLUMNS: List[str] = [
    "hypothesis_id",
    "model",
    "n_unweighted",
    "n_weighted",
    "estimate",
    "se",
    "ci_low",
    "ci_high",
    "p_value",
    "q_value",
    "effect_size_metric",
    "robustness_passed",
    "limitations",
    "confidence_rating",
    "analysis_timestamp",
    "seed",
]


def _needs_quote(name: str) -> bool:
    return not re.match(r"^[A-Za-z_][A-Za-z0-9_]*$", name)


def _quote(name: str) -> str:
    return f'Q("{name}")'


@dataclass(frozen=True)
class HypothesisSpec:
    hypothesis_id: str
    outcome: str
    predictor: str
    controls: Sequence[str]
    estimand: str
    effect_size_metric: str
    model_label: str

    def required_columns(self) -> List[str]:
        return [self.outcome, self.predictor, *self.controls]

    def formula(self) -> str:
        lhs = _quote(self.outcome)
        tokens = [self.predictor if not _needs_quote(self.predictor) else _quote(self.predictor)]
        for control in self.controls:
            tokens.append(control if not _needs_quote(control) else _quote(control))
        rhs = " + ".join(tokens)
        return f"{lhs} ~ {rhs}"

    def predictor_term(self) -> str:
        return self.predictor if not _needs_quote(self.predictor) else _quote(self.predictor)


HYPOTHESES: Dict[str, HypothesisSpec] = {
    "HYP-001": HypothesisSpec(
        hypothesis_id="HYP-001",
        outcome="I love myself (2l8994l)",
        predictor="classchild",
        controls=["selfage", "gendermale", "cis"],
        estimand="Slope of childhood class predicting self-love",
        effect_size_metric="slope_per_unit",
        model_label="ols_hc3_srs",
    ),
    "HYP-003": HypothesisSpec(
        hypothesis_id="HYP-003",
        outcome="I tend to suffer from anxiety (npvfh98)-neg",
        predictor="CSA_score_indicator",
        controls=["selfage", "gendermale", "classchild"],
        estimand="Mean difference in anxiety for any CSA exposure",
        effect_size_metric="difference_in_means",
        model_label="ols_hc3_srs",
    ),
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run pre-registered confirmatory models under SRS assumptions."
    )
    parser.add_argument(
        "--dataset",
        default="data/clean/childhoodbalancedpublic_with_csa_indicator.csv",
        help="Input dataset with derived variables.",
    )
    parser.add_argument(
        "--config",
        default="config/agent_config.yaml",
        help="YAML config containing global seed and defaults.",
    )
    parser.add_argument(
        "--survey-design",
        default="docs/survey_design.yaml",
        help="Survey design metadata (documenting SRS assumption).",
    )
    parser.add_argument(
        "--hypotheses",
        nargs="+",
        default=list(HYPOTHESES.keys()),
        help="Hypothesis IDs to evaluate (default: all registered confirmatory hypotheses).",
    )
    parser.add_argument(
        "--results-csv",
        default="analysis/results.csv",
        help="Path to results CSV to create/update.",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite any existing rows for the targeted hypotheses instead of updating in place.",
    )
    parser.add_argument(
        "--log-level",
        default="INFO",
        help="Logging level (DEBUG, INFO, WARNING, ERROR).",
    )
    return parser.parse_args()


def load_config(path: Path) -> Dict:
    with path.open("r", encoding="utf-8") as fh:
        config = yaml.safe_load(fh)
    return config or {}


def configure_logging(level: str) -> None:
    logging.basicConfig(
        level=getattr(logging, level.upper(), logging.INFO),
        format="%(asctime)s %(levelname)s %(message)s",
    )


def seed_everything(seed: int) -> None:
    random.seed(seed)
    np.random.seed(seed)


def load_dataset(dataset_path: Path, required_columns: Iterable[str]) -> pd.DataFrame:
    if dataset_path.suffix.lower() == ".csv":
        df = pd.read_csv(dataset_path)
    elif dataset_path.suffix.lower() in {".parquet", ".pq"}:
        df = pd.read_parquet(dataset_path)
    else:
        raise ValueError(f"Unsupported dataset format: {dataset_path.suffix}")

    missing = [col for col in required_columns if col not in df.columns]
    if missing:
        raise KeyError(f"Dataset missing required columns: {missing}")
    return df


def run_model_for_spec(df: pd.DataFrame, spec: HypothesisSpec) -> Dict[str, object]:
    logging.info("Running model for %s", spec.hypothesis_id)

    subset = df.loc[:, spec.required_columns()].copy()
    before_drop = len(subset)
    subset = subset.dropna()
    dropped = before_drop - len(subset)
    if dropped:
        logging.info(
            "Dropped %d rows with missing data for %s (%.2f%% of subset).",
            dropped,
            spec.hypothesis_id,
            dropped / before_drop * 100 if before_drop else 0,
        )

    if subset.empty:
        raise ValueError(f"No rows remain after dropna for {spec.hypothesis_id}.")

    formula = spec.formula()
    model = smf.ols(formula=formula, data=subset)
    fitted = model.fit()
    robust = fitted.get_robustcov_results(cov_type="HC3")

    # statsmodels returns NumPy arrays for robust summaries; map onto term names for safe lookup
    term_names = robust.model.exog_names
    params = pd.Series(robust.params, index=term_names)
    ses = pd.Series(robust.bse, index=term_names)
    pvals = pd.Series(robust.pvalues, index=term_names)
    ci_array = robust.conf_int(alpha=0.05)
    ci = pd.DataFrame(ci_array, index=term_names, columns=["ci_low", "ci_high"])

    term = spec.predictor_term()
    estimate = params[term]
    se = ses[term]
    ci_low = float(ci.loc[term, "ci_low"])
    ci_high = float(ci.loc[term, "ci_high"])
    p_value = pvals[term]

    n_unweighted = len(subset)

    result = {
        "hypothesis_id": spec.hypothesis_id,
        "model": spec.model_label,
        "n_unweighted": n_unweighted,
        "n_weighted": float(n_unweighted),
        "estimate": float(estimate),
        "se": float(se),
        "ci_low": float(ci_low),
        "ci_high": float(ci_high),
        "p_value": float(p_value),
        "q_value": None,
        "effect_size_metric": spec.effect_size_metric,
        "robustness_passed": "N",
        "limitations": "",
        "confidence_rating": "Pending",
    }
    return result


def update_results_csv(results_csv: Path, rows: List[Dict[str, object]], seed: int, overwrite: bool) -> None:
    timestamp = datetime.now(tz=timezone.utc).isoformat()
    df_new = pd.DataFrame(rows)
    df_new["analysis_timestamp"] = timestamp
    df_new["seed"] = seed

    if results_csv.exists():
        existing = pd.read_csv(results_csv)
    else:
        existing = pd.DataFrame(columns=RESULT_COLUMNS)

    existing = existing[[c for c in existing.columns if c in RESULT_COLUMNS]]

    if overwrite:
        existing = existing[~existing["hypothesis_id"].isin(df_new["hypothesis_id"])]
    else:
        mask = existing["hypothesis_id"].isin(df_new["hypothesis_id"])
        existing = existing[~mask]

    combined = pd.concat([existing, df_new], ignore_index=True)
    combined = combined[RESULT_COLUMNS]
    combined.sort_values(by="hypothesis_id", inplace=True)
    results_csv.parent.mkdir(parents=True, exist_ok=True)
    combined.to_csv(results_csv, index=False)
    logging.info("Wrote results to %s", results_csv)


def validate_design_assumption(survey_design_path: Path) -> None:
    if not survey_design_path.exists():
        raise FileNotFoundError(
            f"Survey design file {survey_design_path} is required to document SRS assumption."
        )
    with survey_design_path.open("r", encoding="utf-8") as fh:
        design = yaml.safe_load(fh)
    assumed = design.get("assumed_design")
    if assumed != "simple_random_sampling":
        raise ValueError(
            "Confirmatory models currently implemented only for simple random sampling. "
            f"Found assumed_design={assumed!r}."
        )


def main() -> None:
    args = parse_args()
    configure_logging(args.log_level)

    config = load_config(Path(args.config))
    seed = int(config.get("seed", 0) or 0)
    if seed <= 0:
        raise ValueError("Global seed must be a positive integer in config/agent_config.yaml.")
    seed_everything(seed)
    logging.info("Global seed set to %d", seed)

    validate_design_assumption(Path(args.survey_design))

    requested = args.hypotheses
    unknown = [hyp for hyp in requested if hyp not in HYPOTHESES]
    if unknown:
        raise KeyError(f"Hypotheses not registered in confirmatory registry: {unknown}")

    specs = [HYPOTHESES[hyp] for hyp in requested]
    required_columns = sorted({col for spec in specs for col in spec.required_columns()})
    df = load_dataset(Path(args.dataset), required_columns)

    results: List[Dict[str, object]] = []
    for spec in specs:
        row = run_model_for_spec(df, spec)
        results.append(row)

    update_results_csv(Path(args.results_csv), results, seed=seed, overwrite=args.overwrite)


if __name__ == "__main__":
    main()
