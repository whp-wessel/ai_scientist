# Pre-Analysis Plan

**status: draft**

## Project Summary
- **Research focus:** Link specific childhood environments captured in `childhoodbalancedpublic_original.csv` to adult wellbeing, mental health, and socioeconomic positioning.
- **Dataset:** Single cross-sectional survey compiled by Balanced Data. No codebook or design documentation is currently available; see `docs/TODO.md`.
- **Default seed:** `20251016` (record different seeds whenever randomness is introduced).

## Survey Design Assumptions
- No published weights, strata, or clusters accompany the dataset. Until provenance information is recovered, analyses will report simple random sampling (SRS) results and include explicit caveats in the `design_used`/`srs_justification` fields.
- TODO: confirm whether recruitment relied on quota balancing or platform weighting (blocked until codebook is located).

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

### Scale Harmonization (Loop 2)
- Script: `python analysis/scripts/derive_likert_scales.py` reads `childhoodbalancedpublic_original.csv`, creates respondent IDs, and generates centered and standardized variants for each −3..3 Likert item used in H1–H4.
- Output artifact: `analysis/derived/loop002_likert_scales.csv` containing the original items plus `_scaled` (value÷3) and `_z` ((value−μ)/σ) columns for `mds78zu`, `ix5iyv3`, `pqo6jmj`, `z0mhd63`, `4tuoqly`, `dfqbzi5`, and `wz901dj`, alongside the shared covariate set.
- Modeling default: predictors enter as `_scaled` (bounded −1..1 for interpretability). Outcomes also use `_scaled`, keeping coefficients interpretable as the expected change in outcome SDs per full-scale shift in the predictor. `_z` columns remain available for sensitivity checks.

### Data profiling status (Loop 1)
- Script: `python analysis/scripts/profile_key_variables.py` produces `analysis/profiling/loop001_key_vars_summary.csv` and companion value-counts for mds78zu, ix5iyv3, pqo6jmj, z0mhd63, 4tuoqly, classcurrent, dfqbzi5, and wz901dj.
- Each focal variable has ≥14,426 non-missing responses (≤0.12% missing). Likert responses are encoded on −3…+3 scales with roughly symmetric spread, so future models can safely center/rescale to ±1 without loss of information.
- `classcurrent` spans 0–6 with mean ≈3.02 (sd ≈1.26), offering enough variance for socioeconomic outcome modeling.

## Multiplicity
- Confirmatory families align with the four thematic buckets above. If any family exceeds one confirmatory test, Benjamini-Hochberg FDR control at q ≤ 0.05 will apply.

## Reproducibility & Logging
- All analysis commands will be scripted (preferably via notebooks or `.py` modules) with seeds logged in `analysis/decision_log.csv`.
- Generated public tables will live in `tables/` with mandatory n<10 suppression.

## Outstanding Items Before Freezing
1. Acquire codebook/survey design metadata.
2. Inspect remaining variable distributions and missingness for potential covariates beyond the core set.
3. Decide whether weighting or raking is defensible; document rationale.
4. Finalize confirmatory model specifications (link functions, interaction terms) prior to PAP freeze/tagging.
