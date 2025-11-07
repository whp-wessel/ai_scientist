#!/usr/bin/env python3
"""
Run frozen PAP robustness checks for HYP-001 and HYP-003.

Outputs
-------
- QC notes: `qc/<hypothesis>_<check>.md`
- Summary tables: `tables/robustness/robustness_checks_summary.{csv,json}`

All procedures are deterministic and log the global seed from `config/agent_config.yaml`.
"""

from __future__ import annotations

import argparse
import logging
from pathlib import Path
from typing import Callable, Dict, Iterable, List

import numpy as np
import pandas as pd
import statsmodels.api as sm
import statsmodels.formula.api as smf
from statsmodels.miscmodels.ordinal_model import OrderedModel
import yaml


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Execute pre-registered robustness checks for confirmatory hypotheses."
    )
    parser.add_argument(
        "--dataset",
        default="data/clean/childhoodbalancedpublic_with_csa_indicator.csv",
        help="Clean analysis dataset with derived variables.",
    )
    parser.add_argument(
        "--config",
        default="config/agent_config.yaml",
        help="YAML with global seed and settings.",
    )
    parser.add_argument("--qc-dir", default="qc", help="Directory for Markdown QC notes.")
    parser.add_argument(
        "--tables-dir",
        default="tables/robustness",
        help="Directory for machine-readable robustness outputs.",
    )
    parser.add_argument(
        "--hypotheses",
        nargs="+",
        default=["HYP-001", "HYP-003"],
        choices=["HYP-001", "HYP-003"],
        help="Confirmatory hypotheses to evaluate.",
    )
    parser.add_argument(
        "--checks",
        nargs="+",
        default=None,
        help="Optional subset of checks (slugs) to run.",
    )
    parser.add_argument("--log-level", default="INFO", help="Logging verbosity.")
    return parser.parse_args()


def load_config(path: Path) -> Dict:
    with path.open("r", encoding="utf-8") as fh:
        return yaml.safe_load(fh) or {}


def configure_logging(level: str) -> None:
    logging.basicConfig(
        level=getattr(logging, level.upper(), logging.INFO),
        format="%(asctime)sZ [%(levelname)s] %(message)s",
    )


def ensure_dirs(paths: Iterable[Path]) -> None:
    for path in paths:
        path.mkdir(parents=True, exist_ok=True)


def dataset_for_checks(path: Path, hypotheses: List[str]) -> pd.DataFrame:
    df = pd.read_csv(path)
    required = {
        'I love myself (2l8994l)',
        "classchild",
        "selfage",
        "gendermale",
        "cis",
        'I tend to suffer from anxiety (npvfh98)-neg',
        "CSA_score_indicator",
        "CSA_score",
    }
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Dataset missing columns: {missing}")

    cols = set()
    if "HYP-001" in hypotheses:
        cols.update(['I love myself (2l8994l)', "classchild", "selfage", "gendermale", "cis"])
    if "HYP-003" in hypotheses:
        cols.update(
            [
                'I tend to suffer from anxiety (npvfh98)-neg',
                "CSA_score_indicator",
                "selfage",
                "gendermale",
                "classchild",
                "CSA_score",
            ]
        )
    return df.dropna(subset=list(cols))


def write_markdown(path: Path, title: str, stats: Dict[str, float]) -> None:
    lines = [f"# {title}", ""]
    for key, value in stats.items():
        lines.append(f"- **{key}**: {value}")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


# --- Robustness check implementations ---------------------------------------------------------

def hyp001_helmert(df: pd.DataFrame) -> Dict[str, float]:
    model = smf.ols(
        'Q("I love myself (2l8994l)") ~ C(classchild, Helmert) + selfage + gendermale + cis',
        data=df,
    ).fit(cov_type="HC3")
    return {
        "model": "ols_hc3_helmert",
        "n": float(model.nobs),
        "f_stat": float(model.fvalue) if model.fvalue is not None else np.nan,
        "pvalue_overall": float(model.f_pvalue) if model.f_pvalue is not None else np.nan,
        "beta_classchild_mean": float(model.params.filter(like="C(classchild").mean()),
    }


def hyp001_ordinal(df: pd.DataFrame) -> Dict[str, float]:
    outcome = df['I love myself (2l8994l)'].astype(int)
    model = OrderedModel(
        outcome,
        df[["classchild", "selfage", "gendermale", "cis"]],
        distr="logit",
    ).fit(method="bfgs", disp=False)
    coef = model.params.filter(like="classchild").iloc[0]
    return {
        "model": "ordinal_logit",
        "n": float(model.nobs),
        "beta_classchild": float(coef),
        "pvalue_classchild": float(model.pvalues.filter(like="classchild").iloc[0]),
    }


def hyp001_zscore(df: pd.DataFrame) -> Dict[str, float]:
    outcome = df['I love myself (2l8994l)']
    z = (outcome - outcome.mean()) / outcome.std(ddof=0)
    model = smf.ols("z ~ classchild + selfage + gendermale + cis", data=df.assign(z=z)).fit(
        cov_type="HC3"
    )
    return {
        "model": "ols_hc3_zscore",
        "n": float(model.nobs),
        "beta_classchild": float(model.params["classchild"]),
        "se_classchild": float(model.bse["classchild"]),
        "pvalue_classchild": float(model.pvalues["classchild"]),
    }


def hyp003_logit(df: pd.DataFrame) -> Dict[str, float]:
    outcome = (df['I tend to suffer from anxiety (npvfh98)-neg'] >= 1).astype(int)
    model = sm.Logit(
        outcome,
        sm.add_constant(df[["CSA_score_indicator", "selfage", "gendermale", "classchild"]]),
    ).fit(disp=False)
    coef = model.params["CSA_score_indicator"]
    return {
        "model": "logit_high_anxiety",
        "n": float(model.nobs),
        "coef_csa_indicator": float(coef),
        "se_csa_indicator": float(model.bse["CSA_score_indicator"]),
        "odds_ratio": float(np.exp(coef)),
        "pvalue_csa_indicator": float(model.pvalues["CSA_score_indicator"]),
    }


def hyp003_bins(df: pd.DataFrame) -> Dict[str, float]:
    bins = pd.cut(
        df["CSA_score"],
        bins=[-np.inf, 0, 3, np.inf],
        labels=[0, 1, 2],
        right=True,
    ).astype(int)
    model = smf.ols(
        'Q("I tend to suffer from anxiety (npvfh98)-neg") ~ bins + selfage + gendermale + classchild',
        data=df.assign(bins=bins),
    ).fit(cov_type="HC3")
    return {
        "model": "ols_hc3_csa_bins",
        "n": float(model.nobs),
        "beta_bins": float(model.params["bins"]),
        "pvalue_bins": float(model.pvalues["bins"]),
    }


def hyp003_trim(df: pd.DataFrame) -> Dict[str, float]:
    trimmed = df[df["CSA_score"] <= 15].copy()
    model = smf.ols(
        'Q("I tend to suffer from anxiety (npvfh98)-neg") ~ CSA_score_indicator + selfage + gendermale + classchild',
        data=trimmed,
    ).fit(cov_type="HC3")
    return {
        "model": "ols_hc3_trimmed",
        "n": float(model.nobs),
        "beta_csa_indicator": float(model.params["CSA_score_indicator"]),
        "se_csa_indicator": float(model.bse["CSA_score_indicator"]),
        "pvalue_csa_indicator": float(model.pvalues["CSA_score_indicator"]),
    }


CHECKS: Dict[str, Dict[str, Callable[[pd.DataFrame], Dict[str, float]]]] = {
    "HYP-001": {
        "helmert": hyp001_helmert,
        "ordinal_logit": hyp001_ordinal,
        "zscore": hyp001_zscore,
    },
    "HYP-003": {
        "logit_high_anxiety": hyp003_logit,
        "ordinal_bins": hyp003_bins,
        "tail_trim": hyp003_trim,
    },
}


def main() -> None:
    args = parse_args()
    configure_logging(args.log_level)

    cfg = load_config(Path(args.config))
    seed = int(cfg.get("seed", 0))
    logging.info("Running robustness checks with seed=%s", seed)
    np.random.seed(seed)

    qc_dir = Path(args.qc_dir)
    tables_dir = Path(args.tables_dir)
    ensure_dirs([qc_dir, tables_dir])

    hypotheses = args.hypotheses
    requested_checks = set(args.checks or [])
    df = dataset_for_checks(Path(args.dataset), hypotheses)
    rows: List[Dict[str, float]] = []

    for hypothesis in hypotheses:
        for slug, func in CHECKS[hypothesis].items():
            if requested_checks and slug not in requested_checks:
                continue
            logging.info("Executing %s / %s", hypothesis, slug)
            stats = func(df.copy())
            stats.update(hypothesis_id=hypothesis, check=slug, seed=seed)
            rows.append(stats)
            write_markdown(
                qc_dir / f"{hypothesis.lower()}_{slug}.md",
                f"{hypothesis} robustness — {slug}",
                stats,
            )

    if rows:
        frame = pd.DataFrame(rows)
        csv_path = tables_dir / "robustness_checks_summary.csv"
        json_path = tables_dir / "robustness_checks_summary.json"
        frame.to_csv(csv_path, index=False)
        json_path.write_text(frame.to_json(orient="records", indent=2), encoding="utf-8")
        logging.info("Wrote robustness summaries to %s and %s", csv_path, json_path)
    else:
        logging.warning("No robustness checks executed.")


if __name__ == "__main__":
    main()
