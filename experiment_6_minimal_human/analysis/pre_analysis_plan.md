# Pre-Analysis Plan
status: frozen
registry_url: https://github.com/whp-wessel/ai_scientist/blob/main/analysis/pre_analysis_plan.md
freeze_commit: <pending commit containing this frozen PAP>

## 1. Research context and dataset
- **Dataset**: `childhoodbalancedpublic_original.csv`, a cross-sectional, balanced-childhood sample with 14,443 respondents and 718 variables. Descriptive scripts (`analysis/literature_descriptives.py`) will be rerun to log sample size, geography, gender, and scale distributions before every analytic push so that this plan always links to a reproducible snapshot.
- **Survey structure**: The `weight` column provides a continuous sampling weight (observed minimum 0? implicitly positive values such as 130, 170, 310) and will be inspected for zero/negative values. No explicit strata or PSU columns exist, so we will treat the design as weighted but not clustered.
- **Key constructs**: Childhood guidance (parents gave useful guidance at ages 0–12: `pqo6jmj`, 13–18: `dcrx5ab`), childhood verbal/emotional abuse (`mds78zu`, `v1k988q`), current social support (`71mn55g`), religiosity (`902tbll`, `externalreligion`, `Religionchildhood`), adulthood wellbeing (`npvfh98`-neg anxiety, `wz901dj` depression, `ix5iyv3`-neg unhappiness, `hp9qz6f` relationship satisfaction, `2l8994l` self-love), functional impairment (`kd4qc3z`), and socioeconomic controls (`selfage`, `biomale`, `gendered`, `cis`, `education`, `classchild`, `classteen`, `classcurrent`, `networth`, `religion`, `country`).
- **Research goal**: Translate the three hypotheses from `analysis/hypotheses.md` into preregistered regression models that use survey weights and robust standard errors, disclose all variable derivations, and report effect sizes with confidence intervals. Each hypothesis is grounded in at least one peer-reviewed source (Hypothesis 1: Felitti et al. 1998; Hypothesis 2: Koenig 2012; Hypothesis 3: Cohen & Wills 1985).

## 2. Hypotheses, variables, and estimation plan

### H1 — Childhood family cohesion shields adult emotional health
- **Statement**: Higher parental guidance during ages 0–12 and 13–18 predicts lower adult anxiety, lower adult depression, and less functional impairment due to emotional issues, controlling for demographics and SES (Felitti et al. 1998; Repetti, Taylor, & Seeman 2002; Bethell et al. 2019).
- **Exposures**: Average of `pqo6jmj` and `dcrx5ab`, standardized (mean=0, SD=1) after confirming both scales share the same direction. Additional cohesion checks (e.g., household joking items) will be recorded but not part of the preregistered index.
- **Outcomes**: `npvfh98`-neg (anxiety), `wz901dj` (depression), `kd4qc3z` (difficulty accomplishing things due to emotional issues), all reoriented so that higher scores mean worse emotional functioning (flip `-neg` variables as needed) and standardized for coefficient comparability.
- **Model**: Weighted least squares (WLS) regressing each outcome on the guidance index plus controls. Report unstandardized coefficients (per 1-SD increase in guidance) and standardized betas. Use the `weight` column and HC3 robust standard errors; include the sample weight as the WLS weight and report both weighted and unweighted versions.
- **Covariates**: `selfage`, `biomale`, `gendered`, `cis`, country dummies (top categories, with “Other” collapsed if necessary), `education`, `classchild`, `classteen`, `classcurrent`, `networth`, and `religion`/`Religionchildhood` to account for background religiosity.
- **Inference**: Two-sided tests with 95% confidence intervals and Benjamini-Hochberg false discovery rate (FDR) adjustment across the three outcomes. Provide effect-size interpretation as "β per 1-SD increase in parental guidance" and note the proportion of variance explained.

### H2 — Religiosity and psychological well-being in adulthood
- **Statement**: Greater current religiosity and childhood religious support correlate with higher relationship satisfaction and self-love and lower unhappiness (Koenig 2012; Martin, Kirkcaldy, & Siefen 2003; Jung 2017).
- **Exposures**: `902tbll` (current religiosity practice; ordinal 0–3) and `externalreligion` (childhood importance) modeled separately. Each treated as scaled numeric variables; secondary analysis will check `Religionchildhood` categories.
- **Outcomes**: `hp9qz6f` (relationship satisfaction), `2l8994l` (self-love), and `ix5iyv3`-neg (reverse-coded to represent unhappiness). Outcomes will be standardized.
- **Model and inference**: WLS with the same covariates as H1 plus `parental guidance index` to isolate religiosity from general family climate. Weighted coefficients will be interpreted per one-unit increase in religiosity; also present predicted values at each ordinal step to demonstrate substantive change. Robust SEs (HC3) and significance thresholds as above.
- **Sensitivity**: Test whether the relationship persists when replacing `902tbll` with `religion` practice frequency or with the more diffuse `externalreligion` measure to ensure robustness to alternative religiosity codings.

### H3 — Current social support moderates abuse→distress
- **Statement**: Higher present-day social support weakens the positive association between childhood verbal/emotional abuse and adult distress (Cohen & Wills 1985; Košárková et al. 2020).
- **Exposures**: Adversity index formed by averaging `mds78zu` (0–12 verbal/emotional abuse) and `v1k988q` (13–18 version), standardized after checking internal consistency (Cronbach’s alpha ≥ 0.70). Alternative abuse items (bullying, sexual abuse) will be recorded for sensitivity.
- **Moderator**: Continuous `71mn55g` (general social support). As robustness, consider `tmt46e6` on smaller sample.
- **Outcomes**: Same distress/discomfort outcomes as H1 (`npvfh98`, `wz901dj`, `ix5iyv3`-neg).
- **Model**: WLS of each outcome on the abuse index, support score, their interaction, and all H1 covariates plus current relationship satisfaction where relevant. Report interaction coefficients, plot simple slopes at ±1 SD of support, and compute the change in the abuse coefficient across support quartiles.
- **Inference**: Use HC3 SEs; interpret moderation as the difference in predicted distress per 1-SD increase in abuse at low vs. high support.

## 3. Data management, coding, and missingness
- **Coding**: All `-neg` items will be multiplied by `-1` so higher values consistently represent increases in the named construct when needed. Guidance and adversity indices are averages of their items, computed only for respondents with complete inputs (recording the N and Cronbach’s alpha). Indicators like `biomale`, `gendered`, `cis`, and `country` will be treated as binary or categorical dummies with pre-specified reference categories documented in the analysis script.
- **Missing data**: For the primary n (≥14k), if any outcome/exposure pair is missing we will drop that respondent for that specific regression but log the number of observations lost to listwise deletion. For control covariates with ≤5% missingness, impute medians (continuous) or create a “missing” indicator (categorical). If missingness exceeds 5% for a core covariate, run a multiple imputation (m=20, chained equations) as a sensitivity check and compare estimates to the primary complete-case results.
- **Sample restrictions**: Restrict to respondents with valid `selfage` (18–90) and non-missing weights. Document the final analytic sample size for each model, including the percent retained of the starting-frame 14,443 rows.

## 4. Survey-aware analytic approach
- **Weights**: Use `weight` column as analytic weight inside `statsmodels.regression.linear_model.WLS` (or `survey` module if available) and report summary tables with both weight-adjusted and unweighted estimates so readers can assess the impact of weighting.
- **Robust SE**: Request heteroskedasticity-robust (HC3) standard errors for all estimations to mitigate residual variance heterogeneity given the collapsed sample.
- **Effect sizes**: Report unstandardized coefficients per one-unit change as well as standardized (per 1-SD) to facilitate comparisons across outcomes. Compute 95% CIs and Cohen’s d equivalent where possible.
- **Multiple testing**: Apply Benjamini-Hochberg FDR correction across the set of outcomes within each hypothesis. Call out which associations remain significant after correction in final tables.

## 5. Sensitivity and robustness checks
- **Alternative exposures**: Replace the parental guidance index with a composite of additional cohesion items, and replicate the adversity index with a broader set of childhood abuse indicators (including physical/sexual abuse fields) to check whether the main pattern holds.
- **Alternate moderators**: Recompute H3 using `tmt46e6` support when available (noting smaller sample) and test whether `externalreligion` interacts with adversity as a parallel buffer.
- **Weight handling**: Repeat each regression using unweighted OLS and compare coefficients/SEs; also trim extreme weights at the 99th percentile to ensure no single respondent dominates inference.
- **Model form**: For outcomes that show nonlinearity or heavy tails, run generalized additive models (GAMs) as a sensitivity to ensure linearity is not driving results.

## 6. Reproducibility, preregistration, and reporting
- **Code**: All data preparation and modeling code will be captured in the `analysis/` directory (e.g., `analysis/hypothesis_models.py`) with a `main()` that reads `childhoodbalancedpublic_original.csv`, applies the transformations above, and writes output tables/figures to `outputs/`. The `analysis/literature_descriptives.py` script will continue to log key sample statistics for traceability.
- **Versioning**: This plan links to the latest Git commit via `freeze_commit` above; once this document is committed, update `freeze_commit` to that hash so analysts can reference the exact code path. If a release tag is created, substitute `freeze_tag`.
- **Reporting**: Final tables will present the number of observations, weighted means, coefficients, robust SEs, standardized betas, FDR-adjusted p-values, and 95% CIs. Effect size narratives will translate coefficients into expected changes over 1-SD shifts in the exposures.
- **Limitations**: Acknowledge the cross-sectional nature, reliance on self-report, and absence of explicit sampling strata. Document any deviations from this plan in the analysis write-up.
