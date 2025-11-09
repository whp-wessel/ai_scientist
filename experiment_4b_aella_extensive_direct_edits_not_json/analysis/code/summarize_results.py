#!/usr/bin/env python3
"""Aggregate JSON summaries into the pre-BH results CSV."""

from __future__ import annotations

import argparse
import csv
import json
import math
from pathlib import Path
from typing import Any


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Summarize hypothesis results.")
    parser.add_argument(
        "--json-paths",
        nargs="+",
        required=True,
        help="Result JSON files exported by modeling scripts.",
    )
    parser.add_argument(
        "--output-csv",
        default="analysis/results_pre_bh.csv",
        help="Path for the pre-BH results table.",
    )
    return parser.parse_args()


def norm_cdf(x: float) -> float:
    return (1 + math.erf(x / math.sqrt(2))) / 2


def two_sided_pvalue(estimate: float, se: float) -> float:
    if se == 0 or math.isnan(estimate) or math.isnan(se):
        return float("nan")
    z = estimate / se
    return 2 * (1 - norm_cdf(abs(z)))


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


LIMITATIONS: dict[str, str] = {
    "H1": "Ordered logit under SRS; weights not yet available and unmeasured confounding remains possible.",
    "H2": "Same SRS assumption plus missing chronic illness indicator; prospective robustness checks planned.",
    "H3": "Linear model with HC1 SEs; abuse indicator may suffer recall bias.",
    "NC1": "Negative control, null association expected by design.",
}

CONFIDENCE: dict[str, str] = {
    "H1": "Medium",
    "H2": "Medium",
    "H3": "Medium",
    "NC1": "Low",
}


def build_row(data: dict[str, Any]) -> dict[str, Any]:
    hypothesis_id = data["hypothesis_id"]
    effect = data.get("effect", {})
    estimate = float(effect.get("estimate", math.nan))
    se = float(effect.get("se", math.nan))
    ci_low = float(effect.get("ci_lower", math.nan))
    ci_high = float(effect.get("ci_upper", math.nan))
    p_value = effect.get("p_value")
    if p_value is None:
        p_value = two_sided_pvalue(estimate, se)
    row = {
        "hypothesis_id": hypothesis_id,
        "family": data.get("family", ""),
        "targeted": data.get("targeted", "Y"),
        "bh_in_scope": "",
        "model": data.get("model", ""),
        "n_unweighted": int(data.get("n_analytic") or data.get("diagnostics", {}).get("nobs", 0)),
        "n_weighted": int(data.get("n_analytic") or data.get("diagnostics", {}).get("nobs", 0)),
        "estimate": estimate,
        "se": se,
        "ci_low": ci_low,
        "ci_high": ci_high,
        "p_value": p_value,
        "effect_size_metric": data.get("effect_metric", ""),
        "robustness_passed": data.get("robustness_passed", "N"),
        "limitations": LIMITATIONS.get(hypothesis_id, ""),
        "confidence_rating": CONFIDENCE.get(hypothesis_id, "Medium"),
        "notes": data.get("notes", ""),
        "command": data.get("command", ""),
    }
    return row


def main() -> None:
    args = parse_args()
    rows: list[dict[str, Any]] = []
    for json_path in args.json_paths:
        path = Path(json_path)
        if not path.exists():
            raise FileNotFoundError(f"Result JSON missing: {path}")
        data = load_json(path)
        rows.append(build_row(data))
    rows.sort(key=lambda r: r["hypothesis_id"])
    output_path = Path(args.output_csv)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "hypothesis_id",
        "family",
        "targeted",
        "bh_in_scope",
        "model",
        "n_unweighted",
        "n_weighted",
        "estimate",
        "se",
        "ci_low",
        "ci_high",
        "p_value",
        "effect_size_metric",
        "robustness_passed",
        "limitations",
        "confidence_rating",
        "notes",
        "command",
    ]
    with output_path.open("w", newline="") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)
    print(f"Wrote {len(rows)} rows to {output_path}")


if __name__ == "__main__":
    main()
