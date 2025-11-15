# Guidance, the Sacred, and Support: How Childhood Experiences Shape Adult Emotional Health in a Global Sample

## Abstract
The Balanced Childhood Survey captures 14,443 respondents whose childhood family climate, religious practice, and current wellbeing are measured on harmonized Likert-type scales. We test three preregistered hypotheses from resilience, buffering, and religion-health literatures: (1) positive parental guidance protects adult distress, (2) religiosity aligns with relationship and self-regard outcomes, and (3) current social support moderates the legacy of childhood adversity. Weighted least-squares regressions with HC3 robust errors standardize every exposure/outcome, and Benjamini–Hochberg corrections are applied per hypothesis. Guidance lowers anxiety (β=-0.135, 95% CI [-0.152, -0.118]) and impairment (β=-0.163, 95% CI [-0.180, -0.146]) but is unexpectedly positive for depression (β=0.193, 95% CI [0.176, 0.210]). Current religiosity links with greater self-love (β=0.037, 95% CI [0.019, 0.054]) and lower unhappiness (β=-0.034, 95% CI [-0.051, -0.017]), while external religiosity retains only a weak self-love association. Support interacts with a standardized adversity index: the interaction boosts the anxiety/unhappiness slope (β=0.070 and β=0.046, respectively) and flattens depression/self-love gradients (β=-0.049 and β=-0.041). Sensitivity tests (trimmed weights, alternative cohesion/adversity composites) and the guidance–depression diagnostics are archived to keep the write-up reproducible.

## Introduction
Felitti et al. (1998) and the broader ACE literature cemented that disruptive childhood households forecast adult distress, and theorists have since emphasized responsive caregiving (Repetti, Taylor, & Seeman, 2002) and religious/spiritual resources (Koenig et al., 2012) as modifiers of that trajectory. The Balanced Childhood Survey’s simultaneous measurement of parental guidance, emotional/verbal abuse, religious practice, and present-day social support allows a single-capstone test of whether guidance shields wellbeing, religiosity offers psychological ballast, and support buffers adversity’s residue.

## Methods
### Data and preprocessing
Analyses use `childhoodbalancedpublic_original.csv` restricted to the 14,443 respondents with positive sampling weights. All exposures, covariates, and outcomes are z-scored after correcting orientation (e.g., distress items carrying a `-neg` suffix are flipped so higher values signal greater distress). The guidance index averages the two parental guidance items (`pqo6jmj`, `dcrx5ab`), adversity blends emotional abuse, conflict, and separation indicators from ages 0–12 and 13–18, and current support relies on `71mn55g`. Current religiosity is the ordinal `902tbll` mapping (0–3) while external religiosity uses `externalreligion`. Outcomes include anxiety (`npvfh98`), depression (`wz901dj`), functional impairment (`kd4qc3z`), relationship satisfaction (`hp9qz6f`), self-love (`2l8994l`), and unhappiness (`ix5iyv3`). Country dummies, age, gender indicators (`biomale`, `gendered`, `cis`), education, class indicators (`classchild`, `classteen`, `classcurrent`), net worth, and the `religion` variable were recorded as covariates.

### Modeling
H1 fits three WLS models (one per emotional distress outcome) with the guidance index plus the covariates above. H2 regresses each wellbeing outcome on either current or external religiosity, always controlling for the guidance index and the base covariates (the `religion` control is dropped when it duplicates the exposure). H3 nests the adversity index, support score, and their interaction alongside the H2 covariates plus current religiosity. All models are run with HC3 robust standard errors; unweighted counterparts are archived for transparency.

### Multiple testing and reproducibility
Benjamini–Hochberg adjustments occur per hypothesis (i.e., across the three H1 outcomes, the two religiosity exposures × three H2 outcomes, and the four H3 interactions). The entire pipeline is reproducible via `python analysis/run_analysis.py --sensitivity --loop-index 66` with the plan frozen in `analysis/pre_analysis_plan.md` (commit 808054d3455621759d730efc215ef02802924ff0).

## Results
### H1 – Childhood guidance and adult distress
Guidance strongly predicts lower anxiety (β=-0.135, 95% CI [-0.152, -0.118], BH-FDR=0.000, N=14,430) and functional impairment (β=-0.163, 95% CI [-0.180, -0.146], BH-FDR=0.000, N=14,430) but retains a positive association with depression (β=0.193, 95% CI [0.176, 0.210], BH-FDR=0.000, N=14,431), a pattern that persists under trimmed weights and alternative cohesion indices.

### H2 – Religiosity and wellbeing
Current religiosity predicts greater self-love (β=0.037, 95% CI [0.019, 0.054], BH-FDR=0.000, N=14,428) and lower unhappiness (β=-0.034, 95% CI [-0.051, -0.017], BH-FDR=0.000, N=14,430) but has no detectable link with relationship satisfaction (β=0.008, 95% CI [-0.010, 0.025], BH-FDR=0.379, N=14,429). External religiosity mirrors only the self-love signal (β=0.017, 95% CI [0.000, 0.034], BH-FDR=0.132, N=14,429) while its association with relationship satisfaction remains non-significant and the unhappiness coefficient is null. These patterns underscore that the protective religiosity correlates are more robust for self-regard than for relational outcomes.

### H3 – Support moderates the adversity gradient
Support × adversity interactions diverge by outcome: higher support amplifies the anxiety (β=0.070, 95% CI [0.055, 0.085], BH-FDR=0.000, N=14,031) and unhappiness slopes (β=0.046, 95% CI [0.031, 0.061], BH-FDR=0.000, N=14,032) but flattens the depression (β=-0.049, 95% CI [-0.064, -0.034], BH-FDR=0.000, N=14,032) and self-love gradients (β=-0.041, 95% CI [-0.058, -0.025], BH-FDR=0.000, N=14,030). Simple slopes at ±1 SD support and predicted values at mean adversity are saved in `artifacts/h3_simple_slopes_loop66.csv` and `artifacts/h3_predicted_supports_loop66.csv`, respectively.

## Sensitivity and robustness
Trimmed-weight regressions (weights capped at the 99th percentile, `artifacts/sensitivity_trimmed_weights_loop66.csv`) preserve the H1 coefficients and keep H2/H3 estimates within ±0.02 of the base models. The alternative cohesion composite (guidance + playful family cohesion) and two adversity configurations (parental verbal/emotional abuse, feeling “at war with yourself”) maintain the same sign patterns for the primary coefficients (`artifacts/sensitivity_cohesion_loop66.csv`; `artifacts/sensitivity_adversity_loop66.csv`). The guidance–depression diagnostic table (`artifacts/guidance_depression_sensitivity_loop66.csv`) documents a stable correlation (r=0.270) that prompts future work on nonlinearity or measurement heterogeneity.

## Limitations
- The `Religionchildhood` column is fully missing in this wave, so we could not include the intended childhood-religion control.
- The simple slopes and predicted values assume covariates remain at their analytic means, which bounds their interpretability.
- The `religion` control was dropped from the H2 models because it duplicated the active religiosity exposures and inflated coefficients.

## Reproducibility
All regression tables, plots, and artifacts for loop 66 are archived under `artifacts/` (e.g., `artifacts/regression_records_loop66.csv`, `artifacts/h1_coefficients_loop66.png`, `artifacts/pip_freeze_loop66.txt`). The summary in `artifacts/analysis_loop66_summary.md` recaps the pipeline, and the plan stays frozen in `analysis/pre_analysis_plan.md`.
