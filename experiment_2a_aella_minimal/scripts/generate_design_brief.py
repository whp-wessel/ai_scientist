#!/usr/bin/env python3
"""
Generate a sponsor-facing brief summarizing survey design metadata gaps.

The output is deterministic and driven by repository metadata files so that the
brief can be regenerated exactly. Seed is recorded for audit compliance.
"""

import argparse
import pathlib
import re
import sys
from datetime import UTC, datetime
from typing import List, Optional

import yaml

SEED = 20251016


def _read_text(path: pathlib.Path) -> str:
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8")


def _parse_audit_date(markdown: str) -> Optional[str]:
    """
    Extract the ISO-formatted date from lines like '- **Date:** 2025-11-03'.
    """
    match = re.search(r"- \*\*Date:\*\*\s*(\d{4}-\d{2}-\d{2})", markdown)
    return match.group(1) if match else None


def _format_gap_summary(design_meta: dict) -> List[str]:
    required_items = [
        ("weight_variable", "Calibrated base weight column"),
        ("strata_variable", "Stratum identifier"),
        ("cluster_variable", "Primary sampling unit identifier"),
    ]
    gaps: List[str] = []
    for key, label in required_items:
        value = design_meta.get(key)
        if value in (None, "", []):
            gaps.append(f"{label}: missing")
        else:
            gaps.append(f"{label}: present (`{value}`)")

    replicate_weights = design_meta.get("replicate_weights", [])
    if not replicate_weights:
        gaps.append("Replicate weights: missing")
    else:
        joined = ", ".join(str(item) for item in replicate_weights)
        gaps.append(f"Replicate weights: present ({joined})")

    fpc = design_meta.get("finite_population_correction")
    gaps.append(
        "Finite population correction: missing"
        if fpc in (None, "", [])
        else f"Finite population correction: present ({fpc})"
    )
    return gaps


def build_brief(design_path: pathlib.Path,
                validation_note: pathlib.Path,
                monitor_note: pathlib.Path) -> str:
    design_meta = yaml.safe_load(design_path.read_text(encoding="utf-8"))

    dataset = design_meta.get("dataset", "N/A")
    assumption = design_meta.get(
        "design_assumption",
        "Simple random sampling until sponsor metadata arrives."
    )
    notes = design_meta.get("notes", [])

    validation_md = _read_text(validation_note)
    monitor_md = _read_text(monitor_note)

    validation_date = _parse_audit_date(validation_md)
    monitor_date = _parse_audit_date(monitor_md)

    audit_lines: List[str] = []
    if validation_date:
        audit_lines.append(f"Initial validation: {validation_date}")
    if monitor_date and monitor_date != validation_date:
        audit_lines.append(f"Latest monitoring pass: {monitor_date}")
    if not audit_lines:
        audit_lines.append("No dated audits recorded.")

    gaps = _format_gap_summary(design_meta)

    requested_files = [
        "Calibrated individual weight file or integrated weight column metadata.",
        "Stratum definitions and primary sampling unit (PSU) identifiers.",
        "Replicate weight specification (e.g., BRR, JK1/JK2) with scaling factors.",
        "Weighting and variance estimation methodology documentation.",
        "Any finite population correction values or universe totals used in calibration.",
    ]

    now_iso = datetime.now(UTC).replace(microsecond=0).isoformat()

    lines: List[str] = [
        "# Sponsor Brief: Survey Design Metadata",
        "",
        f"- Generated: {now_iso}",
        f"- Seed: {SEED}",
        f"- Dataset: `{dataset}`",
        "",
        "## Current Assumptions",
        assumptions_text(assumption, notes),
        "",
        "## Metadata Gaps",
        *[f"- {gap}" for gap in gaps],
        "",
        "## Requested Sponsor Deliverables",
        *[f"- {item}" for item in requested_files],
        "",
        "## Audit Trail",
        *[f"- {line}" for line in audit_lines],
        "",
        "## Reproducibility",
        "To regenerate this brief, run:",
        "```bash",
        "python scripts/generate_design_brief.py --out reports/design_metadata_brief.md",
        "```",
        "",
        "This script is deterministic and relies on the metadata files referenced above.",
    ]
    return "\n".join(lines)


def assumptions_text(assumption: str, notes: List[str]) -> str:
    parts: List[str] = [assumption]
    if notes:
        formatted = "; ".join(note.strip() for note in notes)
        parts.append(f"Notes: {formatted}")
    return " ".join(parts)


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        description="Generate sponsor brief summarizing survey design metadata gaps."
    )
    parser.add_argument(
        "--design", default="docs/survey_design.yaml",
        help="Path to survey design YAML metadata."
    )
    parser.add_argument(
        "--validation-note", default="qc/design_validation.md",
        help="Path to the initial design validation markdown notes."
    )
    parser.add_argument(
        "--monitor-note", default="qc/design_metadata_monitor.md",
        help="Path to the latest monitoring note."
    )
    parser.add_argument(
        "--out", default="reports/design_metadata_brief.md",
        help="Output markdown path for the sponsor brief."
    )

    args = parser.parse_args(argv)

    design_path = pathlib.Path(args.design)
    if not design_path.exists():
        raise FileNotFoundError(f"Missing design metadata: {design_path}")

    output_path = pathlib.Path(args.out)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    brief = build_brief(
        design_path=design_path,
        validation_note=pathlib.Path(args.validation_note),
        monitor_note=pathlib.Path(args.monitor_note),
    )
    output_path.write_text(brief, encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
