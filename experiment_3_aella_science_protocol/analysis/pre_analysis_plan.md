# PAP (Frozen)
Generated: 2025-11-03T22:05:00Z | Seed: 20251016
Frozen: 2025-11-04T07:58:50Z | Git tag (post-commit): `pap-freeze-20251104`
Status: Frozen | Regen: `python analysis/code/bootstrap_setup.py --artifact analysis/pre_analysis_plan.md`

## Scope and data lineage
- Raw source: `data/raw/childhoodbalancedpublic_original.csv` (see `artifacts/checksums.json` for SHA-256).
- Clean analysis file: `data/clean/childhoodbalancedpublic_with_csa_indicator.csv`, regenerated via  
  `python analysis/code/derive_csa_indicator.py --dataset data/raw/childhoodbalancedpublic_original.csv --out-dataset data/clean/childhoodbalancedpublic_with_csa_indicator.csv --out-distribution tables/csa_indicator_distribution.csv --config config/agent_config.yaml --codebook-in docs/codebook.json --codebook-out docs/codebook.json`.
- Survey design: `docs/survey_design.yaml` documents absence of weights/strata/clusters; analyses proceed under simple random sampling with HC3 variance.
- Confirmatory execution command (frozen):  
  `python analysis/code/confirmatory_models.py --dataset data/clean/childhoodbalancedpublic_with_csa_indicator.csv --config config/agent_config.yaml --survey-design docs/survey_design.yaml --hypotheses HYP-001 HYP-003 --results-csv analysis/results.csv --overwrite`.
- Multiple-imputation plan: trigger MI (m=5, seed 20251016) using future `analysis/code/impute_mi.py` if any included variable exceeds 5% missingness; otherwise perform listwise deletion. All seeds must match `artifacts/seed.txt`.

Portfolio status: HYP-001 (confirmatory), HYP-003 (confirmatory), HYP-002 (exploratory backlog), HYP-004 (exploratory backlog).

## HYP-001 — Childhood class and adult self-love
- **Outcome**: `I love myself (2l8994l)` (Likert −3 to +3)  
  **Predictor**: `classchild` (0–6 ordinal)  
  **Covariates**: `selfage`, `gendermale`, `cis`
- **Estimand**: Average change in outcome per one-step increase in childhood class (design-based OLS with HC3).
- **Primary model**: `survey`-adjusted linear regression under SRS assumption (weights=1). Robust HC3 standard errors with seed 20251016.
- **Model equation** (confirmatory, SRS):  
  `y_i = β_0 + β_1 · classchild_i + β_2 · selfage_i + β_3 · gendermale_i + β_4 · cis_i + ε_i`, with HC3 variance.  
  `β_1` identifies the estimand.
- **Analysis code**: `python analysis/code/confirmatory_models.py --dataset data/clean/childhoodbalancedpublic_with_csa_indicator.csv --config config/agent_config.yaml --survey-design docs/survey_design.yaml --hypotheses HYP-001 --results-csv analysis/results.csv --overwrite`
- **Robustness checks**:  
  1. Treat `classchild` as categorical with Helmert contrasts (tests functional form).  
  2. Fit proportional-odds ordinal logit on the outcome; assess Brant test to flag violations.  
  3. Standardise outcome to z-score and refit OLS to confirm scale invariance.
- **Missing-data plan**: If any covariate missingness >5%, execute multiple imputation (m=5, deterministic seed 20251016) before confirmatory analysis; otherwise listwise deletion.
- **Classification**: Confirmatory (Frozen PAP)

## HYP-003 — CSA exposure and anxiety agreement
- **Outcome**: `I tend to suffer from anxiety (npvfh98)-neg`
- **Predictor**: `CSA_score_indicator` (derived binary; 1 if CSA_score>0)
- **Covariates**: `selfage`, `gendermale`, `classchild`
- **Estimand**: Difference in mean anxiety agreement between any CSA exposure vs none.
- **Primary model**: OLS with HC3 under SRS, plus design-based two-sample comparison (Welch t using survey variance) to confirm direction/scale.
- **Model equation** (confirmatory, SRS):  
  `y_i = β_0 + β_1 · CSA_i + β_2 · selfage_i + β_3 · gendermale_i + β_4 · classchild_i + ε_i`, HC3 variance; `β_1` captures the mean difference between exposed vs non-exposed.
- **Analysis code**: `python analysis/code/confirmatory_models.py --dataset data/clean/childhoodbalancedpublic_with_csa_indicator.csv --config config/agent_config.yaml --survey-design docs/survey_design.yaml --hypotheses HYP-003 --results-csv analysis/results.csv --overwrite`
- **Robustness checks**:  
  1. Logistic regression on `CSA_score_indicator` predicting high anxiety (>=1) to examine non-linear probability scale.  
  2. Replace binary predictor with ordinal bins `{0, 1-3, 4+}` and test linear trend.  
  3. Exclude extreme tail (`CSA_score` > 15) to assess leverage sensitivity.
- **Missing-data plan**: Monitor derived indicator (currently 0% missing). If downstream models require additional variables with >5% missingness, extend MI plan above; record seeds.
- **Classification**: Confirmatory (Frozen PAP)

## Out-of-PAP exploratory hypotheses (not frozen)

### HYP-002 — Current class and depression (Exploratory backlog)
- **Status**: Proposed; requires additional feasibility checks on classcurrent measurement error.
- **Next**: Investigate depression outcome missingness and potential confounding controls before PAP inclusion.

### HYP-004 — Social support and self-love (Exploratory backlog)
- **Outcome**: `I love myself (2l8994l)`
- **Predictor**: `In general, people in my *current* social circles tend to treat me really well (71mn55g)` (Likert −3 to +3; instrument equivalence verified against tmt46e6 via `analysis/code/verify_social_support_equivalence.py`).
- **Covariates**: `selfage`, `gendermale`
- **Rationale**: Pivot from low-coverage variant (`tmt46e6`, 2.65% coverage) to `71mn55g` (97.3%) after confirming identical wording/scale apart from routing typo. Instrument overlap check confirms mutually exclusive routing with no dual responders.
- **Estimand**: Weighted change in self-love per one-unit increase in perceived support.
- **Planned model**: Design-based OLS (HC3) treating the predictor as continuous; evaluate proportional-odds model if outcome retains ordinal interpretation.
- **Robustness checks (pre-registration pending)**:  
  1. Recode support predictor to three bins `{≤0, 1-2, 3}` to assess non-linearity.  
  2. Indicator for top-two responses (2/3) vs others to check threshold effects.
- **Next steps**: Complete literature review on social-support pathways and confirm no routing artifacts before promoting to confirmatory status.

## Confirmatory deliverables and reproducibility
 - **Results target**: Append confirmatory estimates for HYP-001 and HYP-003 to `analysis/results.csv` (overwrite disabled once populated); include HC3 standard errors, 95% CIs, raw p-values, BH-adjusted q-values, sample sizes.
 - **Robustness outputs**: Store model-specific diagnostics under `qc/` (e.g., `qc/hyp-001_helmert.md`, `qc/hyp-003_tail_trim.md`) with regeneration commands produced by `analysis/code/run_robustness_checks.py`.
 - **Figures/Tables**: Confirmatory tables under `tables/confirmatory/` (CSV) plus Markdown summaries; any figures saved as PNG + JSON spec in `figures/confirmatory/`.
 - **MANIFEST**: `papers/main/MANIFEST.md` records this PAP freeze, commit/tag `pap-freeze-20251104`, and regeneration commands for notebook excerpts and manuscript parity.
 - **FDR control**: Apply Benjamini–Hochberg at q=0.05 within the confirmatory family `{HYP-001, HYP-003}` using seed 20251016; execute via  
   `python analysis/code/fdr_adjust.py --results analysis/results.csv --hypotheses analysis/hypotheses.csv --config config/agent_config.yaml --family-scope confirmatory --out analysis/results.csv --audit-table tables/fdr_adjustment_confirmatory.csv`.
 - **Robustness automation**: Execute PAP-listed checks using  
   `python analysis/code/run_robustness_checks.py --dataset data/clean/childhoodbalancedpublic_with_csa_indicator.csv --config config/agent_config.yaml --qc-dir qc --tables-dir tables/robustness --hypotheses HYP-001 HYP-003`.

## Next steps post-freeze
1. Execute confirmatory models per the command above; refrain from altering model specifications without amendment.
2. Implement pre-specified robustness checks and document outcomes.
3. Draft confirmatory results in `reports/findings_v0.1.md` and mirror text in `papers/main/manuscript.tex` (ensure parity per `config/agent_config.yaml`).
4. After confirmatory run, execute FDR adjustment and robustness scripts for audit trails.
