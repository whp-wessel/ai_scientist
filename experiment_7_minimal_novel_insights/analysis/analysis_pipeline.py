#!/usr/bin/env python3
"""Analysis pipeline for the purity culture data."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable, List, Tuple

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import statsmodels.api as sm

np.random.seed(12345)

ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "childhoodbalancedpublic_original.csv"
OUTPUT_DIR = ROOT / "outputs"
TABLES_DIR = ROOT / "tables"
FIGURES_DIR = ROOT / "figures"

REQUIRED_COLUMNS = [
    "selfage",
    "Which category fits you best? (4790ydl)",
    "cis",
    "during ages *0-12*:  taught a purity culture that encouraged abstinance/waiting until marriage (wgbq7hv)",
    "during ages *13-18*:  taught a purity culture that encouraged abstinance/waiting until marriage (wxgm38d)",
    "during ages *13-18*: Your parents gave useful guidance (dcrx5ab)",
    "during ages *13-18*:  family/culture had hilarious joking, goofing around, pranks, tomfoolery (i1g8u4j)",
    "I love myself (2l8994l)",
    "I am satisfied with my romantic relationships (hp9qz6f)",
    "I tend to suffer from anxiety (npvfh98)-neg",
    "education",
    "classcurrent",
    "networth",
    "classchild",
    "classteen",
    "Do you *currently* actively practice a religion? (902tbll)",
    "In your childhood, how important was adherence to the religion? For example: tithing, praying, attending church, having a righteous heart, etc. (xvlgpp5)",
    "externalreligion",
    "during ages *0-12*:  Parents divorcing/separating (jib24si)",
    "during ages *13-18*:  Parents divorcing/separating (o47i7yr)",
    "during ages *0-12*: your parents verbally or emotionally abused you (mds78zu)",
    "during ages *13-18*: your parents verbally or emotionally abused you (v1k988q)",
    "during ages *0-12*:  you were depressed (dfqbzi5)",
    "during ages *13-18*:  you were depressed (n4jefor)",
    "during ages *0-12*:  you struggled with learning in school in the ways people tried to teach you (64toj15)",
    "during ages *13-18*:  you struggled with learning in school in the ways people tried to teach you (wlavhx2)",
]

RELIGION_PRACTICE_MAP = {
    "No": 0,
    "Yes, slightly": 1,
    "Yes, moderately": 2,
    "Yes, very seriously": 3,
}

RELIGION_IMPORTANCE_MAP = {
    "Not at all important": 0,
    "Slightly important": 1,
    "Moderately important": 2,
    "Very important": 3,
    "Absolutely essentially important": 4,
}

GENDER_CATEGORIES = [
    "Woman (cis)",
    "Man (cis)",
    "Woman (trans)",
    "Man (trans)",
    "Nonbinary/other (assigned female at birth)",
    "Nonbinary/other (assigned male at birth)",
]

GENDER_MINORITY_CATEGORIES = {
    "Woman (trans)",
    "Man (trans)",
    "Nonbinary/other (assigned female at birth)",
    "Nonbinary/other (assigned male at birth)",
}

CENTER_COLUMNS = [
    "selfage",
    "education",
    "classcurrent",
    "networth",
    "classchild",
    "classteen",
    "externalreligion",
    "religion_practice_num",
    "religion_importance_num",
    "divorce_0_12",
    "divorce_13_18",
    "abuse_0_12",
    "abuse_13_18",
    "depressed_0_12",
    "depressed_13_18",
    "learning_0_12",
    "learning_13_18",
]

HYP2_TERMS = ["purity13_z", "purity0_z", "gender_minority", "purity13_x_gender_minority", "purity0_x_gender_minority"]


def ensure_dirs() -> None:
    for path in (OUTPUT_DIR, TABLES_DIR, FIGURES_DIR):
        path.mkdir(parents=True, exist_ok=True)


def standardize(series: pd.Series) -> pd.Series:
    return (series - series.mean()) / series.std(ddof=0)


def center(series: pd.Series) -> pd.Series:
    return series - series.mean()


def compute_parent_support(df: pd.DataFrame) -> pd.Series:
    return df[["guidance_13_18", "family_humor_13_18"]].mean(axis=1)


def relabel_columns(df: pd.DataFrame) -> pd.DataFrame:
    rename_map = {
        "during ages *0-12*:  taught a purity culture that encouraged abstinance/waiting until marriage (wgbq7hv)": "purity_0_12",
        "during ages *13-18*:  taught a purity culture that encouraged abstinance/waiting until marriage (wxgm38d)": "purity_13_18",
        "during ages *13-18*: Your parents gave useful guidance (dcrx5ab)": "guidance_13_18",
        "during ages *13-18*:  family/culture had hilarious joking, goofing around, pranks, tomfoolery (i1g8u4j)": "family_humor_13_18",
        "I love myself (2l8994l)": "self_love",
        "I am satisfied with my romantic relationships (hp9qz6f)": "romantic_satisfaction",
        "I tend to suffer from anxiety (npvfh98)-neg": "anxiety",
        "Do you *currently* actively practice a religion? (902tbll)": "religion_practice",
        "In your childhood, how important was adherence to the religion? For example: tithing, praying, attending church, having a righteous heart, etc. (xvlgpp5)": "religion_importance",
        "during ages *0-12*:  Parents divorcing/separating (jib24si)": "divorce_0_12",
        "during ages *13-18*:  Parents divorcing/separating (o47i7yr)": "divorce_13_18",
        "during ages *0-12*: your parents verbally or emotionally abused you (mds78zu)": "abuse_0_12",
        "during ages *13-18*: your parents verbally or emotionally abused you (v1k988q)": "abuse_13_18",
        "during ages *0-12*:  you were depressed (dfqbzi5)": "depressed_0_12",
        "during ages *13-18*:  you were depressed (n4jefor)": "depressed_13_18",
        "during ages *0-12*:  you struggled with learning in school in the ways people tried to teach you (64toj15)": "learning_0_12",
        "during ages *13-18*:  you struggled with learning in school in the ways people tried to teach you (wlavhx2)": "learning_13_18",
    }
    return df.rename(columns=rename_map)


def load_data() -> pd.DataFrame:
    df = pd.read_csv(DATA_PATH, usecols=REQUIRED_COLUMNS)
    df = relabel_columns(df)
    df = df.rename(columns={
        "Which category fits you best? (4790ydl)": "gender_category",
        "cis": "cis_indicator",
    })
    return df


def prepare_analytic_sample() -> pd.DataFrame:
    df = load_data()
    df["religion_practice_num"] = df["religion_practice"].map(RELIGION_PRACTICE_MAP)
    df["religion_importance_num"] = df["religion_importance"].map(RELIGION_IMPORTANCE_MAP)
    df["parent_support"] = compute_parent_support(df)
    df["gender_category"] = pd.Categorical(df["gender_category"], categories=GENDER_CATEGORIES)
    df["gender_minority"] = df["gender_category"].isin(GENDER_MINORITY_CATEGORIES).astype(int)
    df = pd.concat(
        [
            df,
            pd.get_dummies(
                df["gender_category"],
                prefix="gender_cat",
                drop_first=True,
                dtype=float,
            ),
        ],
        axis=1,
    )

    required_cols = [
        "purity_0_12",
        "purity_13_18",
        "parent_support",
        "self_love",
        "romantic_satisfaction",
        "anxiety",
        *CENTER_COLUMNS,
        "gender_category",
    ]
    df = df.dropna(subset=required_cols)

    df["purity0_z"] = standardize(df["purity_0_12"])
    df["purity13_z"] = standardize(df["purity_13_18"])
    df["parent_support_z"] = standardize(df["parent_support"])
    df["guidance_z"] = standardize(df["guidance_13_18"])
    df["family_humor_z"] = standardize(df["family_humor_13_18"])
    df["purity13_support"] = df["purity13_z"] * df["parent_support_z"]
    df["purity13_guidance"] = df["purity13_z"] * df["guidance_z"]
    df["purity13_humor"] = df["purity13_z"] * df["family_humor_z"]
    df["purity13_x_gender_minority"] = df["purity13_z"] * df["gender_minority"]
    df["purity0_x_gender_minority"] = df["purity0_z"] * df["gender_minority"]

    for col in CENTER_COLUMNS:
        df[f"{col}_c"] = center(df[col])

    df["gender_minority"] = df["gender_minority"].astype(int)

    return df


def describe_sample(df: pd.DataFrame) -> dict:
    summary = {
        "analytic_n": int(df.shape[0]),
        "gender_minority_n": int(df["gender_minority"].sum()),
        "gender_minority_pct": float(df["gender_minority"].mean()) * 100,
    }
    for col in ["self_love", "romantic_satisfaction", "anxiety", "purity0_z", "purity13_z", "parent_support_z"]:
        summary[f"{col}_mean"] = float(df[col].mean())
        summary[f"{col}_sd"] = float(df[col].std(ddof=1))
    guidance = df["guidance_13_18"]
    humor = df["family_humor_13_18"]
    corr = guidance.corr(humor)
    summary["parent_support_reliability"] = float((2 * corr) / (1 + corr)) if np.isfinite(corr) else None
    return summary


def run_ols(y: str, X: Iterable[str], df: pd.DataFrame) -> sm.regression.linear_model.RegressionResultsWrapper:
    X_mat = df[list(X)]
    model = sm.OLS(df[y], sm.add_constant(X_mat))
    return model.fit(cov_type="HC3")


def summarize_model(
    result: sm.regression.linear_model.RegressionResultsWrapper,
    outcome: str,
    model_label: str,
    terms: List[str],
    df: pd.DataFrame,
) -> List[dict]:
    states = []
    outcome_sd = float(df[outcome].std(ddof=1))
    for term in terms:
        if term not in result.params:
            continue
        coef = float(result.params[term])
        stderr = float(result.bse[term])
        ci = result.conf_int().loc[term].tolist()
        states.append(
            {
                "model": model_label,
                "outcome": outcome,
                "term": term,
                "coef": coef,
                "stderr": stderr,
                "t": float(result.tvalues[term]),
                "p": float(result.pvalues[term]),
                "ci_lower": float(ci[0]),
                "ci_upper": float(ci[1]),
                "cohens_d": coef / outcome_sd if outcome_sd != 0 else None,
                "nobs": int(result.nobs),
                "r2": float(result.rsquared),
            }
        )
    return states


def hyp1_model_configs(df: pd.DataFrame) -> List[Tuple[str, List[str], List[str]]]:
    covariates = [f"{col}_c" for col in CENTER_COLUMNS]
    gender_dummies = [col for col in df.columns if col.startswith("gender_cat_")]
    base_features = ["purity0_z", *covariates, *gender_dummies]
    return [
        (
            "Hyp1_parent_support",
            ["purity13_z", "parent_support_z", "purity13_support", *base_features],
            ["purity13_z", "parent_support_z", "purity13_support", "purity0_z"],
        ),
        (
            "Hyp1_guidance",
            ["purity13_z", "guidance_z", "purity13_guidance", *base_features],
            ["purity13_z", "guidance_z", "purity13_guidance", "purity0_z"],
        ),
        (
            "Hyp1_humor",
            ["purity13_z", "family_humor_z", "purity13_humor", *base_features],
            ["purity13_z", "family_humor_z", "purity13_humor", "purity0_z"],
        ),
    ]


def hyp2_base_features(df: pd.DataFrame) -> List[str]:
    covariates = [f"{col}_c" for col in CENTER_COLUMNS]
    gender_dummies = [col for col in df.columns if col.startswith("gender_cat_")]
    return ["purity13_z", "purity0_z", "gender_minority", *covariates, *gender_dummies]


def run_hypothesis_models(df: pd.DataFrame) -> List[dict]:
    results_summary: List[dict] = []
    h1_configs = hyp1_model_configs(df)
    for outcome in ["self_love", "romantic_satisfaction", "anxiety"]:
        for label, features, terms in h1_configs:
            result = run_ols(outcome, features, df)
            results_summary.extend(summarize_model(result, outcome, label, terms, df))
            if label == "Hyp1_parent_support" and outcome == "self_love":
                plot_parent_support_margins(df, result, features)

    features_h2_base = hyp2_base_features(df)
    for outcome in ["self_love", "romantic_satisfaction", "anxiety"]:
        # purity13 × gender_minority
        features = [*features_h2_base, "purity13_x_gender_minority"]
        result13 = run_ols(outcome, features, df)
        results_summary.extend(
            summarize_model(result13, outcome, "Hyp2_gender_purity13", HYP2_TERMS, df)
        )
        # purity0 × gender_minority
        features = [*features_h2_base, "purity0_x_gender_minority"]
        result0 = run_ols(outcome, features, df)
        results_summary.extend(
            summarize_model(result0, outcome, "Hyp2_gender_purity0", HYP2_TERMS, df)
        )
    return results_summary


def plot_parent_support_margins(df: pd.DataFrame, model: sm.regression.linear_model.RegressionResultsWrapper, features: List[str]) -> None:
    support_seq = np.linspace(df["parent_support_z"].quantile(0.05), df["parent_support_z"].quantile(0.95), 100)
    purity_levels = {"Low purity" : -1.0, "High purity": 1.0}
    covariate_defaults = {f"{col}_c": 0.0 for col in CENTER_COLUMNS}
    gender_dummies = [col for col in df.columns if col.startswith("gender_cat_")]
    for name in gender_dummies:
        covariate_defaults[name] = 0.0
    fig, ax = plt.subplots(figsize=(6, 4))
    for label, purity_value in purity_levels.items():
        data = pd.DataFrame({
            "purity13_z": purity_value,
            "parent_support_z": support_seq,
            "purity13_support": purity_value * support_seq,
            "purity0_z": 0.0,
            **covariate_defaults,
        })
        X = sm.add_constant(data[features], has_constant="add")
        preds = model.get_prediction(X)
        pred_frame = preds.summary_frame(alpha=0.05)
        ax.plot(support_seq, pred_frame["mean"], label=label)
        ax.fill_between(support_seq, pred_frame["mean_ci_lower"], pred_frame["mean_ci_upper"], alpha=0.2)
    ax.set_xlabel("Parental support (z)")
    ax.set_ylabel("Predicted self-love")
    ax.set_title("Parental support buffers high-purity adolescence")
    ax.legend(title="Purity 13-18")
    fig.tight_layout()
    fig.savefig(FIGURES_DIR / "marginal_self_love.png", dpi=300)
    plt.close(fig)


def save_summary(summary: dict) -> None:
    with open(OUTPUT_DIR / "sample_summary.json", "w", encoding="utf-8") as fh:
        json.dump(summary, fh, indent=2)


def save_results_table(results: List[dict]) -> None:
    df = pd.DataFrame(results)
    df.to_csv(TABLES_DIR / "regression_results.csv", index=False)


def main() -> None:
    ensure_dirs()
    df = prepare_analytic_sample()
    sample_desc = describe_sample(df)
    save_summary(sample_desc)
    results = run_hypothesis_models(df)
    save_results_table(results)
    print("Analysis pipeline complete. Results saved to tables and figures.")


if __name__ == "__main__":
    main()
