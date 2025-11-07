#!/usr/bin/env python3
"""
Generate the CSA–anxiety measurement diagnostic plan as a Markdown artifact.

Regeneration example:
python analysis/code/create_csa_anxiety_measurement_plan.py \
    --config config/agent_config.yaml \
    --out-md qc/csa_anxiety_measurement_plan.md \
    --generated-at 2025-11-04T13:15:00Z
"""

from __future__ import annotations

import argparse
import random
from pathlib import Path

import numpy as np
import yaml


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Render the CSA–anxiety measurement diagnostic plan."
    )
    parser.add_argument(
        "--config",
        required=True,
        help="Path to YAML config with seed and thresholds.",
    )
    parser.add_argument(
        "--out-md",
        required=True,
        help="Destination Markdown file for the diagnostic plan.",
    )
    parser.add_argument(
        "--generated-at",
        default="2025-11-04T13:15:00Z",
        help="ISO8601 timestamp recorded in the plan header (use UTC).",
    )
    return parser.parse_args()


def load_config(path: Path) -> dict:
    config = yaml.safe_load(path.read_text())
    if not isinstance(config, dict):
        raise ValueError("Configuration file must parse to a dictionary.")
    return config


def main() -> None:
    args = parse_args()
    config_path = Path(args.config)
    out_md_path = Path(args.out_md)

    config = load_config(config_path)
    seed = int(config.get("seed", 0))
    small_cell_threshold = int(config.get("small_cell_threshold", 10))
    dataset_path = config.get(
        "clean_dataset", "data/clean/childhoodbalancedpublic_with_csa_indicator.csv"
    )

    random.seed(seed)
    np.random.seed(seed)

    out_md_path.parent.mkdir(parents=True, exist_ok=True)

    lines = [
        "# CSA–Anxiety Measurement Diagnostic Plan",
        f"Generated: {args.generated_at} | Seed: {seed}",
        "",
        "## Context",
        "- Confirmatory results (HYP-003) show a −0.49 point association between CSA exposure "
        "and self-reported anxiety agreement on the −3 to +3 scale.",
        "- Directional diagnostics (`qc/csa_anxiety_direction.md`) confirm CSA-exposed respondents "
        "report lower anxiety agreement. Cell counts exceed the suppression threshold "
        f"({small_cell_threshold}).",
        "- Item routing review (`qc/anxiety_item_routing.md`) indicates the anxiety prompt is "
        "single-item, negatively coded, and situated alongside other affect measures; no reverse "
        "phrasing flag appears in instrument metadata.",
        "",
        "## Diagnostic Objectives",
        "1. Evaluate whether the anxiety response scale behaves equivalently across CSA exposure "
        "and key demographic subgroups (gender, age cohort).",
        "2. Assess convergent validity of the anxiety item with companion affect indicators "
        "(e.g., depression, stress, self-love).",
        "3. Examine whether distributional, routing, or missingness patterns indicate "
        "measurement artifacts or differential reporting.",
        "4. Document implications for interpretation and reporting in the main manuscript.",
        "",
        "## Diagnostic Modules",
        "| Module | Purpose | Primary Command(s) | Planned Outputs | Notes |",
        "|---|---|---|---|---|",
        "| M1: Polarity Verification | Re-run CSA vs anxiety mean comparison to "
        "confirm sign and magnitude, inspect category frequencies | "
        "`python analysis/code/diagnose_csa_anxiety_direction.py --dataset "
        f"{dataset_path} --config config/agent_config.yaml --outcome \"I tend to suffer from anxiety (npvfh98)-neg\" "
        "--indicator CSA_score_indicator --out-table tables/diagnostics/csa_anxiety_direction.csv "
        "--out-md qc/csa_anxiety_direction.md` | "
        "`tables/diagnostics/csa_anxiety_direction.csv`, `qc/csa_anxiety_direction.md` | "
        "Already executed; rerun only if upstream data change. |",
        "| M2: Response Category Audit | Summarise anxiety item distribution overall and "
        "by CSA exposure; verify no sparse categories (n < "
        f"{small_cell_threshold}) | "
        "`python analysis/code/diagnose_csa_anxiety_direction.py --dataset "
        f"{dataset_path} --config config/agent_config.yaml --outcome \"I tend to suffer from anxiety (npvfh98)-neg\" "
        "--indicator CSA_score_indicator --out-table tables/diagnostics/csa_anxiety_direction.csv "
        "--out-md qc/csa_anxiety_direction.md --include-category-counts` | "
        "`tables/diagnostics/csa_anxiety_direction_counts.csv`, "
        "`qc/csa_anxiety_direction.md` (appendix) | "
        "Extend script to emit category-level counts; ensure suppression rules. |",
        "| M3: Convergent Validity | Correlate anxiety item with depression and self-love; "
        "estimate reliability via polychoric correlations | "
        "`python analysis/code/evaluate_anxiety_convergence.py --dataset "
        f"{dataset_path} --config config/agent_config.yaml "
        "--out-table tables/diagnostics/anxiety_convergence.csv "
        "--out-md qc/anxiety_convergence.md` | "
        "`tables/diagnostics/anxiety_convergence.csv`, `qc/anxiety_convergence.md` | "
        "New script required; apply Benjamini–Hochberg within correlation family. |",
        "| M4: DIF / Subgroup Checks | Fit nested ordinal logistic models for anxiety item "
        "with CSA, gender, their interaction; conduct Wald test for DIF | "
        "`python analysis/code/test_anxiety_dif.py --dataset "
        f"{dataset_path} --config config/agent_config.yaml "
        "--groups CSA_score_indicator gender --out-md qc/anxiety_dif.md "
        "--out-table tables/diagnostics/anxiety_dif.csv` | "
        "`tables/diagnostics/anxiety_dif.csv`, `qc/anxiety_dif.md` | "
        "Pre-specify strata; ensure cell counts ≥ "
        f"{small_cell_threshold}. |",
        "| M5: Sensitivity Recode | Recode anxiety item to 0–6 scale and binary high-anxiety "
        "indicator; re-run confirmatory model as robustness | "
        "`python analysis/code/run_robustness_checks.py --dataset "
        f"{dataset_path} --config config/agent_config.yaml --hypotheses HYP-003 "
        "--robustness-set anxiety_scale_recodes` | "
        "`tables/robustness/hyp-003_anxiety_recodes.csv`, "
        "`qc/hyp-003_anxiety_recodes.md` | "
        "Extend robustness script to include recode routine. |",
        "",
        "## Task Breakdown",
        "| Task ID | Priority | Description | Status | Linked Module(s) |",
        "|---|---|---|---|---|",
        "| T-019 | 2 | Draft measurement diagnostic plan for CSA–anxiety anomaly | Completed | All |",
        "| T-020 | 3 | Identify subgroup heterogeneity tests for anxiety outcome | Pending | M4 |",
        "| T-021 | 1 | Implement ordinal DIF analysis for anxiety item (CSA × gender) | Pending | M4 |",
        "| T-022 | 2 | Assess convergent validity across anxiety, depression, self-love | Pending | M3 |",
        "",
        "## Reporting Commitments",
        "- Document all outputs in `qc/` and `tables/diagnostics/` with generation commands in "
        "`papers/main/MANIFEST.md`.",
        "- Update `reports/findings_v0.3.md` and `papers/main/manuscript.tex` once convergence and "
        "DIF diagnostics are executed; include limitations if anomalies persist.",
        "- Append decision log entries for each module executed, tagging the corresponding task IDs.",
        "",
        "## Privacy & Suppression",
        "- Maintain the small-cell threshold of "
        f"{small_cell_threshold} for all subgroup summaries; collapse categories when necessary.",
        "- Mask or omit DIF results for strata with post-weighted counts below threshold.",
        "",
        "## Next Steps",
        "1. Prioritise Module M4 (Task T-021) to test for differential reporting patterns.",
        "2. Execute Module M3 (Task T-022) to contextualise the anxiety item within the affect battery.",
        "3. Revisit robustness scripting to incorporate the sensitivity recodes outlined in Module M5.",
    ]

    out_md_path.write_text("\n".join(lines))


if __name__ == "__main__":
    main()
