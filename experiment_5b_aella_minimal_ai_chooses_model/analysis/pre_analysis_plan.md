# Pre-Analysis Plan

**status: frozen (commit 565989e)**

Freeze tag: pap_freeze_loop004 (git tag `pap_freeze_loop004` -> commit `565989e`)

## Project Summary
- **Research focus:** Link specific childhood environments captured in `childhoodbalancedpublic_original.csv` to adult wellbeing, mental health, and socioeconomic positioning.
- **Dataset:** Single cross-sectional survey compiled by Balanced Data. No codebook or design documentation is currently available; see `docs/TODO.md`.
- **Default seed:** `20251016` (record different seeds whenever randomness is introduced).

## Survey Design Assumptions
- No published weights, strata, or clusters accompany the dataset. Until provenance information is recovered, analyses will report simple random sampling (SRS) results and include explicit caveats in the `design_used`/`srs_justification` fields.
- TODO: confirm whether recruitment relied on quota balancing or platform weighting (blocked until codebook is located).
- Loop 5 due diligence: re-checked the Balanced Data public release (see `docs/TODO.md`) and confirmed no weighting/stratification metadata accompanies `childhoodbalancedpublic_original.csv`; therefore SRS remains the only defensible assumption for confirmatory work, with explicit logging in `analysis/hypotheses.csv` and `analysis/results.csv`.

## Research Questions
1. How do adverse childhood experiences relate to adult affect and self-perception?
2. Do positive parental supports during ages 0–12 predict adult satisfaction in work and relationships?
3. Does early digital access correspond to present socioeconomic positioning?
4. Are childhood mental health self-reports echoed in adulthood?

## Hypotheses (see `analysis/hypotheses.csv`)
- **H1 (childhood_adversity):** Higher scores on childhood parental emotional abuse (`mds78zu`) predict lower adult happiness (`ix5iyv3`).
- **H2 (parental_support):** Higher parental guidance ages 0–12 (`pqo6jmj`) predicts higher adult career satisfaction (`z0mhd63`).
- **H3 (digital_exposure):** Regular childhood computer use (`4tuoqly`) is associated with higher current class ranking (`classcurrent`).
- **H4 (mental_health_continuity):** Childhood depression indicators (`dfqbzi5`) are associated with higher adult depression reports (`wz901dj`).

## Planned Estimands & Models
- Binary or ordinal predictors will be harmonized into interpretable scales (see “Scale Harmonization” below). Outcomes will follow their native scale (Likert or ordinal), modeled using OLS with heteroskedasticity-robust (HC3) SEs while the SRS assumption holds.
- Each hypothesis will estimate average differences between exposure categories controlling for the baseline covariate set: respondent age (`selfage`), binary male indicator (`gendermale`), educational attainment (`education`, ordinal 0–6), and socioeconomic ladder placements during childhood (`classchild`), teen years (`classteen`), and adulthood (`classcurrent` when not used as an outcome).
- Missing data will be handled using listwise deletion initially; multiple imputation is noted for sensitivity analysis once variable missingness is profiled.

### Scale Harmonization (Loop 2–3)
- Script: `python analysis/scripts/derive_likert_scales.py` reads `childhoodbalancedpublic_original.csv`, creates respondent IDs, and generates centered and standardized variants for each −3..3 Likert item used in H1–H4.
- Output artifact: `analysis/derived/loop002_likert_scales.csv` containing the original items plus `_scaled` (value÷3) and `_z` ((value−μ)/σ) columns for `mds78zu`, `ix5iyv3`, `pqo6jmj`, `z0mhd63`, `4tuoqly`, `dfqbzi5`, and `wz901dj`, alongside the shared covariate set. For the ordinal socioeconomic outcome `classcurrent` (0–6), we add `classcurrent_scaled` (÷6) and `classcurrent_z`.
- Modeling default: predictors enter as `_scaled` (bounded −1..1 for interpretability). Likert outcomes use `_scaled`; for H3 the outcome is `classcurrent_z` so coefficients read as SD changes in socioeconomic status per unit change in the predictor. `_z` columns remain available for sensitivity checks.

### Data profiling status (Loop 1)
- Script: `python analysis/scripts/profile_key_variables.py` produces `analysis/profiling/loop001_key_vars_summary.csv` and companion value-counts for mds78zu, ix5iyv3, pqo6jmj, z0mhd63, 4tuoqly, classcurrent, dfqbzi5, and wz901dj.
- Each focal variable has ≥14,426 non-missing responses (≤0.12% missing). Likert responses are encoded on −3…+3 scales with roughly symmetric spread, so future models can safely center/rescale to ±1 without loss of information.
- `classcurrent` spans 0–6 with mean ≈3.02 (sd ≈1.26), offering enough variance for socioeconomic outcome modeling.

## Multiplicity
- Confirmatory families align with the four thematic buckets above. If any family exceeds one confirmatory test, Benjamini-Hochberg FDR control at q ≤ 0.05 will apply.

## Confirmatory Families and Primary Estimands (Frozen)
- Family: childhood_adversity (H1 primary)
  - Estimand: Linear association between childhood parental emotional abuse and adult unhappiness, adjusted for pre-specified covariates.
  - Model: OLS with HC3 SEs.
  - Formula: `ix5iyv3_scaled ~ mds78zu_scaled + selfage + gendermale + education + classchild + classteen + classcurrent`.
  - Unit/scale: Coefficient is change in adult unhappiness (−1..1 scale) per unit change in adversity (−1..1 scale).

- Family: parental_support (H2 primary)
  - Estimand: Linear association between parental guidance (ages 0–12) and adult career satisfaction, adjusted as above.
  - Model: OLS with HC3 SEs.
  - Formula: `z0mhd63_scaled ~ pqo6jmj_scaled + selfage + gendermale + education + classchild + classteen + classcurrent`.

- Family: digital_exposure (H3 primary)
  - Estimand: Association between regular childhood computer use and adult socioeconomic status.
  - Primary model: OLS(HC3), treating outcome as standardized continuous for interpretability.
  - Formula (primary): `classcurrent_z ~ 4tuoqly_scaled + selfage + gendermale + education + classchild + classteen`.
  - Sensitivity (pre-specified): Ordered logit with `classcurrent` as 0–6 ordinal outcome and the same covariates; report the coefficient for `4tuoqly_scaled` with standard errors and z-tests.

- Family: mental_health_continuity (H4 primary)
  - Estimand: Association between childhood depression self-report and adult depression, adjusted as above.
  - Model: OLS with HC3 SEs.
  - Formula: `wz901dj_scaled ~ dfqbzi5_scaled + selfage + gendermale + education + classchild + classteen + classcurrent`.

Notes on families: Each family has exactly one primary confirmatory test as specified above. Interaction and nonlinearity checks listed below are pre-specified sensitivity analyses and do not expand the confirmatory family size.

## Interactions and Nonlinearity (Pre-specified Sensitivities)
- Interactions: For each H1–H4 model, estimate an additional specification with `gendermale × (primary predictor)` included. Interpret interaction cautiously; treat as sensitivity (not confirmatory) and do not adjust FDR for these checks.
- Nonlinearity: For H1 and H2, estimate an additional specification adding a quadratic term for the primary predictor (e.g., `mds78zu_scaled^2`, `pqo6jmj_scaled^2`). Report the quadratic term and compare AIC with the linear baseline. Baseline linear model remains the confirmatory specification.

## Deterministic Commands (Reproducibility)
All commands run from the repository root unless stated.
- Data derivation (scales): `python analysis/scripts/derive_likert_scales.py`
- Confirmatory OLS models (primary):
  - H1/H2: `python analysis/scripts/prototype_h1_h2_regressions.py`
  - H3/H4: `python analysis/scripts/prototype_h3_h4_regressions.py`
- H3 sensitivity (ordered logit): `python analysis/scripts/ordered_logit_h3.py`
Outputs are written under `analysis/results/` and summarized in `analysis/results.csv`. Seeds are fixed at `20251016` where applicable (no randomness in these models beyond numerical optimization).

## Diagnostics Plan (Frozen)
- Linearity and functional form: inspect partial residual plots (lowess overlay) for each predictor; consider quadratic terms if strong curvature appears.
- Heteroskedasticity: compute HC3 by default; report White test p-values as a diagnostic only.
- Influence and leverage: flag observations with Cook’s distance > 4/n and re-estimate without them as a sensitivity.
- Multicollinearity: compute VIFs for the covariate stack; if VIF>10, consider dropping or combining variables.
- Model fit: report R²/adj. R² and distribution of residuals. For H3 treat `classcurrent` as ordinal; OLS is the baseline (HC3), with ordered logit as a pre-specified sensitivity.
- Missingness: profile patterns; if any focal variable has >5% missingness, plan multiple imputation (m=20) as a sensitivity.

## Reproducibility & Logging
- All analysis commands will be scripted (preferably via notebooks or `.py` modules) with seeds logged in `analysis/decision_log.csv`.
- Generated public tables will live in `tables/` with mandatory n<10 suppression.

## Post-Freeze Backlog
1. Acquire codebook/survey design metadata (update SRS justification if new information emerges).
2. Inspect remaining variable distributions and missingness for potential covariates beyond the core set (document any justified additions as sensitivity-only).
3. Revisit whether weighting or raking is defensible if design metadata becomes available; otherwise maintain SRS with HC3.
4. Execute confirmatory models and H3’s ordered-logit sensitivity; prepare public tables with n<10 suppression.
