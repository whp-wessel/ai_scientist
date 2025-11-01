#!/usr/bin/env python3
"""Generate missingness diagnostics for key wellbeing and abuse variables."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List

import numpy as np
import pandas as pd
import statsmodels.api as sm

CONFIG_PATH = Path("config/agent_config.yaml")
DATA_CANDIDATES = [
    Path("data/clean/childhoodbalancedpublic_original.csv"),
    Path("data/raw/childhoodbalancedpublic_original.csv"),
    Path("childhoodbalancedpublic_original.csv"),
]
TARGET_COLUMNS: Dict[str, str] = {
    "self_love": "I love myself (2l8994l)",
    "parental_abuse_0_12": "during ages *0-12*: your parents verbally or emotionally abused you (mds78zu)",
}
NUMERIC_PREDICTORS: List[str] = [
    "selfage",
    "classchild",
    "networth",
    "education",
    "biomale",
]
SMALL_CELL_THRESHOLD = 10
MISSING_TOKENS = {
    "",
    "nan",
    "na",
    "n/a",
    "NaN",
    "NA",
    "N/A",
    "Prefer not to answer",
    "Prefer Not to Answer",
    "prefer not to answer",
}
OUTPUT_SUMMARY = Path("tables/missingness_summary.csv")
OUTPUT_MODELS = Path("tables/missingness_logit_results.csv")
OUTPUT_METADATA = Path("tables/missingness_outputs.json")
QC_REPORT = Path("qc/missingness_analysis.md")


def read_seed(path: Path) -> int:
    seed_val = 0
    if not path.exists():
        return seed_val
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            stripped = line.strip()
            if stripped.startswith("seed:"):
                _, value = stripped.split(":", 1)
                try:
                    seed_val = int(value.strip())
                except ValueError:
                    seed_val = 0
                break
    return seed_val


def resolve_data_path(candidates: List[Path]) -> Path:
    for candidate in candidates:
        if candidate.exists():
            return candidate
    raise FileNotFoundError("Dataset not found in expected locations.")


def normalize_missing(series: pd.Series) -> pd.Series:
    """Return boolean mask identifying interpreted missing values."""
    if series.dtype.kind in {"b", "i", "u", "f"}:
        return series.isna()
    as_str = series.astype(str).str.strip()
    return series.isna() | as_str.isin(MISSING_TOKENS)


def build_summary(df: pd.DataFrame, targets: Dict[str, str]) -> pd.DataFrame:
    records = []
    total = len(df)
    for short_name, col in targets.items():
        if col not in df.columns:
            raise KeyError(f"Column '{col}' not found in dataset.")
        mask = normalize_missing(df[col])
        missing_count = int(mask.sum())
        nonmissing_count = int(total - missing_count)
        missing_display = missing_count if missing_count >= SMALL_CELL_THRESHOLD else f"<{SMALL_CELL_THRESHOLD}"
        missing_pct = round(missing_count / total * 100, 2) if total else np.nan
        missing_pct_display = missing_pct if isinstance(missing_display, int) else np.nan
        records.append(
            {
                "variable_short": short_name,
                "variable_name": col,
                "missing_count": missing_display,
                "missing_pct": missing_pct_display,
                "nonmissing_count": nonmissing_count,
                "nonmissing_pct": round(nonmissing_count / total * 100, 2) if total else np.nan,
            }
        )
    return pd.DataFrame.from_records(records)


def prepare_predictors(df: pd.DataFrame, predictors: List[str]) -> pd.DataFrame:
    prepared = df.copy()
    for col in predictors:
        if col in prepared.columns:
            prepared[col] = pd.to_numeric(prepared[col], errors="coerce")
        else:
            prepared[col] = np.nan
    return prepared


def fit_logit_model(df: pd.DataFrame, indicator_col: str, predictors: List[str]):
    data = df[predictors + [indicator_col]].dropna()
    if data[indicator_col].nunique() < 2:
        raise ValueError(f"Indicator '{indicator_col}' has fewer than two levels after dropping missing predictors.")
    y = data[indicator_col].astype(int)
    X = data[predictors].copy()
    X = sm.add_constant(X, has_constant="add")
    model = sm.Logit(y, X)
    result = model.fit(disp=False, maxiter=200)
    return result, len(data)


def model_to_frame(result: sm.Logit, model_name: str, n_obs: int) -> pd.DataFrame:
    conf = result.conf_int(alpha=0.05)
    frame = pd.DataFrame(
        {
            "model": model_name,
            "term": result.params.index,
            "estimate": result.params.values,
            "std_error": result.bse.values,
            "ci_low": conf[0].values,
            "ci_high": conf[1].values,
            "p_value": result.pvalues.values,
            "n_obs": n_obs,
        }
    )
    return frame


def write_markdown_report(summary: pd.DataFrame, models: Dict[str, sm.Logit], n_obs: Dict[str, int], report_path: Path) -> None:
    report_path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Missingness Diagnostics (Exploratory)",
        "",
        f"Generated: {datetime.now(timezone.utc).isoformat()}",
        "",
        "## Overview",
        "",
        "This exploratory report summarizes missingness patterns for the self-love and parental emotional abuse items.",
        "",
        "### Missingness Rates",
        "",
        "```",
        summary.to_string(index=False),
        "```",
        "",
        "### Logistic Models for Missingness Indicators",
        "",
    ]
    for model_name, result in models.items():
        lines.append(f"#### {model_name}")
        lines.append("")
        lines.append(f"Observations (listwise complete): {n_obs[model_name]}")
        lines.append("")
        lines.append("```")
        lines.append(result.summary2().as_text())
        lines.append("```")
        lines.append("")
    lines.append("_Exploratory output – do not treat as confirmatory evidence._")
    report_path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    seed = read_seed(CONFIG_PATH)
    np.random.seed(seed)

    data_path = resolve_data_path(DATA_CANDIDATES)
    df = pd.read_csv(data_path, low_memory=False)

    summary = build_summary(df, TARGET_COLUMNS)

    predictors_df = prepare_predictors(df, NUMERIC_PREDICTORS)
    models = {}
    n_obs = {}
    model_frames = []

    for short_name, column in TARGET_COLUMNS.items():
        indicator_name = f"missing_{short_name}"
        predictors_df[indicator_name] = normalize_missing(df[column]).astype(int)
        try:
            result, n_obs_val = fit_logit_model(predictors_df, indicator_name, NUMERIC_PREDICTORS)
        except Exception as exc:  # pylint: disable=broad-except
            raise RuntimeError(f"Failed to fit logistic model for {short_name}: {exc}") from exc
        models[short_name] = result
        n_obs[short_name] = n_obs_val
        model_frames.append(model_to_frame(result, f"logit_missing_{short_name}", n_obs_val))

    OUTPUT_SUMMARY.parent.mkdir(parents=True, exist_ok=True)
    summary.to_csv(OUTPUT_SUMMARY, index=False)

    all_models = pd.concat(model_frames, ignore_index=True)
    all_models.to_csv(OUTPUT_MODELS, index=False)

    OUTPUT_METADATA.write_text(
        json.dumps(
            {
                "generated_at_utc": datetime.now(timezone.utc).isoformat(),
                "seed": seed,
                "data_path": str(data_path.resolve()),
                "outputs": [str(OUTPUT_SUMMARY), str(OUTPUT_MODELS), str(QC_REPORT)],
            },
            indent=2,
        ),
        encoding="utf-8",
    )

    write_markdown_report(summary, models, n_obs, QC_REPORT)


if __name__ == "__main__":
    main()
