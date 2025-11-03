from __future__ import annotations

import argparse, datetime as dt, json, math, random
from pathlib import Path

import numpy as np
import pandas as pd
import yaml


def iso():
    return dt.datetime.now(dt.timezone.utc).isoformat().replace("+00:00", "Z")


def load_codebook(path):
    data = json.loads(path.read_text(encoding="utf-8"))
    return {item.get("name"): item for item in data.get("variables", [])}


def pick(cols, keys):
    return [col for col in cols if any(key in col.lower() for key in keys)]


def summarise(df, names, codebook):
    total = len(df)
    summary = []
    for name in names:
        series = df[name]
        non_missing = series.notna().sum()
        fraction = float(non_missing / total) if total else math.nan
        meta = codebook.get(name) or {}
        summary.append(
            {
                "name": name,
                "codebook_label": meta.get("label"),
                "non_missing_fraction": round(fraction, 6)
                if fraction == fraction
                else None,
                "dtype": str(series.dtype),
            }
        )
    return summary


def detect(df, codebook):
    cols = list(df.columns)
    weight = [
        name
        for name in pick(cols, ["weight"])
        if not (
            "your weight" in name.lower()
            or ("weight" in ((codebook.get(name) or {}).get("label") or "").lower()
                and "clos" in ((codebook.get(name) or {}).get("label") or "").lower())
        )
    ]
    return {
        "weight_candidates": summarise(df, weight, codebook),
        "strata_candidates": summarise(df, pick(cols, ["strata", "stratum"]), codebook),
        "cluster_candidates": summarise(
            df, pick(cols, ["cluster", "psu", "primary sampling unit"]), codebook
        ),
        "replicate_weight_candidates": summarise(
            df, pick(cols, ["replicate", "repwt", "jack", "bootstrap"]), codebook
        ),
    }


def as_table(rows):
    if not rows:
        return "None detected."
    lines = [
        "| name | codebook_label | non_missing_fraction | dtype |",
        "| --- | --- | --- | --- |",
    ]
    for row in rows:
        label = row.get("codebook_label") or "—"
        fraction = row.get("non_missing_fraction")
        fraction_str = f"{fraction:.6f}" if fraction is not None else "—"
        lines.append(
            f"| `{row['name']}` | {label} | {fraction_str} | {row.get('dtype', '—')} |"
        )
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Validate survey design metadata for childhoodbalancedpublic."
    )
    parser.add_argument("--dataset", type=Path, required=True)
    parser.add_argument("--codebook", type=Path, required=True)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    parser.add_argument("--seed", type=int, default=None)
    args = parser.parse_args()

    config = yaml.safe_load(args.config.read_text(encoding="utf-8"))
    seed = args.seed if args.seed is not None else int(config.get("seed", 20251016))
    random.seed(seed)
    np.random.seed(seed)

    df = pd.read_csv(args.dataset, low_memory=False)
    n_obs, n_cols = df.shape
    codebook = load_codebook(args.codebook)
    candidates = detect(df, codebook)

    design = "simple_random_sampling"
    notes = (
        "No survey weights, strata, or clusters detected; proceed as SRS pending provider confirmation."
    )
    command = (
        "python analysis/code/validate_survey_design.py "
        f"--dataset {args.dataset} --codebook {args.codebook} "
        f"--config {args.config} --output {args.output} --report {args.report}"
    )

    payload = {
        "dataset": args.dataset.name,
        "generated_at": iso(),
        "seed": seed,
        "n_observations": n_obs,
        "weight_variable": None,
        "strata_variable": None,
        "cluster_variable": None,
        "replicate_weights": [],
        "fpc": None,
        "assumed_design": design,
        "detection_summary": candidates,
        "notes": notes,
        "validation": {
            "command": command,
            "created_by": "agent",
            "outputs": ["docs/survey_design.yaml", "qc/survey_design_validation.md"],
        },
    }
    args.output.write_text(
        yaml.safe_dump(payload, sort_keys=False, allow_unicode=False), encoding="utf-8"
    )

    report = [
        "# Survey Design Validation",
        f"Generated: {iso()} | Seed: {seed}",
        "",
        f"Command: `{command}`",
        "",
        "## Dataset Summary",
        f"- File: `{args.dataset}`",
        f"- Observations: {n_obs}",
        f"- Columns: {n_cols}",
        f"- Design: **{design.replace('_', ' ').title()}**",
        "",
        "## Detection Summary",
        "### Weight-like Columns",
        as_table(candidates["weight_candidates"]),
        "",
        "### Strata-like Columns",
        as_table(candidates["strata_candidates"]),
        "",
        "### Cluster-like Columns",
        as_table(candidates["cluster_candidates"]),
        "",
        "### Replicate Weight Columns",
        as_table(candidates["replicate_weight_candidates"]),
        "",
        "## Notes",
        notes,
        "",
        "All findings remain exploratory; confirm with documentation when available.",
        "",
        "_Exploratory diagnostics only; no confidential data disclosed._",
    ]
    args.report.write_text("\n".join(report), encoding="utf-8")


if __name__ == "__main__":
    main()
