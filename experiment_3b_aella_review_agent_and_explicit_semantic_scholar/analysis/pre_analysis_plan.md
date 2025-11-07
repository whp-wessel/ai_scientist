status: draft
freeze_commit: TBD
registry_url: TBD
seed: 20251016
last_updated: 2025-11-07T10:59:57Z

# Pre-Analysis Plan (Draft)

This scaffold captures the confirmatory analysis intent for the childhood wellbeing
survey. The plan remains **draft** until: (1) survey design metadata are verified,
(2) measurement validity entries exist for every referenced variable, (3) the
literature gate (≥3 DOI-backed papers) is satisfied, and (4) the PAP is registered
and tagged. Once frozen, this header will read `status: frozen (commit <sha>, tag pap-v1)`,
and all confirmatory work will reference that commit/tag.

## Data & Design Overview
- **Dataset**: `childhoodbalancedpublic_original.csv` (14,443 rows × 718 columns; raw file
  stored at repository root; clean derivatives will live under `data/clean/`).
- **Survey design**: Currently treated as SRS because no weight/strata/cluster variables are
  documented. Task `T-001` tracks verification; if weights exist they must be incorporated
  via `survey` or `srvyr` in R or `statsmodels` survey modules in Python before freezing.
- **Seed discipline**: All random operations (imputation, resampling) will use `20251016`
  and record the seed in outputs and manifests.

## Priority Hypotheses (Confirmatory candidates)

### H1 (wellbeing family; claim C1)
- **Question**: Do respondents from higher childhood socioeconomic classes (`classchild`)
  report greater agreement with being happier as adults than in childhood (`h33e6gg`)?
- **Estimand**: Difference in weighted mean Likert score between respondents coded as
  `classchild` ≥ 4 vs ≤ 2. Secondary estimand: slope from ordinal logit treating
  `classchild` as ordered predictor.
- **Model**: Survey-weighted linear regression (if weights confirmed) or SRS OLS with
  robust SEs clustered by nothing (default) plus proportional-odds model as robustness.
- **Controls**: `selfage`, `gendermale`, indicator for current net worth above median.
- **Missing data**: If ≤5% missing per variable, use listwise deletion; otherwise apply
  multiple imputation by chained equations (m=20 iterations, seed 20251016) after verifying
  MAR assumption plausibility.
- **Robustness**:
  1. Re-code `classchild` into z-score and model as continuous trend.
  2. Stratify by gender to check heterogeneity (report effect modification descriptively).

### H3 (adversity family; claim C3)
- **Question**: Is childhood verbal/emotional abuse (`mds78zu`) associated with higher adult
  depression tendencies (`wz901dj`)?
- **Estimand**: Average difference in probability of selecting Likert ≥4 between exposed vs
  non-exposed respondents.
- **Model**: Survey-weighted logistic regression on binary indicator `wz901dj >= 4` with
  controls `selfage`, `gendermale`, `classchild`, and `mentalillness` diagnosis history to
  capture baseline severity.
- **Missing data**: Expect non-response due to sensitivity; implement MI (m=20, burn-in 10,
  seed 20251016) if missingness >10% and assumed MAR conditional on controls; otherwise
  treat as its own category and compare.
- **Robustness**:
  1. Negative-control outcome: `height` (should show null association); failure triggers
     review of reporting bias.
  2. Alternate exposure definition using adolescent abuse (`v1k988q`).

## Measurement & Validity Tasks
- Populate `qc/measures_validity.md` with reliability (Cronbach's α) for `h33e6gg`,
  `npvfh98`, `wz901dj`, `classchild`, `mds78zu`, `dcrx5ab`, and `networth`.
- Document DIF checks across gender for each Likert outcome before PAP freeze.

## Privacy & Disclosure
- Suppress or redact any cell counts < 10 in public artifacts per SAMPL guidance.
- Sensitive trauma variables will only appear in aggregate with indicator-level    
  suppression log recorded in `qc/disclosure_check_loop_000.md` before sharing outputs.

## Reproducibility Notes
- **Script location** (planned): `analysis/code/01_prepare_data.py` for cleaning and
  `analysis/code/02_models.py` for estimations.
- **Regeneration command** (placeholder):
  ```bash
  python analysis/code/00_run_all.py --seed 20251016 --pap analysis/pre_analysis_plan.md
  ```
- **Outputs**: Tables under `tables/` and figures under `figures/` will include MANIFEST
  entries referencing the exact command above once scripts exist.

## Outstanding Items Blocking Freeze
1. Confirm presence/absence of survey weights + replicate structure (Task T-001).
2. Gather ≥3 DOI-backed references + populate `lit/evidence_map.csv` with claim IDs.
3. Create `qc/measures_validity.md` entries and reliability estimates.
4. Finalize Semantic Scholar query automation + bibliography entries.

Until the above are complete, this PAP remains a draft and no confirmatory results will be
produced or committed.
