"""Quick scoping and reliability checks for childhoodbalancedpublic_public."""

from __future__ import annotations

from typing import Sequence

import numpy as np
import pandas as pd
from factor_analyzer import FactorAnalyzer


def cronbach_alpha(df: pd.DataFrame) -> tuple[float, int]:
    """Return Cronbach's alpha and number of rows used."""
    df_clean = df.dropna()
    n_items = df_clean.shape[1]
    if n_items <= 1:
        return float("nan"), 0
    total_var = df_clean.sum(axis=1).var(ddof=1)
    if total_var == 0:
        return float("nan"), df_clean.shape[0]
    item_var_sum = df_clean.var(axis=0, ddof=1).sum()
    alpha = n_items / (n_items - 1) * (1 - item_var_sum / total_var)
    return float(alpha), int(df_clean.shape[0])


def omega(df: pd.DataFrame) -> float:
    """Return McDonald's omega from a single-factor solution."""
    df_clean = df.dropna()
    if df_clean.shape[1] <= 1:
        return float("nan")
    fa = FactorAnalyzer(n_factors=1, rotation=None)
    fa.fit(df_clean)
    loadings = fa.loadings_[:, 0]
    uniqueness = fa.get_uniquenesses()
    numerator = float(loadings.sum() ** 2)
    denominator = numerator + float(uniqueness.sum())
    return numerator / denominator if denominator > 0 else float("nan")


def scale_stats(df: pd.DataFrame, columns: Sequence[str]) -> dict:
    """Gather descriptive and reliability stats for a list of columns."""
    sub = df[list(columns)]
    desc = sub.describe().loc[["count", "mean", "std", "min", "max"]].T
    alpha, n_alpha = cronbach_alpha(sub)
    omega_value = omega(sub)
    return {
        "description": desc,
        "alpha": alpha,
        "omega": omega_value,
        "n_complete": n_alpha,
    }


def main() -> None:
    csv_path = "childhoodbalancedpublic_original.csv"
    df = pd.read_csv(csv_path, low_memory=False)

    print("Dataset shape:", df.shape)
    print("Numeric columns:", df.select_dtypes(include=[np.number]).shape[1])
    print("Object columns:", df.select_dtypes(include=["object"]).shape[1])
    print("\nDtype warning arises because some columns mix strings/numbers.")

    missing = df.isna().mean().sort_values(ascending=False)
    print("\nTop columns with all or nearly all missing values:")
    print(missing[missing >= 0.8].head(20).to_string())
    print("\nColumns with 60-80% missing values:")
    print(missing[(missing >= 0.6) & (missing < 0.8)].head(15).to_string())
    print("\nColumns with up to 1% missingness (helpful for baseline covariates):")
    print(missing[(missing > 0) & (missing <= 0.01)].head(10).to_string())

    print("\nAge summary:")
    age_cols = ["Your age? (hcdfzjj)", "selfage"]
    print(df[age_cols].describe().loc[["mean", "std", "min", "max"]].T)

    gender_summary = df[["biomale", "gendermale"]].mean().to_frame("mean")
    print("\nBinary gender proxies (mean ≈ prevalence of 1):")
    print(gender_summary)

    distribution_cols = ["height", "weight"]
    print("\nHeight/weight descriptives:")
    print(df[distribution_cols].describe().loc[["mean", "std", "min", "max"]].T)

    adult_pos_cols = [
        "I love myself (2l8994l)",
        "I am satisfied with my romantic relationships (hp9qz6f)",
        "I am satisfied with my work/career life (or lack thereof) (z0mhd63)",
        "I'm happy with my appearance (39kxhhw)",
        "I tend to be calm/peaceful (6e6zhy3)",
        "I tend to have a lot of energy (gczsvvo)",
        "On average, I am happier as an adult than I was in childhood (h33e6gg)",
        "In general, people in my *current* social circles tend to treat me really well (71mn55g)",
    ]

    loved_cols = [
        "during ages *0-12*: you felt unconditionally loved (xtrwcp7)",
        "during ages *13-18*: you felt unconditionally loved (wa9yb85)",
        "you felt unconditionally loved",
    ]

    print("\nAdult positivity scale stats:")
    adult_stats = scale_stats(df, adult_pos_cols)
    print(adult_stats["description"])
    print(f"Cronbach's alpha: {adult_stats['alpha']:.3f} (n={adult_stats['n_complete']})")
    print(f"McDonald's omega: {adult_stats['omega']:.3f}")

    print("\nFeeling-loved scale stats:")
    loved_stats = scale_stats(df, loved_cols)
    print(loved_stats["description"])
    print(f"Cronbach's alpha: {loved_stats['alpha']:.3f} (n={loved_stats['n_complete']})")
    print(f"McDonald's omega: {loved_stats['omega']:.3f}")


if __name__ == "__main__":
    main()
