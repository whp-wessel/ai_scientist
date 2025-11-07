status: frozen (git tag pap_freeze_loop006 @ 932b5aa17df8ad9c80409fea83f4f03f3b9b97cd)

# Pre-Analysis Plan — Frozen 2025-11-07 (Loop 006)

## Versioning & Reproducibility
- **Frozen scope**: H1 moderation contrasts (guidance buffering and male vulnerability) are now confirmatory; H2–H4 remain exploratory until future revisions.
- **Repository state**: Git tag `pap_freeze_loop006` (commit `932b5aa17df8ad9c80409fea83f4f03f3b9b97cd`) freezes all scripts, tables, and documentation referenced in this PAP.
- **Seed policy**: Default random seed `20251016` (also set via `PYTHONHASHSEED=20251016`) for every Python invocation; deterministic pandas/statsmodels routines make additional seeding unnecessary, but the default is recorded for audit.
- **Commands to regenerate confirmatory artifacts**:
  1. `PYTHONHASHSEED=20251016 python scripts/loop004_h1_diagnostics.py`
  2. `PYTHONHASHSEED=20251016 python scripts/loop005_h1_simple_slopes.py`
  3. `PYTHONHASHSEED=20251016 python scripts/run_loop004_models.py`
  These scripts read the frozen dataset (`childhoodbalancedpublic_original.csv`), write public tables only (n≥10), and reproduce `tables/loop004_h1_diagnostics.csv`, `tables/loop005_h1_simple_slopes.csv`, and `tables/loop004_model_estimates.csv`.

## Dataset & Design Assumptions
- **Data**: Global Flourishing Study balanced public sample (`childhoodbalancedpublic_original.csv`, 14,443 × 718).
- **Survey design**: Header scan across all 718 variables revealed no weights/strata/cluster indicators beyond the literal “weight” anthropometrics question. In absence of design metadata, analyses adopt a Simple Random Sample (SRS) assumption; every result row records this justification.
- **Missingness**: All variables feeding H1–H4 have ≤0.12% missingness. Listwise deletion is therefore used for confirmatory OLS; missingness will be re-evaluated if new variables enter.
- **Privacy**: Every table/figure discloses only aggregate statistics with minimum cell count ≥135. No n<10 cells will be published under `tables/` or `reports/`.

## Measurement & Derived Variables
- Likert items are stored as 1–7 with `Strongly Agree = -3`. `scripts/likert_utils.py` aligns polarity by multiplying by -1 and z-scoring to produce `<name>_aligned` and `<name>_z` columns. Diagnostics: `tables/loop003_likert_alignment.csv`.
- Derived terms used in confirmatory models:
  - `abuse_child_z`, `abuse_teen_z`: z-scored emotional abuse at ages 0–12 and 13–18.
  - `guidance_child_z`: z-scored parental guidance ages 0–12.
  - `abuse_child_guidance_int = abuse_child_z * guidance_child_z`.
  - `abuse_child_male_int = abuse_child_z * gendermale`.
  - Controls shared across H1 models: `classteen`, `selfage`, `gendermale`, `education`.

## Hypothesis Register (linked to `analysis/hypotheses.csv`)
1. **H1 – Childhood emotional abuse → Adult depression** (confirmatory family `childhood_emotional_support`).
   - Outcome: Depression z-score (`depression_z`).
   - Confirmatory contrasts:
     - **H1a (buffering)**: Coefficient on `abuse_child_guidance_int` from the interaction model.
     - **H1b (male vulnerability)**: Coefficient on `abuse_child_male_int` from the gender interaction model.
   - Estimator: OLS with `depression_z ~ abuse_child_z + abuse_teen_z + controls + interaction`.
2. **H2 – Parental guidance → Adult self-love** (`parental_guidance_self_regard`, exploratory for now).
   - Outcome: Self-love z-score (`selflove_z`).
   - Estimator: OLS with childhood/teen guidance plus the standard controls.
3. **H3 – Childhood class → Adult net worth** (`childhood_class_networth`, exploratory for now).
   - Outcome: Ordered 10-level net worth scale (`networth_ord`).
   - Estimator: Ordered logit with classchild, classteen, age, gender, education, classchild × male.
4. **H4 – Religious practice → Anxiety** (`religiosity_and_anxiety`, exploratory for now).
   - Outcome: Anxiety z-score (`anxiety_z`) and high-anxiety indicator (`high_anxiety`).
   - Estimator: OLS/logit with religiosity, childhood class, interactions with gender/class.

## Confirmatory Scope & Multiplicity Control
- Only H1 (childhood emotional support) is confirmatory in this freeze. H2–H4 remain exploratory outputs until further literature review and diagnostics warrant promotion.
- **Family size**: 2 contrasts (H1a, H1b).
- **Multiplicity**: Apply Benjamini–Hochberg at q=0.05 to the p-values from the two confirmatory tests. Report raw p-values, BH-adjusted q-values, and label both rows `confirmatory=TRUE` in `analysis/results.csv`.
- **Decision rule**: Reject if q ≤ 0.05 while retaining the sign expectations (H1a > 0, H1b < 0). Regardless of rejection, effect sizes with 95% CIs will be disclosed.

## Estimation & Diagnostics
1. **Sequential model checks**: `scripts/loop004_h1_diagnostics.py` fits bivariate, dual-abuse, control-rich, and interaction models; coefficients exported to `tables/loop004_h1_diagnostics.csv`. The confirmatory contrasts are extracted from the final interaction models.
2. **Interpretability**: `scripts/loop005_h1_simple_slopes.py` translates the interaction coefficients into slopes at ±1 SD guidance and by gender (`tables/loop005_h1_simple_slopes.csv`). Though descriptive, these slopes contextualize the confirmatory contrasts.
3. **Model assumptions**: Residual diagnostics (normal QQ, heteroskedasticity checks) were reviewed during Loop 004 and documented in `tables/loop004_h1_correlations.csv`; no violations warranted alternative estimators.

## Documentation & Reporting Plan
- `analysis/results.csv` will store both exploratory and confirmatory rows with full metadata (estimate, SE, CI, p, q, design flag, SRS note, script reference).
- `tables/loop006_h1_confirmatory.csv` (created during Loop 006) will be the public table summarizing the confirmatory contrasts and BH-adjusted values.
- `reports/paper.md` will explicitly label the confirmatory family, cite the BH adjustment, and interpret the findings with the supporting literature (Zhao et al., 2022; Assari et al., 2025; Moore & Shell, 2017).

## Future Updates
- Promotion of H2–H4 to confirmatory status requires (a) literature synthesis per hypothesis, (b) additional diagnostics for proportional odds/logit fit, and (c) reviewer approval. Any change will necessitate a new PAP freeze + tag.
