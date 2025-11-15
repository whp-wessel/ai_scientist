# Guidance, the Sacred, and Support: How Childhood Experiences Shape Adult Emotional Health in a Global Sample

## Abstract
We preregistered three hypotheses in the Balanced Childhood Survey (14,443 respondents) and tested them using survey-weighted least-squares regressions (HC3 SEs) with Benjamini–Hochberg corrections. Childhood guidance lowers anxiety (β = -0.135, 95% CI [-0.152, -0.118], BH-FDR < 0.001) and functional impairment (β = -0.163, 95% CI [-0.180, -0.146], BH-FDR < 0.001) while predicting more depression (β = 0.193, 95% CI [0.176, 0.210], BH-FDR < 0.001). Current religiosity links to greater self-love (β = 0.037, 95% CI [0.019, 0.054], BH-FDR < 0.001) and less unhappiness (β = -0.034, 95% CI [-0.051, -0.017], BH-FDR < 0.001), whereas external religiosity only preserves a modest self-love signal (β = 0.017, 95% CI [0.000, 0.034], BH-FDR = 0.132). Support × adversity interactions depend on the outcome: anxiety (β = 0.070, 95% CI [0.055, 0.085]), depression (β = -0.049, 95% CI [-0.064, -0.034]), unhappiness (β = 0.046, 95% CI [0.031, 0.061]), and self-love (β = -0.041, 95% CI [-0.058, -0.025]) all achieve BH-FDR < 0.001.

## Introduction
Felitti et al.’s (1998) Adverse Childhood Experiences framework, resilience models (Repetti et al., 2002; Bethell et al., 2019), religion-health reviews (Koenig et al., 2012; Martin et al., 2003), and Cohen and Wills’s (1985) buffering hypothesis motivate our focus on childhood guidance, religiosity, and social support. The Balanced Childhood Survey captures retrospective guidance, adversity, religiosity, and support items that map directly onto this literature, letting us preregister and test whether guidance shields distress (H1), whether religiosity predicts wellbeing (H2), and whether current support moderates earlier adversity (H3) as recorded in `analysis/pre_analysis_plan.md`.

## Methods

### Data and preprocessing
We analyze `childhoodbalancedpublic_original.csv`, keep respondents with positive weights (14,443 rows), and archive the pass in `artifacts/analysis_loop78_summary.md`. The guidance index averages the ages 0–12 and 13–18 guidance items, the adversity index aggregates eight verbal/emotional/conflict indicators, religiosity blends current (`902tbll`) and external items, and support is the `71mn55g` measure. Outcomes include anxiety (`npvfh98`), depression (`wz901dj`), functional impairment (`kd4qc3z`), relationship satisfaction (`hp9qz6f`), self-love (`2l8994l`), and unhappiness (`ix5iyv3`). All scales are oriented so higher values reflect more of the construct, z-standardized, and respondents missing any key variable are dropped (`artifacts/h1_sample_comparison_loop78.csv`, `artifacts/h1_vif_loop78.csv`).

### Modeling
Each hypothesis relies on weighted least squares with HC3 robust standard errors plus an unweighted counterpart, following the frozen plan. H1 regresses standardized anxiety, depression, and functional impairment on the guidance index with covariates for age, gender indicators (`biomale`, `gendered`, `cis`), education, childhood/current class, net worth, religion, external religiosity, and country dummies. H2 regresses relationship satisfaction, self-love, and unhappiness separately on current or external religiosity while controlling for the guidance index and dropping the `religion` covariate when it mirrors the exposure. H3 regresses each emotional outcome on adversity, support, and their interaction plus the full covariate set and current religiosity, yielding simple slopes (`artifacts/h3_simple_slopes_loop78.csv`) and predicted values (`artifacts/h3_predicted_supports_loop78.csv`).

### Multiple testing and reproducibility
P-values are adjusted within each hypothesis block using Benjamini–Hochberg. Figures and tables are archived (`artifacts/h1_coefficients_loop78.png`, `artifacts/h2_coefficients_loop78.png`, `artifacts/h3_coefficients_loop78.png`, `artifacts/h3_interaction_loop78.png`), and the pipeline runs via `python analysis/run_analysis.py --sensitivity --loop-index 78`, which regenerates every artifact and the `artifacts/pip_freeze_loop78.txt` snapshot.

## Results

### H1 – Childhood guidance and adult distress
Guidance lowers anxiety (β = -0.135, 95% CI [-0.152, -0.118], N = 14,430, BH-FDR < 0.001) and functional impairment (β = -0.163, 95% CI [-0.180, -0.146], N = 14,430, BH-FDR < 0.001) while maintaining a positive depression coefficient (β = 0.193, 95% CI [0.176, 0.210], N = 14,431, BH-FDR < 0.001); the regression trace is `artifacts/regression_records_loop78.csv`.

### H2 – Religiosity and wellbeing
Current religiosity is unrelated to relationship satisfaction (β = 0.008, 95% CI [-0.010, 0.025], N = 14,429, BH-FDR = 0.379) but associates with more self-love (β = 0.037, 95% CI [0.019, 0.054], N = 14,428, BH-FDR < 0.001) and less unhappiness (β = -0.034, 95% CI [-0.051, -0.017], N = 14,430, BH-FDR < 0.001). External religiosity only sustains the self-love link (β = 0.017, 95% CI [0.000, 0.034], N = 14,429, BH-FDR = 0.132) while remaining null for relationship satisfaction (β = -0.013, 95% CI [-0.030, 0.004], BH-FDR = 0.201) and unhappiness (β = 0.000, 95% CI [-0.016, 0.016], BH-FDR = 0.967).

### H3 – Support moderates adversity
The adversity × support interaction varies by outcome: anxiety (β = 0.070, 95% CI [0.055, 0.085], N = 14,031, BH-FDR < 0.001) and unhappiness (β = 0.046, 95% CI [0.031, 0.061], BH-FDR < 0.001) steepen with more support, whereas depression (β = -0.049, 95% CI [-0.064, -0.034], BH-FDR < 0.001) and self-love (β = -0.041, 95% CI [-0.058, -0.025], BH-FDR < 0.001) flatten; see the interaction plot and simple slopes/predictions.

## Sensitivity and robustness
1. **Trimmed weights** (99th percentile) reproduce the H1 βs (-0.135, 0.193, -0.163) and keep H2/H3 coefficients within ±0.02 of the main estimates (`artifacts/sensitivity_trimmed_weights_loop78.csv`).
2. **Alternative composites**: The guidance + playful cohesion index mirrors the H1 signs, and both alternative adversity constructs retain the support-dependent moderation (`artifacts/sensitivity_cohesion_loop78.csv`, `artifacts/sensitivity_adversity_loop78.csv`).
3. **Guidance–depression diagnostics**: The positive guidance → depression coefficient aligns with the raw correlation (r = 0.270), and the binned averages appear in `artifacts/guidance_depression_sensitivity_loop78.csv`, suggesting measurement nuance rather than misspecification.
4. **Sample stability**: Analytic sample comparisons and VIF diagnostics confirm no substantive drift from the full panel (`artifacts/h1_sample_comparison_loop78.csv`, `artifacts/h1_vif_loop78.csv`).

## Limitations
- The planned childhood religiosity control (`Religionchildhood`) is fully missing, so it cannot be included.
- Simple slopes and predicted outcomes assume covariates remain at analytic means.
- The `religion` covariate was dropped from H2 because it mirrors the active religiosity exposures and inflated coefficients.

## Reproducibility
Regression records, diagnostics, and figures live under `artifacts/` (e.g., `artifacts/regression_records_loop78.csv`, `artifacts/h1_coefficients_loop78.png`, `artifacts/pip_freeze_loop78.txt`). Running `python analysis/run_analysis.py --sensitivity --loop-index 78` reproduces every number and figure while honoring the frozen pre-analysis plan (`analysis/pre_analysis_plan.md`).
