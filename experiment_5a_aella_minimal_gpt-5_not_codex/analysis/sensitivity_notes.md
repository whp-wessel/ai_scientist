status: draft
title: Sensitivity Notes — Ordinal Outcomes and Specification Checks

Summary:
- Many outcomes are Likert-style items treated as numeric in exploratory OLS. As sensitivity, consider ordered logit/probit and nonlinearity in predictors (splines for `classteen`, `externalreligion`).
- Add covariates: consider education, region, and childhood SES interactions if available in codebook; document variable selection and pre-specified transformations at PAP freeze.
- Missingness: outcomes have 5–6 missing values; confirm MCAR/MAR plausibility and verify robustness to complete-case vs. simple imputation (mean/median), noting imputation is discouraged for ordinal outcomes without proper models.
- Survey design: still no weights/strata/clusters. If design metadata surface, re-run primary models with design-based SEs and update `analysis/results.csv` with `design_used=true`.

Planned checks (exploratory until PAP freeze):
- Refit H1–H4 with ordered logit and report marginal effects.
- Add quadratic terms for `classteen` and `externalreligion` and compare AIC/BIC.
- Robust SEs (HC3) vs. OLS SEs; compare conclusions.

