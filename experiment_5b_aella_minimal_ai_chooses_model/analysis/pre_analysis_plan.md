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
- Binary or ordinal predictors will be harmonized into interpretable scales (e.g., scaled 0–1). Outcomes will follow their native scale (Likert or ordinal), modeled using linear probability / OLS with robust SEs while SRS holds.
- Each hypothesis will estimate average differences between exposure categories controlling for age, gender markers, and socioeconomic childhood baseline.
- Missing data will be handled using listwise deletion initially; multiple imputation is noted for sensitivity analysis once variable missingness is profiled.

## Multiplicity
- Confirmatory families align with the four thematic buckets above. If any family exceeds one confirmatory test, Benjamini-Hochberg FDR control at q ≤ 0.05 will apply.

## Reproducibility & Logging
- All analysis commands will be scripted (preferably via notebooks or `.py` modules) with seeds logged in `analysis/decision_log.csv`.
- Generated public tables will live in `tables/` with mandatory n<10 suppression.

## Outstanding Items Before Freezing
1. Acquire codebook/survey design metadata.
2. Inspect variable distributions, recode schemes, and missingness.
3. Decide whether weighting or raking is defensible; document rationale.
4. Finalize model specifications (link functions, covariate sets) prior to confirmatory tagging.
