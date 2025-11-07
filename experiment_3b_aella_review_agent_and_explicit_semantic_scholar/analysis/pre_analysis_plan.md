status: draft
freeze_commit: TBD
registry_url: TBD
seed: 20251016
last_updated: 2025-11-07T11:12:00Z

# Pre-Analysis Plan (Draft)

This document governs confirmatory analyses for the childhood wellbeing survey. It
remains a **draft** until (a) survey design metadata are verified or explicitly
assumed SRS, (b) the literature gate (>=3 DOI-backed citations) is satisfied, (c)
`qc/measures_validity.md` contains entries for every referenced variable with
reliability evidence, and (d) the PAP is registered + tagged. When frozen, this
header will read `status: frozen (commit <sha>, tag pap-v1)` and all
confirmatory work will cite that commit/tag.

## 1. Data, Design, and Determinism
- **Dataset**: `childhoodbalancedpublic_original.csv` (14,443 x 718). Raw file is
  immutable; cleaning scripts will write to `data/clean/`.
- **Survey design**: Treated as SRS until Task T-001 resolves whether weights,
  strata, or replicate design files exist. Any newly discovered design vars must
  be added to `docs/survey_design.yaml` and reflected in all estimators before a
  PAP freeze.
- **Seed discipline**: Global seed `20251016` (from `config/agent_config.yaml`).
  All randomized operations (e.g., multiple imputation) will explicitly set this
  seed and log it inside the resulting tables/figures manifests.
- **Regeneration command** (draft skeleton):
  ```bash
  python analysis/code/00_run_all.py \
    --seed 20251016 \
    --pap analysis/pre_analysis_plan.md \
    --raw childhoodbalancedpublic_original.csv
  ```
  Scripts referenced above will orchestrate cleaning (`analysis/code/01_prepare_data.py`)
  and estimation (`analysis/code/02_models.py`). Hashes + command strings will be
  recorded in `papers/main/MANIFEST.md` once implemented.
- **LaTeX parity plan**: Every time the Markdown manuscript or PAP changes,
  `papers/main/manuscript.tex` will be regenerated via `latexmk -pdf` and logged in
  `papers/main/build_log.txt`. The PAP references that build log as evidence of parity.

## 2. Priority Hypotheses (Confirmatory Candidates)

### H1 — Wellbeing (Claim C1)
- **Question**: Do respondents from higher childhood socioeconomic classes
  (`classchild`) report being happier as adults relative to childhood (`h33e6gg`)?
- **Estimand**: Difference in weighted mean Likert score between respondents with
  `classchild >= 4` (upper/upper-middle) and `classchild <= 2` (lower/lower-middle).
  Sensitivity: ordinal logit slope treating `classchild` as an ordered predictor.
- **Model**: Survey-weighted linear regression (or SRS OLS with HC2 SEs if weights
  remain unavailable). Include controls `selfage`, `gendermale`, and indicator for
  `networth` >= sample median. Secondary model: proportional-odds regression.
- **Missing data**: If any covariate has >5% missingness, deploy multiple
  imputation by chained equations (m=20, burn-in 10) seeded at 20251016. Record
  pooled estimates and Rubin's rules SEs.
- **Robustness checks**:
  1. Treat `classchild` as z-scored continuous predictor (trend test).
  2. Estimate models separately for `gendermale==1` vs `gendermale==0` and report
     qualitative heterogeneity (no interaction term in primary estimand).

### H2 — Adversity (Claim C2)
- **Question**: Is childhood verbal/emotional abuse (`mds78zu`) associated with
  higher likelihood of reporting adult depression (`wz901dj`)?
- **Estimand**: Difference in probability of selecting Likert levels >=4 between
  exposed vs non-exposed respondents.
- **Model**: Survey-weighted logistic regression on indicator(`wz901dj >= 4`)
  with controls `selfage`, `gendermale`, `classchild`, and `education`.
- **Missing data**: Sensitive trauma items may exceed 10% missingness. If so,
  implement MI (m=20, seed 20251016) with predictive mean matching for Likert
  outcomes. Retain a missingness flag in robustness tables to document MAR
  assumptions.
- **Negative-control outcome**: Repeat the model with `height` (continuous) as
  the outcome—association should be null. Non-null effects will trigger a PAP
  revision before freeze.
- **Secondary robustness**: Replace exposure with adolescent abuse item (if
  present) to ensure age-window consistency.

### H3/H4 — Proposed (Not Yet in PAP)
- H3 (economic): Evaluate whether childhood SES predicts current net worth after
  adjusting for education; candidate for future PAP inclusion once mediation plan
  is articulated.
- H4 (psychosocial): Explore anxiety-happiness coupling to inform composite
  wellbeing indices; remains exploratory until measurement validity completed.

## 3. Measurement Validity & QC Tasks
- Populate `qc/measures_validity.md` with Cronbach's alpha (or test-retest
  metrics) for `h33e6gg`, `npvfh98`, `wz901dj`, `classchild`, `mds78zu`, and
  `networth`. Include DIF checks across `gendermale` for each Likert scale.
- `qc/data_checks.md` will continue to log schema validation, dtype coercions,
  and missingness summaries. Any deviations must be mirrored in the Decision Log.

## 4. Privacy & Disclosure Controls
- Small-cell threshold: 10 respondents. Every public table/figure must log its
  minimum cell count in `qc/disclosure_check_loop_000.md` before circulation.
- Trauma variables (e.g., `mds78zu`) will be reported only in aggregate; hex-binned
  plots preferred over raw scatter to avoid re-identification.

## 5. Literature & Documentation Requirements
- Maintain `lit/evidence_map.csv` with `claim_id` coverage; each claim cited in
  future manuscripts must map to >=1 DOI-backed entry.
- Append Semantic Scholar query metadata under `lit/queries/loop_{loop}/` for
  every search (already satisfied for loop 000).
- Update `lit/bibliography.bib` alongside the evidence map; run `bibtex` during
  manuscript builds and log warnings in `papers/main/build_log.txt`.

## 6. Outstanding Items Blocking Freeze
1. Verify survey design weights/replicates or formally document SRS assumption.
2. Produce at least three DOI-backed literature entries linked to Claim IDs.
3. Complete `qc/measures_validity.md` for all PAP-referenced variables.
4. Implement the scripted regeneration pathway and populate MANIFEST commands.

Confirmatory analyses will **not** begin until the above blockers are removed and
this PAP is marked frozen with a registry URL plus commit SHA/tag reference.
