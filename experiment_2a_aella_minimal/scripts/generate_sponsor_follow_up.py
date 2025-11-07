#!/usr/bin/env python3
"""
Generate a sponsor follow-up note requesting outstanding survey design deliverables.

The content is derived from the latest design metadata brief so the request stays
aligned with previously logged gaps. The script is deterministic aside from the
timestamp, which is recorded for transparency. Seed is logged for reproducibility.
"""

import argparse
import pathlib
import re
import sys
from datetime import UTC, datetime
from typing import List, Optional

SEED = 20251016


def _read_text(path: pathlib.Path) -> str:
    if not path.exists():
        raise FileNotFoundError(f"Expected brief at {path}")
    return path.read_text(encoding="utf-8")


def _extract_dataset(markdown: str) -> Optional[str]:
    match = re.search(r"-\s*Dataset:\s*`([^`]+)`", markdown)
    return match.group(1) if match else None


def _extract_bullets(markdown: str, heading: str) -> List[str]:
    lines = markdown.splitlines()
    capture = False
    bullets: List[str] = []
    for line in lines:
        if line.startswith("## "):
            if capture and line.strip() != f"## {heading}":
                break
            capture = line.strip() == f"## {heading}"
            continue
        if capture and line.startswith("- "):
            bullets.append(line[2:].strip())
    return bullets


def build_follow_up(brief_markdown: str, brief_path: pathlib.Path) -> str:
    dataset = _extract_dataset(brief_markdown) or "the study dataset"
    requested = _extract_bullets(brief_markdown, "Requested Sponsor Deliverables")
    gaps = _extract_bullets(brief_markdown, "Metadata Gaps")

    generated_ts = datetime.now(UTC).replace(microsecond=0).isoformat()

    email_lines: List[str] = [
        "# Sponsor Follow-up: Survey Design Deliverables",
        "",
        f"- Generated: {generated_ts}",
        f"- Seed: {SEED}",
        f"- Source brief: {brief_path.as_posix()}",
        "",
        "## Email Draft",
        "Subject: Follow-up on Survey Design Deliverables for Childhood Balanced Study",
        "",
        "Hello [Sponsor Team],",
        "",
        "Thank you for your partnership on the Childhood Balanced Study. "
        "Following our earlier brief, we still need the survey design metadata "
        "below to finalize weighting and variance estimation protocols. "
        "Could you please share the outstanding items or an estimated delivery date?",
        "",
        "Outstanding deliverables:",
        *[f"- {item}" for item in requested],
        "",
        "Once we receive these files we can update the survey design metadata, rerun "
        "the validation scripts, and confirm that the weighting specifications align "
        "with your production workflow. Please let us know if any of the items have "
        "changed or if additional context is required.",
        "",
        "Best regards,",
        "",
        "[Research Automation Team]",
        "",
        "## Talking Points for Follow-up Call",
        *[f"- {gap}" for gap in gaps],
        "",
        "## Attachments/References",
        f"- Latest design brief: {brief_path.as_posix()}",
        "",
        "## Reproducibility",
        "To regenerate this note, run:",
        "```bash",
        "python scripts/generate_sponsor_follow_up.py "
        f"--brief {brief_path.as_posix()} --out reports/sponsor_follow_up.md",
        "```",
        "",
        "This script is deterministic aside from the timestamp and records the seed above.",
    ]
    return "\n".join(email_lines)


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        description="Generate sponsor follow-up communication referencing the design brief."
    )
    parser.add_argument(
        "--brief",
        default="reports/design_metadata_brief.md",
        help="Path to the design metadata brief markdown file."
    )
    parser.add_argument(
        "--out",
        default="reports/sponsor_follow_up.md",
        help="Output markdown path for the follow-up note."
    )
    args = parser.parse_args(argv)

    brief_path = pathlib.Path(args.brief)
    follow_up_path = pathlib.Path(args.out)
    follow_up_path.parent.mkdir(parents=True, exist_ok=True)

    brief_markdown = _read_text(brief_path)
    follow_up_content = build_follow_up(brief_markdown, brief_path=brief_path)
    follow_up_path.write_text(follow_up_content, encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
