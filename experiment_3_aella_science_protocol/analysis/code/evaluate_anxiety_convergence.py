#!/usr/bin/env python3
"""
Evaluate convergent validity for the CSA anxiety outcome using companion affect items.

Regeneration example:
python analysis/code/evaluate_anxiety_convergence.py \
    --dataset data/clean/childhoodbalancedpublic_with_csa_indicator.csv \
    --config config/agent_config.yaml \
    --out-table tables/diagnostics/anxiety_convergence.csv \
    --out-md qc/anxiety_convergence.md \
    --seed 20251016
"""

from __future__ import annotations

import argparse
import math
import random
import warnings
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable, List, Sequence, Tuple

import numpy as np
import pandas as pd
import yaml
from scipy.optimize import minimize_scalar
from scipy.stats import norm, pearsonr, spearmanr, multivariate_normal
from statsmodels.stats.multitest import fdrcorrection


DEFAULT_OUTCOME = "I tend to suffer from anxiety (npvfh98)-neg"
DEFAULT_COMPARATORS: tuple[str, ...] = (
    "I tend to suffer from depression (wz901dj)",
    "I'm quite sensitive to stress (qhyti2r)-neg",
    "I love myself (2l8994l)",
    "I tend to be calm/peaceful (6e6zhy3)",
)

# Expected association directions for interpretability checks.
EXPECTED_DIRECTIONS = {
    "I tend to suffer from depression (wz901dj)": "positive",
    "I'm quite sensitive to stress (qhyti2r)-neg": "positive",
    "I love myself (2l8994l)": "negative",
    "I tend to be calm/peaceful (6e6zhy3)": "negative",
}


@dataclass(frozen=True)
class ReliabilitySet:
    name: str
    items: Sequence[Tuple[str, int]]


RELIABILITY_SETS: tuple[ReliabilitySet, ...] = (
    ReliabilitySet(
        name="Negative affect triad (anxiety, depression, stress)",
        items=(
            (DEFAULT_OUTCOME, 1),
            ("I tend to suffer from depression (wz901dj)", 1),
            ("I'm quite sensitive to stress (qhyti2r)-neg", 1),
        ),
    ),
    ReliabilitySet(
        name="Self-regulation composite (anxiety vs. reversed calm/self-love)",
        items=(
            (DEFAULT_OUTCOME, 1),
            ("I love myself (2l8994l)", -1),
            ("I tend to be calm/peaceful (6e6zhy3)", -1),
        ),
    ),
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Compute convergent validity diagnostics for the anxiety outcome."
    )
    parser.add_argument("--dataset", required=True, help="Input CSV dataset path.")
    parser.add_argument(
        "--config", required=True, help="Path to config YAML with seed and thresholds."
    )
    parser.add_argument(
        "--out-table",
        required=True,
        help="Destination CSV capturing correlation diagnostics.",
    )
    parser.add_argument(
        "--out-md",
        required=True,
        help="Destination Markdown file summarising findings.",
    )
    parser.add_argument(
        "--out-json",
        default=None,
        help="Optional JSON dump of intermediate statistics.",
    )
    parser.add_argument(
        "--outcome",
        default=DEFAULT_OUTCOME,
        help="Outcome column capturing anxiety tendency (neg-coded).",
    )
    parser.add_argument(
        "--comparators",
        nargs="+",
        default=list(DEFAULT_COMPARATORS),
        help="Comparator columns to test for convergent validity.",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=None,
        help="Optional override for random seed (otherwise taken from config).",
    )
    return parser.parse_args()


def load_config(path: Path) -> dict:
    config = yaml.safe_load(path.read_text())
    if not isinstance(config, dict):
        raise ValueError("Configuration file must parse to a dictionary.")
    return config


def fisher_ci(r: float, n: int, alpha: float = 0.05) -> Tuple[float, float]:
    if n <= 3 or abs(r) >= 1:
        return float("nan"), float("nan")
    z = 0.5 * math.log((1 + r) / (1 - r))
    se = 1 / math.sqrt(n - 3)
    z_crit = norm.ppf(1 - alpha / 2)
    lower = z - z_crit * se
    upper = z + z_crit * se
    return math.tanh(lower), math.tanh(upper)


def safe_series(df: pd.DataFrame, cols: Iterable[str]) -> pd.DataFrame:
    missing = [col for col in cols if col not in df.columns]
    if missing:
        joined = ", ".join(missing)
        raise ValueError(f"Dataset missing expected columns: {joined}")
    return df[list(cols)]


def _category_thresholds(counts: np.ndarray) -> np.ndarray:
    proportions = counts / counts.sum()
    cumulative = np.cumsum(proportions)[:-1]
    # Guard against 0 or 1 probabilities pushing thresholds to infinities.
    eps = 1e-6
    cumulative = np.clip(cumulative, eps, 1 - eps)
    return norm.ppf(cumulative)


def _bvn_cdf(x: float, y: float, rho: float) -> float:
    if math.isinf(x) and x < 0:
        return 0.0
    if math.isinf(y) and y < 0:
        return 0.0
    if math.isinf(x) and x > 0 and math.isinf(y) and y > 0:
        return 1.0

    cov = np.array([[1.0, rho], [rho, 1.0]], dtype=float)
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", category=RuntimeWarning)
        value = multivariate_normal.cdf(
            [x if not math.isinf(x) else np.sign(x) * 8.0,
             y if not math.isinf(y) else np.sign(y) * 8.0],
            mean=[0.0, 0.0],
            cov=cov,
        )
    return float(value)


def _cell_probability(
    lower: float, upper: float, lower_y: float, upper_y: float, rho: float
) -> float:
    a = _bvn_cdf(upper, upper_y, rho)
    b = _bvn_cdf(lower, upper_y, rho)
    c = _bvn_cdf(upper, lower_y, rho)
    d = _bvn_cdf(lower, lower_y, rho)
    prob = max(a - b - c + d, 0.0)
    return prob


def estimate_polychoric(x: np.ndarray, y: np.ndarray) -> Tuple[float, str]:
    """Estimate the polychoric correlation between two ordinal variables."""
    data = pd.DataFrame({"x": x, "y": y}).dropna()
    if data.empty:
        raise ValueError("No complete cases available for polychoric estimation.")

    freq = (
        pd.crosstab(data["x"], data["y"])
        .sort_index(axis=0)
        .sort_index(axis=1)
        .astype(float)
    )
    row_counts = freq.sum(axis=1).values
    col_counts = freq.sum(axis=0).values

    x_thresholds = _category_thresholds(row_counts)
    y_thresholds = _category_thresholds(col_counts)

    # Append boundary infinities for interval calculations.
    x_bounds = np.concatenate(([-np.inf], x_thresholds, [np.inf]))
    y_bounds = np.concatenate(([-np.inf], y_thresholds, [np.inf]))
    freq_values = freq.values

    def neg_log_likelihood(rho: float) -> float:
        if not (-0.999 < rho < 0.999):
            return np.inf

        log_likelihood = 0.0
        for i in range(freq_values.shape[0]):
            for j in range(freq_values.shape[1]):
                lower_x = x_bounds[i]
                upper_x = x_bounds[i + 1]
                lower_y = y_bounds[j]
                upper_y = y_bounds[j + 1]
                prob = _cell_probability(lower_x, upper_x, lower_y, upper_y, rho)
                prob = max(prob, 1e-12)
                log_likelihood += freq_values[i, j] * math.log(prob)
        return -log_likelihood

    result = minimize_scalar(
        neg_log_likelihood, bounds=(-0.995, 0.995), method="bounded"
    )

    if not result.success:
        return float("nan"), f"optimisation_failed:{result.status}"

    rho_hat = float(result.x)
    return rho_hat, "ok"


def cronbach_alpha(matrix: pd.DataFrame) -> float:
    if matrix.empty:
        return float("nan")
    values = matrix.to_numpy(dtype=float)
    k = values.shape[1]
    if k < 2:
        return float("nan")
    item_variances = values.var(axis=0, ddof=1)
    total_variance = values.sum(axis=1).var(ddof=1)
    if total_variance <= 0:
        return float("nan")
    return (k / (k - 1)) * (1 - item_variances.sum() / total_variance)


def format_float(value: float, digits: int = 3) -> str:
    if isinstance(value, str):
        return value
    if value is None or (isinstance(value, float) and math.isnan(value)):
        return "NA"
    return f"{value:.{digits}f}"


def build_markdown(
    table: pd.DataFrame,
    reliability_notes: List[str],
    direction_notes: List[str],
    seed: int,
    outcome: str,
    dataset: Path,
    config: Path,
) -> str:
    timestamp = datetime.now(timezone.utc).isoformat()
    lines = [
        "# Anxiety Convergent Validity Diagnostics",
        f"Generated: {timestamp} | Seed: {seed}",
        "",
        f"- Outcome: `{outcome}`",
        f"- Dataset: `{dataset}`",
        f"- Config: `{config}`",
        "",
        "## Correlation Summary",
        "| Comparator | Expected Direction | Direction OK | n | Pearson r | 95% CI | Spearman ρ | Polychoric r | q (BH, Pearson) | Notes |",
        "|---|---|---|---|---|---|---|---|---|---|",
    ]

    for _, row in table.iterrows():
        ci = f"[{format_float(row['pearson_ci_low'])}, {format_float(row['pearson_ci_high'])}]"
        lines.append(
            f"| `{row['comparator']}` | {row['direction_expected']} | "
            f"{row['direction_consistent']} | {int(row['n_complete'])} | "
            f"{format_float(row['pearson_r'])} | {ci} | {format_float(row['spearman_rho'])} | "
            f"{format_float(row['polychoric_r'])} | {format_float(row['pearson_q_value'])} | {row['notes']} |"
        )

    lines.extend(
        [
            "",
            "## Reliability Benchmarks",
        ]
    )

    if reliability_notes:
        lines.extend(f"- {note}" for note in reliability_notes)
    else:
        lines.append("- No reliability sets evaluated (insufficient data).")

    lines.extend(["", "## Interpretation"])

    if direction_notes:
        lines.extend(f"- {note}" for note in direction_notes)
    else:
        lines.append(
            "- All comparator directions align with theoretical expectations for convergent validity."
        )

    lines.append(
        "- q-values apply Benjamini–Hochberg (q=0.05) across Pearson correlations within this diagnostic family."
    )

    lines.extend(
        [
            "",
            "## Reproducibility",
            f"- Command: `python analysis/code/evaluate_anxiety_convergence.py --dataset {dataset} --config {config} "
            f"--out-table tables/diagnostics/anxiety_convergence.csv --out-md qc/anxiety_convergence.md --seed {seed}`",
        ]
    )

    return "\n".join(lines)


def main() -> None:
    args = parse_args()

    dataset_path = Path(args.dataset)
    config_path = Path(args.config)
    out_table_path = Path(args.out_table)
    out_md_path = Path(args.out_md)
    outcome = args.outcome
    comparators = list(dict.fromkeys(args.comparators))  # preserve order, remove dups

    config = load_config(config_path)
    seed = int(args.seed if args.seed is not None else config.get("seed", 0))
    q_alpha = float(config.get("fdr_q", 0.05))
    threshold = int(config.get("small_cell_threshold", 10))

    random.seed(seed)
    np.random.seed(seed)

    df = pd.read_csv(dataset_path, low_memory=False)
    data = safe_series(df, [outcome] + comparators)

    results = []
    pearson_pvalues = []

    for comparator in comparators:
        pair = data[[outcome, comparator]].dropna()
        n_complete = int(pair.shape[0])
        if n_complete < threshold:
            raise ValueError(
                f"Complete cases for {comparator} below suppression threshold ({n_complete} < {threshold})."
            )

        pearson_r, pearson_p = pearsonr(pair[outcome], pair[comparator])
        spearman_rho, spearman_p = spearmanr(pair[outcome], pair[comparator])
        ci_low, ci_high = fisher_ci(pearson_r, n_complete)

        polychoric_r, status = estimate_polychoric(
            pair[outcome].to_numpy(), pair[comparator].to_numpy()
        )

        expected_direction = EXPECTED_DIRECTIONS.get(comparator, "unspecified")
        direction_consistent = True
        if expected_direction == "positive":
            direction_consistent = pearson_r >= 0
        elif expected_direction == "negative":
            direction_consistent = pearson_r <= 0

        notes = "pairwise complete; polychoric OK"
        if status != "ok":
            notes = f"pairwise complete; polychoric status={status}"
        if (
            expected_direction in {"positive", "negative"}
            and not direction_consistent
        ):
            notes = (
                f"{notes}; pearson sign != expected {expected_direction}"
            )

        results.append(
            {
                "outcome": outcome,
                "comparator": comparator,
                "direction_expected": expected_direction,
                "direction_consistent": direction_consistent,
                "n_complete": n_complete,
                "pearson_r": pearson_r,
                "pearson_ci_low": ci_low,
                "pearson_ci_high": ci_high,
                "pearson_p_value": pearson_p,
                "spearman_rho": spearman_rho,
                "spearman_p_value": spearman_p,
                "polychoric_r": polychoric_r,
                "notes": notes,
            }
        )
        pearson_pvalues.append(pearson_p)

    # Apply Benjamini–Hochberg FDR correction across Pearson correlations.
    pearson_q_values = [float("nan")] * len(results)
    if any(not math.isnan(p) for p in pearson_pvalues):
        valid_indices = [i for i, p in enumerate(pearson_pvalues) if not math.isnan(p)]
        valid_ps = [pearson_pvalues[i] for i in valid_indices]
        _, q_vals = fdrcorrection(valid_ps, alpha=q_alpha)
        for idx, q_val in zip(valid_indices, q_vals):
            pearson_q_values[idx] = float(q_val)

    for result, q_val in zip(results, pearson_q_values):
        result["pearson_q_value"] = q_val

    table = pd.DataFrame(results)
    table = table[
        [
            "outcome",
            "comparator",
            "direction_expected",
            "direction_consistent",
            "n_complete",
            "pearson_r",
            "pearson_ci_low",
            "pearson_ci_high",
            "pearson_p_value",
            "pearson_q_value",
            "spearman_rho",
            "spearman_p_value",
            "polychoric_r",
            "notes",
        ]
    ]

    out_table_path.parent.mkdir(parents=True, exist_ok=True)
    table.to_csv(out_table_path, index=False)

    # Reliability calculations.
    reliability_notes: List[str] = []
    for rel_set in RELIABILITY_SETS:
        cols = [name for name, _ in rel_set.items]
        oriented = []
        missing_cols = [col for col in cols if col not in data.columns]
        if missing_cols:
            reliability_notes.append(
                f"{rel_set.name}: skipped (missing columns: {', '.join(missing_cols)})"
            )
            continue

        oriented_frames = []
        for col, direction in rel_set.items:
            oriented_frames.append(data[col] * direction)
        matrix = pd.concat(oriented_frames, axis=1, keys=[c for c, _ in rel_set.items])
        matrix = matrix.dropna()
        complete_n = int(matrix.shape[0])
        if complete_n < threshold:
            reliability_notes.append(
                f"{rel_set.name}: insufficient complete cases ({complete_n} < {threshold})."
            )
            continue
        alpha = cronbach_alpha(matrix)
        if math.isnan(alpha):
            reliability_notes.append(
                f"{rel_set.name}: Cronbach's α unavailable (zero variance)."
            )
            continue
        if alpha < 0:
            reliability_notes.append(
                f"{rel_set.name}: Cronbach's α = {format_float(alpha)} "
                f"(n={complete_n}; negative suggests opposing construct directions)."
            )
            continue
        reliability_notes.append(
            f"{rel_set.name}: Cronbach's α = {format_float(alpha)} (n={complete_n})."
        )

    direction_notes: List[str] = []
    directional_mask = table["direction_expected"].isin({"positive", "negative"})
    if directional_mask.any():
        mismatched = table[directional_mask & (~table["direction_consistent"])]
        if mismatched.empty:
            direction_notes.append(
                "Pearson correlations align with expected directions for all comparators."
            )
        else:
            for _, row in mismatched.iterrows():
                observed_sign = "positive" if row["pearson_r"] > 0 else "negative"
                direction_notes.append(
                    f"{row['comparator']} correlation is {format_float(row['pearson_r'])} "
                    f"(observed {observed_sign}, expected {row['direction_expected']})."
                )

    markdown = build_markdown(
        table=table,
        reliability_notes=reliability_notes,
        direction_notes=direction_notes,
        seed=seed,
        outcome=outcome,
        dataset=dataset_path,
        config=config_path,
    )
    out_md_path.parent.mkdir(parents=True, exist_ok=True)
    out_md_path.write_text(markdown)


if __name__ == "__main__":
    main()
