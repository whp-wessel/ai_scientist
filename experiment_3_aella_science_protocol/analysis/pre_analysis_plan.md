# PAP Draft
Generated: 2025-11-03T20:01:43Z | Seed: 20251016
Status: Draft (not frozen) | Regen: `python analysis/code/bootstrap_setup.py --artifact analysis/pre_analysis_plan.md`

Portfolio: HYP-001 (High), HYP-002 (Medium), HYP-003 (High), HYP-004 (Medium)

HYP-001 → Outcome `I love myself (2l8994l)`; Predictor `classchild`; Covariates `selfage`, `gendermale`, `cis`; Estimand weighted change per class unit; Model survey OLS (HC3); Robustness collapse class + ordinal logit; MI if missing >5%.

HYP-003 → Outcome `I tend to suffer from anxiety (npvfh98)-neg`; Predictor `CSA_score_indicator`; Covariates `selfage`, `gendermale`, `classchild`; Estimand weighted mean difference; Model survey OLS + design t-test; Robustness ordinal CSA bins + drop CSA>=6; monitor missingness.

Roadmap: 1) Finalize survey design. 2) Label exploratory descriptives. 3) Freeze PAP & tag git. 4) Execute confirmatory models and log seeds in `analysis/results.csv` + MANIFEST.

Manuscript parity: update `reports/findings_v0.1.md` and `papers/main/manuscript.tex` together; store regeneration commands with outputs.
