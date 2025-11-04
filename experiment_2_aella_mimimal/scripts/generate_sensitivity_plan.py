#!/usr/bin/env python3
"""
Generate a deterministic Markdown plan documenting sensitivity strategies for
missing survey weights and replicate designs.

The script reads the survey design YAML and the global agent configuration to
ensure the plan stays synchronized with repository metadata. Timestamp output
can be fixed with --timestamp to support exact regeneration.
"""

import argparse
import pathlib
import sys
from datetime import UTC, datetime
from typing import Dict, List, Optional

import yaml


def load_yaml(path: pathlib.Path) -> Dict:
    if not path.exists():
        raise FileNotFoundError(f"Missing required YAML file: {path}")
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def determine_timestamp(ts_arg: Optional[str]) -> str:
    if ts_arg:
        return ts_arg
    return datetime.now(UTC).replace(microsecond=0).isoformat()


def missing_design_elements(design_meta: Dict) -> List[str]:
    checks = [
        ("weight_variable", "Calibrated weight column"),
        ("strata_variable", "Stratum identifier"),
        ("cluster_variable", "Primary sampling unit identifier"),
    ]
    gaps: List[str] = []
    for key, label in checks:
        if not design_meta.get(key):
            gaps.append(f"{label}: missing")
        else:
            gaps.append(f"{label}: present (`{design_meta[key]}`)")

    replicate_weights = design_meta.get("replicate_weights", [])
    if replicate_weights:
        joined = ", ".join(str(item) for item in replicate_weights)
        gaps.append(f"Replicate weights: present ({joined})")
    else:
        gaps.append("Replicate weights: missing")

    fpc = design_meta.get("finite_population_correction")
    if fpc:
        gaps.append(f"Finite population correction: present ({fpc})")
    else:
        gaps.append("Finite population correction: missing")
    return gaps


def build_markdown(config: Dict,
                   design_meta: Dict,
                   dataset: str,
                   generated_ts: str,
                   out_path: pathlib.Path) -> str:
    seed = config.get("seed", "N/A")
    privacy = config.get("privacy", {})
    min_cell = privacy.get("min_cell_size", "N/A")

    design_assumption = design_meta.get(
        "design_assumption",
        "Treat as simple random sample until sponsor provides design metadata."
    )
    design_notes = design_meta.get("notes", [])
    notes_joined = "; ".join(note.strip() for note in design_notes) if design_notes else "None recorded."

    gaps = missing_design_elements(design_meta)

    regen_cmd = (
        "python scripts/generate_sensitivity_plan.py "
        f"--config config/agent_config.yaml "
        f"--design docs/survey_design.yaml "
        f"--dataset {dataset} "
        f"--out {out_path.as_posix()} "
        f"--timestamp {generated_ts}"
    )

    lines: List[str] = [
        "# Sensitivity Strategy: Missing Survey Weights and Replicate Designs",
        "",
        f"- Generated: {generated_ts}",
        f"- Seed: {seed} (from `config/agent_config.yaml`)",
        f"- Dataset: `{dataset}`",
        "",
        "## Reproducibility",
        "Regenerate this plan with:",
        "```bash",
        regen_cmd,
        "```",
        "The script is deterministic aside from the timestamp, which is fixed via `--timestamp`.",
        "",
        "## Purpose and Scope",
        "Document how ongoing analyses will quantify uncertainty introduced by missing survey weights, strata, PSUs, and replicate designs. "
        "All follow-up steps must retain deterministic execution under the shared seed and respect the privacy guardrail "
        f"(suppress estimates where contributing cell counts fall below {min_cell}).",
        "",
        "## Current Design Constraints",
        f"- Assumption: {design_assumption}",
        f"- Notes: {notes_joined}",
        "- Metadata status:",
        *[f"  - {item}" for item in gaps],
        "",
        "## Proposed Sensitivity Scenarios",
        "### Scenario 0: Baseline SRS Benchmark",
        "- Maintain current simple random sampling assumption as the comparison anchor.",
        "- Archive existing H1/H2 outputs and manifests to support contrasts once weights arrive.",
        "- Deliverable: updated manifest documenting baseline metrics (already complete via prior loops).",
        "",
        "### Scenario 1: Proxy Weight Calibration",
        "- Construct pseudo-weights by calibrating to external population margins (age x sex, region) derived from public sources.",
        "- Implementation outline:",
        "  1. Assemble candidate calibration targets (e.g., Census CPS) and document provenance.",
        "  2. Fit raking or generalized regression weighting using deterministic solvers seeded with 20251016.",
        "  3. Re-compute key estimands (H1, H2, forthcoming hypotheses) under pseudo-weights and compare to Scenario 0.",
        "- Privacy: ensure each calibration cell retains at least 10 respondents; otherwise merge categories deterministically.",
        "- Anticipated artifact: `tables/sensitivity_proxy_weights_{hypothesis}.csv` with manifests noting calibration inputs.",
        "",
        "### Scenario 2: Variance Inflation via Design Effect Grid",
        "- Emulate plausible design effects by inflating standard errors using fixed multipliers (e.g., 1.2, 1.5, 2.0).",
        "- Implementation outline:",
        "  1. Define a deterministic grid of design effect multipliers informed by literature and sponsor guidance.",
        "  2. Apply multipliers to Scenario 0 standard errors and adjust confidence intervals accordingly.",
        "  3. Record thresholds where inference (e.g., significance at alpha=0.05) changes.",
        "- Anticipated artifact: `tables/sensitivity_design_effect_grid.csv` with multiplier annotations.",
        "",
        "### Scenario 3: Replicate Design Imputation",
        "- Approximate replicate variance by generating synthetic strata/PSU structures using stable clustering rules.",
        "- Implementation outline:",
        "  1. Deterministically cluster respondents on geography and demographics to form pseudo-PSUs.",
        "  2. Assign equal-within-cluster weights (or use Scenario 1 weights if available) and build BRR/JK replicates.",
        "  3. Re-estimate focal statistics using survey packages that accept replicate weight matrices.",
        "- Deliverable: manifest recording clustering rules, seed, and replicate counts.",
        "",
        "## Implementation Roadmap",
        "- T-013 (new): Curate external margin targets and develop deterministic raking script.",
        "- T-014 (new): Generate design-effect multiplier grid and reporting template.",
        "- T-015 (new): Prototype pseudo-PSU clustering and replicate weight generation.",
        "- Dependencies: completion of Scenario 1 informs Scenario 3 weighting; Scenario 2 can proceed in parallel.",
        "",
        "## Quality Assurance and Logging",
        "- Log all commands and seeds in `analysis/decision_log.csv` and relevant manifests.",
        "- Update `artifacts/state.json` with new artifacts and regeneration commands after each scenario.",
        "- Store intermediate calibration inputs under `artifacts/` with deterministic filenames.",
        "",
        "## External Coordination",
        "- Continue sponsor outreach for official design files; once provided, rerun baseline scripts with authentic weights and retire proxy scenarios.",
        "- Maintain `reports/design_metadata_brief.md` and `reports/sponsor_follow_up.md` to reflect status changes.",
    ]
    return "\n".join(lines)


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        description="Generate sensitivity planning document for missing survey weights."
    )
    parser.add_argument(
        "--config", default="config/agent_config.yaml",
        help="Path to global agent configuration."
    )
    parser.add_argument(
        "--design", default="docs/survey_design.yaml",
        help="Path to survey design metadata YAML."
    )
    parser.add_argument(
        "--dataset", default="childhoodbalancedpublic_original.csv",
        help="Name of the primary survey dataset."
    )
    parser.add_argument(
        "--out", default="analysis/sensitivity_plan.md",
        help="Output Markdown path for the sensitivity plan."
    )
    parser.add_argument(
        "--timestamp",
        help="ISO-8601 timestamp to stamp in the plan for reproducibility."
    )

    args = parser.parse_args(argv)

    config_path = pathlib.Path(args.config)
    design_path = pathlib.Path(args.design)
    out_path = pathlib.Path(args.out)

    config = load_yaml(config_path)
    design_meta = load_yaml(design_path)
    generated_ts = determine_timestamp(args.timestamp)

    out_path.parent.mkdir(parents=True, exist_ok=True)

    markdown = build_markdown(
        config=config,
        design_meta=design_meta,
        dataset=args.dataset,
        generated_ts=generated_ts,
        out_path=out_path,
    )
    out_path.write_text(markdown, encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
