# PAP Draft
Generated: 2025-11-03T21:05:45Z | Seed: 20251016
Status: Draft (not frozen) | Regen: `python analysis/code/bootstrap_setup.py --artifact analysis/pre_analysis_plan.md`

Data inputs:
- Raw: `data/raw/childhoodbalancedpublic_original.csv`
- Clean (derived): `data/clean/childhoodbalancedpublic_with_csa_indicator.csv` via `python analysis/code/derive_csa_indicator.py --dataset data/raw/childhoodbalancedpublic_original.csv --out-dataset data/clean/childhoodbalancedpublic_with_csa_indicator.csv --out-distribution tables/csa_indicator_distribution.csv --config config/agent_config.yaml --codebook-in docs/codebook.json --codebook-out docs/codebook.json`

Portfolio: HYP-001 (High), HYP-002 (Medium), HYP-003 (High), HYP-004 (Medium)

## HYP-001 — Childhood class and adult self-love
- **Outcome**: `I love myself (2l8994l)` (Likert −3 to +3)  
  **Predictor**: `classchild` (0–6 ordinal)  
  **Covariates**: `selfage`, `gendermale`, `cis`
- **Estimand**: Average change in outcome per one-step increase in childhood class (design-based OLS with HC3).
- **Primary model**: `survey`-adjusted linear regression under SRS assumption (weights=1). Robust HC3 standard errors with seed 20251016.
- **Robustness checks**:  
  1. Treat `classchild` as categorical with Helmert contrasts (tests functional form).  
  2. Fit proportional-odds ordinal logit on the outcome; assess Brant test to flag violations.  
  3. Standardise outcome to z-score and refit OLS to confirm scale invariance.
- **Missing-data plan**: If any covariate missingness >5%, execute multiple imputation (m=5, deterministic seed 20251016) before confirmatory analysis; otherwise listwise deletion.

## HYP-003 — CSA exposure and anxiety agreement
- **Outcome**: `I tend to suffer from anxiety (npvfh98)-neg`
- **Predictor**: `CSA_score_indicator` (derived binary; 1 if CSA_score>0)
- **Covariates**: `selfage`, `gendermale`, `classchild`
- **Estimand**: Difference in mean anxiety agreement between any CSA exposure vs none.
- **Primary model**: OLS with HC3 under SRS, plus design-based two-sample comparison (Welch t using survey variance) to confirm direction/scale.
- **Robustness checks**:  
  1. Logistic regression on `CSA_score_indicator` predicting high anxiety (>=1) to examine non-linear probability scale.  
  2. Replace binary predictor with ordinal bins `{0, 1-3, 4+}` and test linear trend.  
  3. Exclude extreme tail (`CSA_score` > 15) to assess leverage sensitivity.
- **Missing-data plan**: Monitor derived indicator (currently 0% missing). If downstream models require additional variables with >5% missingness, extend MI plan above; record seeds.

Roadmap: 1) Finalize survey design assumptions and document SRS rationale. 2) Label exploratory descriptives (clearly marked). 3) Update PAP with model equations + estimators, freeze, and tag git. 4) Execute confirmatory models, log seeds to `analysis/results.csv`, and mirror updates in `papers/main/MANIFEST.md`.

Manuscript parity: update `reports/findings_v0.1.md` and `papers/main/manuscript.tex` in lockstep; record regeneration commands alongside outputs.
