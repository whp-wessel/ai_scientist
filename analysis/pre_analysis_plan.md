# Pre-Analysis Plan (Draft)

- Document status: Draft (not frozen)
- Generated: 2025-10-16T12:44:10Z
- Seed: 20251016
- Regeneration: `python analysis/code/bootstrap_setup.py --only pap`

## Scope

This draft PAP covers preliminary confirmatory planning for three wellbeing, socioeconomic, and relational hypotheses (HYP-001 through HYP-003). Status remains exploratory until design diagnostics and weighting strategy are finalized.

## Data

- Dataset: `childhoodbalancedpublic_original.csv` (n=14,443; p=718) as inspected on 2025-10-16.
- Inclusion: respondents with non-missing variables required per hypothesis.
- Survey design: TODO — pending confirmation of weight/strata/cluster variables. Analyses will assume SRS with weights=1 until metadata is verified.

## Hypotheses

1. **HYP-001 (wellbeing)** — Respondents reporting greater childhood emotional abuse will show lower adult self-love scores.
2. **HYP-002 (socioeconomic)** — Higher perceived childhood class associates with higher current net worth category.
3. **HYP-003 (relationships)** — Active religious practice is associated with preferring monogamy.

## Outcomes, Predictors, Controls

### HYP-001
- Outcome: `I love myself (2l8994l)` (Likert; treat as approximately continuous pending scale confirmation).
- Predictor: `during ages *0-12*: your parents verbally or emotionally abused you (mds78zu)` (ordinal frequency).
- Controls: `selfage`, `gendermale`, `education`.
- Estimand: Survey-weighted mean difference across abuse frequency categories; fallback to ordinal regression if Likert assumptions break.

### HYP-002
- Outcome: `networth` (ordered categories).
- Predictor: `classchild` (ordered categories).
- Controls: `selfage`, `gendermale`, `education`.
- Estimand: Survey-weighted cumulative logit (proportional odds). Will assess proportional odds assumption.

### HYP-003
- Outcome: `monogamy` (categorical).
- Predictor: `Do you *currently* actively practice a religion? (902tbll)`.
- Controls: `selfage`, `gendermale`.
- Estimand: Survey-weighted multinomial logit relative risk ratios for monogamy preference categories.

## Missing Data Strategy

- Profile missingness for all variables listed above.
- If missingness > 5% on key variables and plausibly MAR, implement multiple imputation with seed 20251016; otherwise use listwise deletion for preliminary analyses.

## Robustness Checks (pre-specified)

- **HYP-001:** (1) Recode abuse predictor into binary (any vs none). (2) Use ordinal logistic regression for Likert outcome categories.
- **HYP-002:** (1) Collapse extreme net worth bins to ensure cell size ≥ 10. (2) Fit survey-weighted linear regression on mid-point dollars as sensitivity.
- **HYP-003:** (1) Restrict sample to respondents currently in relationships. (2) Alternative coding that groups non-monogamous categories together.

## Multiplicity

- Apply Benjamini–Hochberg FDR control at q=0.05 within the set {HYP-001, HYP-002, HYP-003} once confirmatory analyses commence.

## Deviations & Updates

- Any deviations from this draft must be documented in `analysis/pre_analysis_plan.md` with timestamped notes and reason. PAP will be frozen only after survey design validation.

## Reproducibility Notes

- Regenerate this draft with `python analysis/code/bootstrap_setup.py --only pap`.
- All analyses will honor the global project seed `20251016`.
