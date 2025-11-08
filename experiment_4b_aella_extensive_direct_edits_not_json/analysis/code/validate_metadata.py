#!/usr/bin/env python3
"""Validate codebook + survey design metadata against the dataset columns."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import pandas as pd
import yaml


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Metadata validation helper.")
    parser.add_argument("--dataset", required=True, help="Path to the CSV dataset.")
    parser.add_argument("--codebook", required=True, help="Path to the JSON codebook.")
    parser.add_argument("--survey-design", required=True, help="Path to the YAML survey design file.")
    parser.add_argument("--report-json", type=Path, required=True, help="JSON output path.")
    parser.add_argument("--report-md", type=Path, required=True, help="Markdown output path.")
    return parser.parse_args()


def load_columns(dataset_path: Path) -> list[str]:
    df = pd.read_csv(dataset_path, nrows=0)
    return df.columns.tolist()


def validate_codebook(columns: list[str], codebook_path: Path) -> dict[str, Any]:
    data = json.loads(codebook_path.read_text())
    documented_entries = []
    source_columns: list[str] = []
    for entry in data.get("variables", []):
        alias = entry.get("name")
        if not alias:
            continue
        source_column = entry.get("source_column") or alias
        exists = source_column in columns
        documented_entries.append(
            {
                "alias": alias,
                "source_column": source_column,
                "exists_in_data": exists,
            }
        )
        source_columns.append(source_column)

    missing_in_data = sorted(
        [entry["alias"] for entry in documented_entries if not entry["exists_in_data"]]
    )
    undocumented_columns = sorted([col for col in columns if col not in source_columns])

    return {
        "documented_variables": len(documented_entries),
        "missing_in_data": missing_in_data,
        "undocumented_columns_count": len(undocumented_columns),
        "documented_entries": documented_entries,
        "codebook_path": str(codebook_path),
    }


def validate_survey_design(columns: list[str], survey_path: Path) -> dict[str, Any]:
    design = yaml.safe_load(survey_path.read_text())
    design_info = design.get("design", {})

    results: dict[str, Any] = {"survey_design_path": str(survey_path), "checks": []}
    for field in ("weight_variable", "strata_variable", "cluster_variable"):
        column_name = design_info.get(field)
        if column_name:
            exists = column_name in columns
            results["checks"].append(
                {
                    "field": field,
                    "column": column_name,
                    "exists_in_data": exists,
                }
            )

    replicate_weights = design_info.get("replicate_weights") or []
    if replicate_weights:
        missing = [col for col in replicate_weights if col not in columns]
        results["checks"].append(
            {
                "field": "replicate_weights",
                "missing": missing,
                "total_listed": len(replicate_weights),
            }
        )
    return results


def write_markdown(codebook_summary: dict, survey_summary: dict, output_path: Path):
    lines = [
        "# Metadata Validation Report",
        "",
        "## Codebook vs Dataset",
        f"- Documented variables: {codebook_summary['documented_variables']}",
        f"- Codebook path: `{codebook_summary['codebook_path']}`",
        f"- Variables documented but missing in dataset: {len(codebook_summary['missing_in_data'])}",
    ]
    if codebook_summary["missing_in_data"]:
        lines.append("  - " + ", ".join(codebook_summary["missing_in_data"]))
    lines.append(
        f"- Dataset columns not documented: {codebook_summary['undocumented_columns_count']}"
    )
    lines.append("")
    lines.append("| alias | source_column | exists_in_data |")
    lines.append("| --- | --- | --- |")
    for entry in codebook_summary["documented_entries"]:
        lines.append(
            f"| {entry['alias']} | {entry['source_column']} | {entry['exists_in_data']} |"
        )
    lines.append("")
    lines.append("## Survey Design Checks")
    if survey_summary["checks"]:
        lines.append("| metadata_field | column | exists_in_data | notes |")
        lines.append("| --- | --- | --- | --- |")
        for check in survey_summary["checks"]:
            if check["field"] == "replicate_weights":
                notes = "missing: " + ", ".join(check.get("missing") or ["none"])
                lines.append(
                    f"| replicate_weights | {check['total_listed']} listed | "
                    f"{'OK' if not check.get('missing') else 'incomplete'} | {notes} |"
                )
            else:
                lines.append(
                    f"| {check['field']} | {check['column']} | {check['exists_in_data']} | |"
                )
    else:
        lines.append("No design variables specified; treated as simple random sample per metadata.")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(lines))


def main():
    args = parse_args()
    dataset_path = Path(args.dataset)
    codebook_path = Path(args.codebook)
    survey_path = Path(args.survey_design)

    if not dataset_path.exists():
        raise FileNotFoundError(dataset_path)
    if not codebook_path.exists():
        raise FileNotFoundError(codebook_path)
    if not survey_path.exists():
        raise FileNotFoundError(survey_path)

    columns = load_columns(dataset_path)
    codebook_summary = validate_codebook(columns, codebook_path)
    survey_summary = validate_survey_design(columns, survey_path)

    report = {
        "dataset_path": str(dataset_path),
        "codebook_summary": codebook_summary,
        "survey_summary": survey_summary,
    }
    args.report_json.parent.mkdir(parents=True, exist_ok=True)
    args.report_json.write_text(json.dumps(report, indent=2))

    write_markdown(codebook_summary, survey_summary, args.report_md)


if __name__ == "__main__":
    main()
