#!/usr/bin/env python3
"""MI robustness runner for HYP-001 and HYP-002.

The script compares complete-case and multiple-imputation specifications
(prototype and reduced-auxiliary) for key hypotheses. Outputs include
scenario-tagged coefficient tables, predictive summaries, metadata JSON,
and Markdown narratives with regeneration commands.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import math
import shlex
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Tuple

import numpy as np
import pandas as pd
import statsmodels.api as sm
from scipy import stats
from statsmodels.miscmodels.ordinal_model import OrderedModel
import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_DATASET = REPO_ROOT / "childhoodbalancedpublic_original.csv"
DEFAULT_MI_PROTOTYPE = REPO_ROOT / "data" / "derived" / "childhoodbalancedpublic_mi_prototype.csv.gz"
DEFAULT_MI_REDUCED = REPO_ROOT / "data" / "derived" / "childhoodbalancedpublic_mi_reduced_aux.csv.gz"
DEFAULT_MAPPING_PROTOTYPE = REPO_ROOT / "analysis" / "imputation" / "mice_variable_map.json"
DEFAULT_MAPPING_REDUCED = REPO_ROOT / "analysis" / "imputation" / "mice_variable_map__reduced_aux.json"
DEFAULT_OUTPUT_DIR = REPO_ROOT / "tables"
DEFAULT_NOTE_DIR = REPO_ROOT / "analysis" / "imputation"
DEFAULT_CONFIG = REPO_ROOT / "config" / "agent_config.yaml"
DEFAULT_ALPHA = 0.05
SMALL_CELL_THRESHOLD = 10
ALLOWED_HYPOTHESES = {"HYP-001", "HYP-002"}

spec = importlib.util.spec_from_file_location(
    "pap_runner", REPO_ROOT / "analysis" / "code" / "run_pap_models.py"
)
pap = importlib.util.module_from_spec(spec)
if spec.loader is None:  # pragma: no cover - defensive
    raise ImportError("Unable to load run_pap_models module")
sys.modules[spec.name] = pap
spec.loader.exec_module(pap)  # type: ignore[arg-type]

prepare_hyp001_mi = pap.prepare_hyp001_mi
fit_mi_linear = pap.fit_mi_linear
prepare_hyp002_mi = pap.prepare_hyp002_mi
fit_mi_ordered_logit = pap.fit_mi_ordered_logit
df_to_markdown = pap.df_to_markdown
ensure_dir = pap.ensure_dir
serialize_metadata = pap.serialize_metadata
load_project_seed = pap.load_project_seed
set_global_seed = pap.set_global_seed


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run MI robustness checks for PAP hypotheses")
    parser.add_argument("--dataset", type=Path, default=DEFAULT_DATASET)
    parser.add_argument("--mi-prototype", type=Path, default=DEFAULT_MI_PROTOTYPE)
    parser.add_argument("--mi-reduced", type=Path, default=DEFAULT_MI_REDUCED)
    parser.add_argument("--mapping-prototype", type=Path, default=DEFAULT_MAPPING_PROTOTYPE)
    parser.add_argument("--mapping-reduced", type=Path, default=DEFAULT_MAPPING_REDUCED)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--note-dir", type=Path, default=DEFAULT_NOTE_DIR)
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--seed", type=int, default=None)
    parser.add_argument("--alpha", type=float, default=DEFAULT_ALPHA)
    parser.add_argument("--cell-threshold", type=int, default=SMALL_CELL_THRESHOLD)
    parser.add_argument(
        "--hypotheses",
        nargs="+",
        default=["HYP-001", "HYP-002"],
        help="Subset of hypotheses to process",
    )
    return parser.parse_args()


def resolve_path(path: Path) -> Path:
    return path if path.is_absolute() else (REPO_ROOT / path)


def load_mapping(path: Path) -> Optional[Dict[str, str]]:
    resolved = resolve_path(path)
    if not resolved.exists():
        return None
    mapping_raw = json.loads(resolved.read_text(encoding="utf-8"))
    if isinstance(mapping_raw, dict):
        return {value: key for key, value in mapping_raw.items()}
    return None


def load_mi_dataset(path: Path, columns: Optional[Sequence[str]] = None) -> Optional[pd.DataFrame]:
    resolved = resolve_path(path)
    if not resolved.exists() or resolved.stat().st_size == 0:
        return None
    return pd.read_csv(resolved, usecols=columns, low_memory=False)


def load_base_dataset(path: Path, hypotheses: List[str]) -> pd.DataFrame:
    required: set[str] = set()
    if "HYP-001" in hypotheses:
        required.update(
            {
                "selfage",
                "gendermale",
                "education",
                "I love myself (2l8994l)",
                "during ages *0-12*: your parents verbally or emotionally abused you (mds78zu)",
            }
        )
    if "HYP-002" in hypotheses:
        required.update({"selfage", "gendermale", "education", "networth", "classchild"})
    resolved = resolve_path(path)
    return pd.read_csv(resolved, usecols=sorted(required), low_memory=False)


def prepare_hyp001_complete_case(
    df: pd.DataFrame,
    cell_threshold: int,
) -> Tuple[pd.DataFrame, Dict[str, object]]:
    outcome_col = "I love myself (2l8994l)"
    predictor_col = "during ages *0-12*: your parents verbally or emotionally abused you (mds78zu)"
    control_cols = ["selfage", "gendermale", "education"]

    required = [outcome_col, predictor_col, *control_cols]
    missing = [col for col in required if col not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {', '.join(missing)}")

    subset = df[required].apply(pd.to_numeric, errors="coerce").dropna()
    if subset.empty:
        raise ValueError("No observations remain for HYP-001 complete-case analysis")

    counts = subset[predictor_col].value_counts()
    if (counts < cell_threshold).any():
        low = ", ".join(sorted(set(str(k) for k, v in counts.items() if v < cell_threshold)))
        raise ValueError(
            f"Abuse levels below disclosure threshold in complete-case data: {low}"
        )

    prepared = subset.rename(
        columns={
            outcome_col: "self_love",
            predictor_col: "abuse",
        }
    )
    prepared = prepared[["self_love", "abuse", *control_cols]]

    control_means = {col: float(prepared[col].mean()) for col in control_cols}
    abuse_levels = sorted(float(level) for level in prepared["abuse"].unique())

    metadata = {
        "source": "complete_case",
        "n_observations": int(len(prepared)),
        "abuse_levels": abuse_levels,
        "control_means": control_means,
        "cell_threshold": cell_threshold,
        "abuse_level_counts": {str(k): int(v) for k, v in counts.items()},
    }
    return prepared, metadata


def fit_complete_case_linear(
    df: pd.DataFrame,
    alpha: float,
) -> Tuple[pd.DataFrame, pd.DataFrame, Dict[str, object]]:
    y = df["self_love"].astype(float)
    exog_cols = [col for col in df.columns if col != "self_love"]
    X = sm.add_constant(df[exog_cols].astype(float))
    result = sm.OLS(y, X).fit(cov_type="HC1")

    ci = result.conf_int(alpha)
    summary_df = pd.DataFrame(
        {
            "term": result.params.index,
            "model": "complete_case_linear",
            "estimate": result.params.values,
            "std_error": result.bse.values,
            "df": [float(result.df_resid)] * len(result.params),
            "stat": result.tvalues.values,
            "p_value": result.pvalues.values,
            "ci_low": ci[0].values,
            "ci_high": ci[1].values,
        }
    )

    control_cols = [col for col in exog_cols if col != "abuse"]
    control_means = {col: float(df[col].mean()) for col in control_cols}
    abuse_levels = sorted(float(level) for level in df["abuse"].unique())

    design_rows: List[Dict[str, float]] = []
    for level in abuse_levels:
        row = {"const": 1.0, "abuse": float(level)}
        for col in control_cols:
            row[col] = control_means.get(col, 0.0)
        design_rows.append(row)

    design = pd.DataFrame(design_rows)[result.params.index]
    prediction = result.get_prediction(design)
    pred_summary = prediction.summary_frame(alpha=alpha)
    pred_df = pd.DataFrame(
        {
            "abuse_level": abuse_levels,
            "predicted_self_love": pred_summary["mean"].astype(float),
            "std_error": pred_summary["mean_se"].astype(float),
            "ci_low": pred_summary["mean_ci_lower"].astype(float),
            "ci_high": pred_summary["mean_ci_upper"].astype(float),
        }
    )

    metadata = {
        "model": "OLS_HC1_complete_case",
        "n_observations": int(len(df)),
        "df_resid": float(result.df_resid),
        "alpha": alpha,
        "prediction_controls_at": control_means,
    }
    return summary_df, pred_df, metadata


def prepare_hyp002_complete_case(
    df: pd.DataFrame,
    cell_threshold: int,
) -> Tuple[pd.DataFrame, Dict[str, object]]:
    outcome_col = "networth"
    predictor_col = "classchild"
    control_cols = ["selfage", "gendermale", "education"]

    required = [outcome_col, predictor_col, *control_cols]
    missing = [col for col in required if col not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {', '.join(missing)}")

    subset = df[required].apply(pd.to_numeric, errors="coerce").dropna()
    if subset.empty:
        raise ValueError("No observations remain for HYP-002 complete-case analysis")

    subset[outcome_col] = subset[outcome_col].round().astype(int)
    subset[predictor_col] = subset[predictor_col].astype(float)

    networth_levels = sorted(int(level) for level in subset[outcome_col].unique())
    networth_labels = [str(level) for level in networth_levels]
    label_map = {level: str(level) for level in networth_levels}

    subset["networth_category"] = pd.Categorical(
        subset[outcome_col].map(label_map),
        categories=networth_labels,
        ordered=True,
    )

    counts = subset["networth_category"].value_counts()
    if (counts < cell_threshold).any():
        low = ", ".join(sorted(set(str(k) for k, v in counts.items() if v < cell_threshold)))
        raise ValueError(
            f"Net worth categories below disclosure threshold in complete-case data: {low}"
        )

    classchild_levels = sorted(float(level) for level in subset[predictor_col].unique())
    control_means = {col: float(subset[col].mean()) for col in control_cols}

    prepared = subset[["networth_category", predictor_col, *control_cols]].rename(
        columns={predictor_col: "classchild"}
    )

    metadata = {
        "source": "complete_case",
        "n_observations": int(len(prepared)),
        "networth_levels": networth_levels,
        "classchild_levels": classchild_levels,
        "control_means": control_means,
        "cell_threshold": cell_threshold,
        "networth_counts": {str(k): int(v) for k, v in counts.items()},
    }
    return prepared, metadata


def fit_complete_case_ordered_logit(
    df: pd.DataFrame,
    alpha: float,
) -> Tuple[pd.DataFrame, pd.DataFrame, Dict[str, object]]:
    outcome = df["networth_category"]
    if hasattr(outcome, "cat"):
        category_labels = list(outcome.cat.categories)
    else:
        category_labels = [str(item) for item in sorted(outcome.unique())]
    exog_cols = ["classchild", "selfage", "gendermale", "education"]
    exog = df[exog_cols].astype(float)
    model = OrderedModel(outcome, exog, distr="logit")
    result = model.fit(method="bfgs", disp=False, maxiter=1000, cov_type="HC1")

    param_names = list(result.model.data.param_names)
    params = pd.Series(np.asarray(result.params), index=param_names, dtype=float)
    bse = pd.Series(np.asarray(result.bse), index=param_names, dtype=float)
    z_scores = params / bse
    p_values = pd.Series(
        2 * stats.norm.sf(np.abs(z_scores)),
        index=param_names,
        dtype=float,
    )
    crit = stats.norm.ppf(1 - alpha / 2)
    ci_low = params - crit * bse
    ci_high = params + crit * bse

    summary_df = pd.DataFrame(
        {
            "term": param_names,
            "model": "complete_case_ordered_logit",
            "estimate": params.to_numpy(),
            "std_error": bse.to_numpy(),
            "df": [np.nan] * len(param_names),
            "stat": z_scores.to_numpy(),
            "p_value": p_values.to_numpy(),
            "ci_low": ci_low.to_numpy(),
            "ci_high": ci_high.to_numpy(),
        }
    )

    control_means = {
        col: float(df[col].mean())
        for col in ["selfage", "gendermale", "education"]
    }
    classchild_levels = sorted(float(level) for level in df["classchild"].unique())

    prob_rows = []
    for level in classchild_levels:
        row = {"classchild": float(level)}
        for col, mean in control_means.items():
            row[col] = mean
        prob_rows.append(row)
    prob_exog = pd.DataFrame(prob_rows)[exog_cols]
    prob_matrix = result.model.predict(result.params, exog=prob_exog, which="prob")
    prob_df = pd.DataFrame(prob_matrix, columns=category_labels)
    prob_df.insert(0, "classchild_level", classchild_levels)

    metadata = {
        "model": "ordered_logit_HC1_complete_case",
        "n_observations": int(len(df)),
        "alpha": alpha,
        "prediction_controls_at": control_means,
    }
    return summary_df, prob_df, metadata


def add_scenario_column(df: pd.DataFrame, scenario: str) -> pd.DataFrame:
    result = df.copy()
    result.insert(0, "scenario", scenario)
    return result


def build_narrative(
    hypothesis: str,
    coeff_df: pd.DataFrame,
    note_path: Path,
    tables: Dict[str, str],
    scenarios: List[str],
    seed: int,
    alpha: float,
    skipped: List[str],
    command: str,
) -> None:
    timestamp = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    key_term = "abuse" if hypothesis == "HYP-001" else "classchild"
    focus = coeff_df[coeff_df["term"] == key_term]
    lines = [
        f"# {hypothesis} MI Robustness (Exploratory)",
        "",
        f"- Completed: {timestamp}",
        f"- Seed: {seed}",
        f"- Alpha: {alpha}",
        f"- Scenarios: {', '.join(scenarios) if scenarios else 'None'}",
    ]
    if skipped:
        lines.append(f"- Skipped: {', '.join(skipped)}")
    for label, path in tables.items():
        lines.append(f"- {label}: `{path}`")
    lines.append("")
    lines.append("## Key Comparisons")
    if focus.empty:
        lines.append("- Target term not found; review coefficient table.")
    else:
        for row in focus.itertuples(index=False):
            lines.append(
                f"- {row.scenario}: estimate={row.estimate:.4f}, 95% CI [{row.ci_low:.4f}, {row.ci_high:.4f}]"
            )
        if len(focus) > 1:
            delta_max = focus["estimate"].max() - focus["estimate"].min()
            lines.append(f"- Max difference across scenarios: {delta_max:.4f}.")
    lines.extend(
        [
            "",
            "## Regeneration",
            "```bash",
            command,
            "```",
        ]
    )
    note_path.parent.mkdir(parents=True, exist_ok=True)
    note_path.write_text("\n".join(lines), encoding="utf-8")


def write_tables(
    stem: str,
    coeff_df: pd.DataFrame,
    secondary_df: pd.DataFrame,
    output_dir: Path,
) -> Dict[str, str]:
    ensure_dir(output_dir)
    coeff_csv = output_dir / f"{stem}_coefficients.csv"
    coeff_md = output_dir / f"{stem}_coefficients.md"
    secondary_csv = output_dir / f"{stem}_secondary.csv"
    secondary_md = output_dir / f"{stem}_secondary.md"

    coeff_df.to_csv(coeff_csv, index=False)
    coeff_md.write_text(
        f"# {stem.replace('_', ' ').title()} — Coefficients\n\n" + df_to_markdown(coeff_df),
        encoding="utf-8",
    )

    secondary_df.to_csv(secondary_csv, index=False)
    secondary_md.write_text(
        f"# {stem.replace('_', ' ').title()} — Secondary Summary\n\n" + df_to_markdown(secondary_df),
        encoding="utf-8",
    )

    return {
        "Coefficient CSV": str(coeff_csv.relative_to(REPO_ROOT)),
        "Coefficient Markdown": str(coeff_md.relative_to(REPO_ROOT)),
        "Secondary CSV": str(secondary_csv.relative_to(REPO_ROOT)),
        "Secondary Markdown": str(secondary_md.relative_to(REPO_ROOT)),
    }


def main() -> None:
    args = parse_args()
    hypotheses = [hyp.upper() for hyp in args.hypotheses]
    for hyp in hypotheses:
        if hyp not in ALLOWED_HYPOTHESES:
            raise ValueError(f"Unsupported hypothesis: {hyp}")

    dataset_df = load_base_dataset(args.dataset, hypotheses)

    seed = args.seed or load_project_seed(resolve_path(args.config)) or 0
    set_global_seed(seed)

    mi_columns = {"imputation_id", "selfage", "gendermale", "education"}
    if "HYP-001" in hypotheses:
        mi_columns.update({"i_love_myself_2l8994l", "during_ages_0_12_your_parents_verbally_or_emotionally_abused_you_mds78zu"})
    if "HYP-002" in hypotheses:
        mi_columns.update({"networth", "classchild"})

    mi_prototype_df = load_mi_dataset(args.mi_prototype, columns=sorted(mi_columns))
    mi_reduced_df = load_mi_dataset(args.mi_reduced, columns=sorted(mi_columns))
    map_prototype = load_mapping(args.mapping_prototype)
    map_reduced = load_mapping(args.mapping_reduced)

    command = "python analysis/code/run_mi_robustness.py " + " ".join(
        shlex.quote(arg) for arg in sys.argv[1:]
    )
    results_summary: Dict[str, object] = {
        "hypotheses": hypotheses,
        "seed": seed,
        "alpha": args.alpha,
        "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "command": command,
        "scenarios": {},
    }
    manifest_outputs: List[str] = []

    if "HYP-001" in hypotheses:
        coeff_frames: List[pd.DataFrame] = []
        secondary_frames: List[pd.DataFrame] = []
        scenarios: List[str] = []
        skipped: List[str] = []
        scenario_meta: Dict[str, object] = {}

        try:
            prepared_cc, meta_cc = prepare_hyp001_complete_case(dataset_df, args.cell_threshold)
            cc_summary, cc_pred, cc_model_meta = fit_complete_case_linear(prepared_cc, args.alpha)
            coeff_frames.append(add_scenario_column(cc_summary, "complete_case"))
            secondary_frames.append(add_scenario_column(cc_pred, "complete_case"))
            scenarios.append("complete_case")
            scenario_meta["complete_case"] = {**meta_cc, **cc_model_meta}
        except Exception as exc:  # pragma: no cover - defensive
            skipped.append(f"complete_case ({exc})")

        if mi_prototype_df is not None:
            try:
                prepped_proto = prepare_hyp001_mi(
                    mi_prototype_df,
                    args.cell_threshold,
                    column_map=map_prototype,
                )
                proto_summary, proto_pred, proto_meta = fit_mi_linear(prepped_proto, alpha=args.alpha)
                coeff_frames.append(add_scenario_column(proto_summary, "mi_prototype"))
                secondary_frames.append(add_scenario_column(proto_pred, "mi_prototype"))
                scenarios.append("mi_prototype")
                scenario_meta["mi_prototype"] = serialize_metadata(proto_meta)
            except Exception as exc:  # pragma: no cover - defensive
                skipped.append(f"mi_prototype ({exc})")
        else:
            skipped.append("mi_prototype (dataset missing)")

        if mi_reduced_df is not None:
            try:
                prepped_reduced = prepare_hyp001_mi(
                    mi_reduced_df,
                    args.cell_threshold,
                    column_map=map_reduced,
                )
                reduced_summary, reduced_pred, reduced_meta = fit_mi_linear(
                    prepped_reduced, alpha=args.alpha
                )
                coeff_frames.append(add_scenario_column(reduced_summary, "mi_reduced_aux"))
                secondary_frames.append(add_scenario_column(reduced_pred, "mi_reduced_aux"))
                scenarios.append("mi_reduced_aux")
                scenario_meta["mi_reduced_aux"] = serialize_metadata(reduced_meta)
            except Exception as exc:  # pragma: no cover - defensive
                skipped.append(f"mi_reduced_aux ({exc})")
        else:
            skipped.append("mi_reduced_aux (dataset missing)")

        if not coeff_frames:
            raise RuntimeError("HYP-001 robustness failed; no scenarios succeeded")

        coeff_df = pd.concat(coeff_frames, ignore_index=True)
        secondary_df = pd.concat(secondary_frames, ignore_index=True)
        stem = "robustness_hyp001_mi_scenarios"
        table_paths = write_tables(stem, coeff_df, secondary_df, resolve_path(args.output_dir))
        manifest_outputs.extend(table_paths.values())
        note_path = resolve_path(args.note_dir) / f"{stem}.md"
        build_narrative(
            "HYP-001",
            coeff_df,
            note_path,
            table_paths,
            scenarios,
            seed,
            args.alpha,
            skipped,
            command,
        )
        manifest_outputs.append(str(note_path.relative_to(REPO_ROOT)))
        metadata_path = resolve_path(args.output_dir) / f"{stem}_metadata.json"
        metadata_payload = serialize_metadata(
            {
                "hypothesis": "HYP-001",
                "scenarios": scenario_meta,
                "skipped": skipped,
                "outputs": table_paths,
                "note": str(note_path.relative_to(REPO_ROOT)),
            }
        )
        metadata_path.write_text(json.dumps(metadata_payload, indent=2), encoding="utf-8")
        manifest_outputs.append(str(metadata_path.relative_to(REPO_ROOT)))
        results_summary["scenarios"]["HYP-001"] = {
            "available": scenarios,
            "skipped": skipped,
            "coefficients": table_paths["Coefficient CSV"],
            "secondary": table_paths["Secondary CSV"],
        }

    if "HYP-002" in hypotheses:
        coeff_frames = []
        secondary_frames = []
        scenarios = []
        skipped: List[str] = []
        scenario_meta = {}

        try:
            prepared_cc, meta_cc = prepare_hyp002_complete_case(dataset_df, args.cell_threshold)
            cc_summary, cc_probs, cc_model_meta = fit_complete_case_ordered_logit(
                prepared_cc, args.alpha
            )
            coeff_frames.append(add_scenario_column(cc_summary, "complete_case"))
            secondary_frames.append(add_scenario_column(cc_probs, "complete_case"))
            scenarios.append("complete_case")
            scenario_meta["complete_case"] = {**meta_cc, **cc_model_meta}
        except Exception as exc:  # pragma: no cover - defensive
            skipped.append(f"complete_case ({exc})")

        if mi_prototype_df is not None:
            try:
                prepped_proto = prepare_hyp002_mi(
                    mi_prototype_df,
                    args.cell_threshold,
                    column_map=map_prototype,
                )
                proto_summary, proto_probs, proto_meta = fit_mi_ordered_logit(
                    prepped_proto, alpha=args.alpha
                )
                coeff_frames.append(add_scenario_column(proto_summary, "mi_prototype"))
                secondary_frames.append(add_scenario_column(proto_probs, "mi_prototype"))
                scenarios.append("mi_prototype")
                scenario_meta["mi_prototype"] = serialize_metadata(proto_meta)
            except Exception as exc:  # pragma: no cover - defensive
                skipped.append(f"mi_prototype ({exc})")
        else:
            skipped.append("mi_prototype (dataset missing)")

        if mi_reduced_df is not None:
            try:
                prepped_reduced = prepare_hyp002_mi(
                    mi_reduced_df,
                    args.cell_threshold,
                    column_map=map_reduced,
                )
                reduced_summary, reduced_probs, reduced_meta = fit_mi_ordered_logit(
                    prepped_reduced, alpha=args.alpha
                )
                coeff_frames.append(add_scenario_column(reduced_summary, "mi_reduced_aux"))
                secondary_frames.append(add_scenario_column(reduced_probs, "mi_reduced_aux"))
                scenarios.append("mi_reduced_aux")
                scenario_meta["mi_reduced_aux"] = serialize_metadata(reduced_meta)
            except Exception as exc:  # pragma: no cover - defensive
                skipped.append(f"mi_reduced_aux ({exc})")
        else:
            skipped.append("mi_reduced_aux (dataset missing)")

        if not coeff_frames:
            raise RuntimeError("HYP-002 robustness failed; no scenarios succeeded")

        coeff_df = pd.concat(coeff_frames, ignore_index=True)
        secondary_df = pd.concat(secondary_frames, ignore_index=True)
        stem = "robustness_hyp002_mi_scenarios"
        table_paths = write_tables(stem, coeff_df, secondary_df, resolve_path(args.output_dir))
        manifest_outputs.extend(table_paths.values())
        note_path = resolve_path(args.note_dir) / f"{stem}.md"
        build_narrative(
            "HYP-002",
            coeff_df,
            note_path,
            table_paths,
            scenarios,
            seed,
            args.alpha,
            skipped,
            command,
        )
        manifest_outputs.append(str(note_path.relative_to(REPO_ROOT)))
        metadata_path = resolve_path(args.output_dir) / f"{stem}_metadata.json"
        metadata_payload = serialize_metadata(
            {
                "hypothesis": "HYP-002",
                "scenarios": scenario_meta,
                "skipped": skipped,
                "outputs": table_paths,
                "note": str(note_path.relative_to(REPO_ROOT)),
            }
        )
        metadata_path.write_text(json.dumps(metadata_payload, indent=2), encoding="utf-8")
        manifest_outputs.append(str(metadata_path.relative_to(REPO_ROOT)))
        results_summary["scenarios"]["HYP-002"] = {
            "available": scenarios,
            "skipped": skipped,
            "coefficients": table_paths["Coefficient CSV"],
            "secondary": table_paths["Secondary CSV"],
        }

    results_summary["outputs"] = manifest_outputs
    print(json.dumps(results_summary, indent=2))


if __name__ == "__main__":
    main()
