#!/usr/bin/env python3
"""Compute disclosure-control diagnostics for tables and figures.

The script scans CSV tables for minimum numeric counts and lists figure
artifacts so every public release documents the n >= threshold rule.
"""

from __future__ import annotations

import argparse
import datetime as dt
import shlex
from pathlib import Path
from typing import List, Optional, Tuple

import pandas as pd


def list_csv_files(directory: Path) -> List[Path]:
    if not directory.exists():
        return []
    return sorted(p for p in directory.iterdir() if p.suffix.lower() == ".csv")


def list_figure_files(directory: Path) -> List[Path]:
    if not directory.exists():
        return []
    figure_exts = {".png", ".svg", ".jpg", ".jpeg", ".pdf"}
    return sorted(p for p in directory.iterdir() if p.suffix.lower() in figure_exts)


def min_numeric_cell(path: Path) -> Optional[float]:
    df = pd.read_csv(path)
    numeric = df.select_dtypes(include=["number"])
    if numeric.empty:
        return None
    return float(numeric.min().min())


def format_command(args: argparse.Namespace) -> str:
    quoted = " ".join(shlex.quote(str(a)) for a in [__file__] + args.original_args)
    return f"python {quoted}"


def build_table_rows(args: argparse.Namespace) -> Tuple[List[str], int]:
    rows: List[str] = []
    violations = 0

    for csv_path in list_csv_files(args.tables_dir):
        min_cell = min_numeric_cell(csv_path)
        if min_cell is None:
            action = "n/a"
            note = "No numeric columns detected"
            min_display = "n/a"
        else:
            min_display = f"{min_cell:.0f}" if min_cell.is_integer() else f"{min_cell:.2f}"
            if min_cell < args.min_n:
                action = "suppress/bin"
                violations += 1
            else:
                action = "ok"
            note = "auto scan of numeric columns"
        rows.append(
            f"| {csv_path} | table | {min_display} | {args.min_n} | {action} | {note} |"
        )

    for fig_path in list_figure_files(args.figures_dir):
        rows.append(
            f"| {fig_path} | figure | n/a | {args.min_n} | n/a | Structural figure (no cells) |"
        )

    if not rows:
        rows.append("| _None_ | PAP drafting only | n/a | {args.min_n} | n/a | No tables/figures detected |")

    return rows, violations


def write_report(args: argparse.Namespace) -> None:
    rows, violations = build_table_rows(args)
    args.output_md.parent.mkdir(parents=True, exist_ok=True)
    now = dt.datetime.utcnow().isoformat(timespec="seconds") + "Z"
    command = format_command(args)
    header = (
        f"# Disclosure Control Check\n"
        f"Date: {now}\n\n"
        f"Seed: {args.seed}\n\n"
        f"Threshold: n \u2265 {args.min_n}\n\n"
        "Command to reproduce:\n"
        "```bash\n"
        f"{command}\n"
        "```\n\n"
    )
    table_header = "| artifact | description | min_cell_n | threshold | suppression_action | notes |\n| --- | --- | --- | --- | --- | --- |\n"
    content = header + table_header + "\n".join(rows) + f"\n\nviolations: {violations}\n"
    args.output_md.write_text(content)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Disclosure checklist generator")
    parser.add_argument("--tables-dir", type=Path, default=Path("tables"))
    parser.add_argument("--figures-dir", type=Path, default=Path("figures"))
    parser.add_argument("--min-n", type=int, default=10)
    parser.add_argument("--output-md", type=Path, required=True)
    parser.add_argument("--seed", type=int, default=20251016)
    args = parser.parse_args()
    # Preserve argv for reporting (skip interpreter + script)
    setattr(args, "original_args", [])
    return args


def main() -> None:
    args = parse_args()
    args.original_args = []
    import sys

    args.original_args = sys.argv[1:]
    write_report(args)


if __name__ == "__main__":
    main()
