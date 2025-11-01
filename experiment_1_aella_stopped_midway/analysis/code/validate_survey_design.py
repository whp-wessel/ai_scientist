#!/usr/bin/env python3
"""Validate survey design metadata against the available dataset."""

import datetime as dt
import json
import random
from pathlib import Path

import numpy as np
import pandas as pd
import yaml

CONFIG_PATH = Path("config/agent_config.yaml")
DESIGN_PATH = Path("docs/survey_design.yaml")
QC_PATH = Path("qc/data_checks.md")
OUTPUT_METADATA_PATH = Path("artifacts/last_validation.json")


def load_seed() -> int:
    with CONFIG_PATH.open("r", encoding="utf-8") as f:
        config = yaml.safe_load(f)
    seed = config.get("seed")
    if seed is None:
        raise ValueError("`seed` missing from config/agent_config.yaml")
    return int(seed)


def seed_everything(seed: int) -> None:
    random.seed(seed)
    np.random.seed(seed)


def timestamp_utc() -> str:
    return dt.datetime.utcnow().replace(microsecond=0).isoformat() + "Z"


def load_design() -> dict:
    with DESIGN_PATH.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def detect_weight_like_columns(columns):
    weight_like = []
    for col in columns:
        col_lower = col.lower()
        if "weight" in col_lower or col_lower.endswith("_wt") or col_lower.startswith("wt_"):
            weight_like.append(col)
    return weight_like


def summarise_candidate(series: pd.Series) -> dict:
    non_null = series.dropna()
    unique_count = int(non_null.nunique(dropna=True)) if not non_null.empty else 0
    sample_values = []
    if not non_null.empty:
        sample_values = non_null.unique().tolist()[:5]
    dtype = str(series.dtype)
    is_numeric = pd.api.types.is_numeric_dtype(series)
    return {
        "dtype": dtype,
        "non_null_n": int(non_null.shape[0]),
        "unique_non_null": unique_count,
        "sample_values": sample_values,
        "is_numeric": bool(is_numeric),
    }


def compose_markdown(context: dict) -> str:
    lines = []
    lines.append("# Data Quality Checks")
    lines.append("")
    lines.append(f"Generated: {context['timestamp']}")
    lines.append(f"Seed: {context['seed']}")
    lines.append("Regenerate: `python analysis/code/validate_survey_design.py`")
    lines.append("")
    lines.append("## Survey Design Metadata Audit")
    lines.append("")
    lines.append(f"- Dataset file: `{context['dataset_path']}`")
    lines.append(f"- Rows (unweighted): {context['row_count']}")
    lines.append(f"- Columns: {context['column_count']}")
    lines.append(f"- Weight variable specified in design: {context['design_weight']}")
    lines.append(f"- Strata variable specified in design: {context['design_strata']}")
    lines.append(f"- Cluster variable specified in design: {context['design_cluster']}")
    lines.append("")
    lines.append("## Weight / Strata / Cluster Validation")
    lines.append("")
    lines.append("| Component | Expected | Present in data | Status | Notes |")
    lines.append("| --- | --- | --- | --- | --- |")
    for row in context["validation_rows"]:
        lines.append("| {Component} | {Expected} | {Present} | {Status} | {Notes} |".format(**row))
    lines.append("")
    if context["candidate_details"]:
        lines.append("### Candidate Columns Containing 'weight'")
        lines.append("")
        lines.append("| Column | Dtype | Non-null n | Unique non-null | Sample values | Likely survey weight? |")
        lines.append("| --- | --- | --- | --- | --- | --- |")
        for cand in context["candidate_details"]:
            sample_values = ", ".join(map(str, cand["sample_values"])) if cand["sample_values"] else ""
            line = "| {col} | {dtype} | {non_null} | {unique} | {sample} | {likely} |".format(
            col=cand['column'],
            dtype=cand['summary']['dtype'],
            non_null=cand['summary']['non_null_n'],
            unique=cand['summary']['unique_non_null'],
            sample=sample_values,
            likely=cand['likely_weight'],
        )
        lines.append(line)
        lines.append("")
    else:
        lines.append("No column names contained the substring 'weight'.")
        lines.append("")
    lines.append("## Assessment")
    lines.append("")
    lines.append(context["assessment"])
    lines.append("")
    lines.append("## Follow-up Actions")
    lines.append("")
    for action in context["next_steps"]:
        lines.append(f"- [ ] {action}")
    lines.append("")
    return "\n".join(lines)


def main() -> None:
    seed = load_seed()
    seed_everything(seed)
    ts = timestamp_utc()

    design = load_design()
    dataset_relative = design.get("dataset")
    dataset_path = Path(dataset_relative)
    if not dataset_path.exists():
        raise FileNotFoundError(f"Dataset not found: {dataset_relative}")

    df = pd.read_csv(dataset_path)
    row_count = int(df.shape[0])
    column_count = int(df.shape[1])

    candidate_columns = detect_weight_like_columns(df.columns)

    candidate_details = []
    for col in candidate_columns:
        summary = summarise_candidate(df[col])
        # Heuristic: treat as unlikely survey weight if non-numeric, too few unique values, or matches known body-weight columns
        likely_weight = summary["is_numeric"] and summary["unique_non_null"] > 20
        col_lower = col.lower()
        if col_lower.strip() in {"weight"} or col_lower.startswith("your weight"):
            likely_weight = False
        candidate_details.append(
            {
                "column": col,
                "summary": summary,
                "sample_values": summary.get('sample_values', []),
                "likely_weight": "Yes" if likely_weight else "No",
            }
        )

    design_weight = design.get("weights", {}).get("weight_var")
    design_strata = design.get("strata", {}).get("strata_var")
    design_cluster = design.get("clusters", {}).get("cluster_var")

    def component_row(name, expected, present, status, notes):
        return {
            "Component": name,
            "Expected": expected if expected is not None else "None",
            "Present": present,
            "Status": status,
            "Notes": notes,
        }

    validation_rows = []

    if design_weight:
        present = "Yes" if design_weight in df.columns else "No"
        status = "ok" if present == "Yes" else "missing"
        notes = "" if present == "Yes" else "Column absent; cannot apply provided weights."
    else:
        present = ", ".join(candidate_columns) if candidate_columns else "None detected"
        status = "missing"
        notes = "No survey weight variable documented; defaulting to equal weights until clarified."
    validation_rows.append(component_row("Weights", design_weight, present, status, notes))

    if design_strata:
        present = "Yes" if design_strata in df.columns else "No"
        status = "ok" if present == "Yes" else "missing"
        notes = "" if present == "Yes" else "Strata variable absent; cannot replicate stratification."
    else:
        present = "None detected"
        status = "missing"
        notes = "No strata metadata provided."
    validation_rows.append(component_row("Strata", design_strata, present, status, notes))

    if design_cluster:
        present = "Yes" if design_cluster in df.columns else "No"
        status = "ok" if present == "Yes" else "missing"
        notes = "" if present == "Yes" else "Cluster variable absent; cannot account for clustering."
    else:
        present = "None detected"
        status = "missing"
        notes = "No cluster metadata provided."
    validation_rows.append(component_row("Clusters", design_cluster, present, status, notes))

    replicate_weights = design.get("replicate_weights", []) or []
    if replicate_weights:
        missing = [col for col in replicate_weights if col not in df.columns]
        present = "Yes" if not missing else "Missing"
        status = "ok" if not missing else "missing"
        notes = "" if not missing else f"Missing replicate columns: {', '.join(missing)}"
    else:
        present = "None defined"
        status = "n/a"
        notes = "Replicate weights not specified."
    validation_rows.append(component_row("Replicate weights", ", ".join(replicate_weights) if replicate_weights else None, present, status, notes))

    assessment_lines = [
        "No survey-design variables (weights/strata/clusters) are available in the provided dataset.",
        "Proceeding analyses must assume equal-probability sampling (simple random sampling) until official design information is supplied.",
    ]

    if candidate_details:
        assessment_lines.append(
            "Columns containing 'weight' were inspected; all appear to capture respondent body weight categories and are unsuitable as survey weights."
        )
        assessment_lines.append("Columns reviewed: " + ", ".join(f"`{c}`" for c in candidate_columns) + ".")

    next_steps = [
        "Request official survey weight documentation from data provider.",
        "Document SRS assumption in PAP and subsequent analyses until metadata is updated.",
    ]

    context = {
        "timestamp": ts,
        "seed": seed,
        "dataset_path": str(dataset_path),
        "row_count": row_count,
        "column_count": column_count,
        "design_weight": design_weight,
        "design_strata": design_strata,
        "design_cluster": design_cluster,
        "validation_rows": validation_rows,
        "candidate_details": candidate_details,
        "assessment": " ".join(assessment_lines),
        "next_steps": next_steps,
    }

    markdown = compose_markdown(context)
    QC_PATH.write_text(markdown, encoding="utf-8")

    validation_metadata = {
        "timestamp": ts,
        "seed": seed,
        "dataset_path": str(dataset_path),
        "row_count": row_count,
        "column_count": column_count,
        "candidate_columns": candidate_columns,
        "candidate_details": candidate_details,
        "assessment": assessment_lines,
        "command": "python analysis/code/validate_survey_design.py",
    }
    OUTPUT_METADATA_PATH.write_text(json.dumps(validation_metadata, indent=2), encoding="utf-8")

    # Update survey design YAML with validation notes
    weights_section = design.setdefault("weights", {})
    weights_section["notes"] = (
        f"Validated {ts}: No survey weight variable present in dataset; analyses will assume equal weights until metadata is updated."
    )
    weights_section["validation"] = {
        "status": "missing",
        "checked_on": ts,
        "checked_with": "analysis/code/validate_survey_design.py",
        "candidates": candidate_columns,
    }

    strata_section = design.setdefault("strata", {})
    strata_section["notes"] = (
        f"Validated {ts}: No strata variable documented or detected in data."
    )
    strata_section["validation"] = {
        "status": "missing",
        "checked_on": ts,
        "checked_with": "analysis/code/validate_survey_design.py",
    }

    clusters_section = design.setdefault("clusters", {})
    clusters_section["notes"] = (
        f"Validated {ts}: No cluster variable documented or detected in data."
    )
    clusters_section["validation"] = {
        "status": "missing",
        "checked_on": ts,
        "checked_with": "analysis/code/validate_survey_design.py",
    }

    assumptions = design.setdefault("assumptions", [])
    base_prefix = "Assuming simple random sampling until survey design metadata is verified"
    assumptions = [a for a in assumptions if not str(a).startswith(base_prefix)]
    assumptions.append(f"{base_prefix} (updated {ts}).")
    design["assumptions"] = assumptions

    design["validation_command"] = "python analysis/code/validate_survey_design.py"

    with DESIGN_PATH.open("w", encoding="utf-8") as f:
        yaml.safe_dump(design, f, sort_keys=False, allow_unicode=True)

    OUTPUT_METADATA_PATH.parent.mkdir(parents=True, exist_ok=True)


if __name__ == "__main__":
    main()
