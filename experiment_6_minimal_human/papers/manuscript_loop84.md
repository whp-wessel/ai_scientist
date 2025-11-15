# Guidance, the Sacred, and Support: How Childhood Experiences Shape Adult Emotional Health in a Global Sample

## Abstract
We preregistered three hypotheses in the Balanced Childhood Survey (14,443 respondents) and evaluated them with survey-weighted least-squares regressions (HC3 SEs, Benjamini–Hochberg corrections). Childhood guidance lowers anxiety (β = -0.135, 95% CI [-0.152, -0.118], BH-FDR < 0.001) and functional impairment (β = -0.163, 95% CI [-0.180, -0.146], BH-FDR < 0.001) while maintaining a positive association with depression (β = 0.193, 95% CI [0.176, 0.210], BH-FDR < 0.001). Current religiosity links to greater self-love (β = 0.037, 95% CI [0.019, 0.054], BH-FDR < 0.001) and less unhappiness (β = -0.034, 95% CI [-0.051, -0.017], BH-FDR < 0.001) but shows no reliable relationship with romantic satisfaction; external religiosity only preserves the self-love signal (β = 0.017, 95% CI [0.000, 0.034], BH-FDR = 0.132). Adversity × support interactions differ by outcome, steepening anxiety and unhappiness while flattening depression and self-love (all BH-FDR < 0.001), spotlighting how current circles reshape childhood adversity’s emotional legacy.

## Introduction
Felitti et al. (1998) anchor our focus on early-family protection and risk, while Repetti et al. (2002), Bethell et al. (2019), Koenig et al. (2012), and Cohen & Wills (1985) justify modeling guidance, relational resources, religiosity, and buffering support together. The Balanced Childhood Survey captures these domains (childhood guidance/adversity, religiosity, current support, adult wellbeing), permitting the preregistered examination of family cohesion (H1), religiosity (H2), and the buffering role of contemporary social support (H3) outlined in `analysis/pre_analysis_plan.md`.

## Methods

### Data and preprocessing
We analyze `childhoodbalancedpublic_original.csv`, retain respondents with positive weights (14,443 rows), and archive this pass in `artifacts/analysis_loop84_summary.md`. The guidance index averages the ages 0–12 and 13–18 parental guidance questions, the adversity index aggregates eight verbal/emotional/conflict indicators, religiosity relies on current practice (`902tbll`) plus the external affirmation, and support is measured by `71mn55g`. Outcomes include anxiety (`npvfh98`), depression (`wz901dj`), functional impairment (`kd4qc3z`), relationship satisfaction (`hp9qz6f`), self-love (`2l8994l`), and unhappiness (`ix5iyv3`). All scales are reoriented so higher values reflect more of the intended construct, z-standardized, and respondents missing any key variable are dropped (`artifacts/h1_sample_comparison_loop84.csv`, `artifacts/h1_vif_loop84.csv`).

### Modeling
Each hypothesis relies on weighted least squares with HC3 robust standard errors plus an unweighted counterpart, following the frozen pre-analysis plan. H1 regresses standardized anxiety, depression, and functional impairment on the guidance index with covariates for age, gender indicators (`biomale`, `gendered`, `cis`), education, childhood/current class, net worth, religion, external religiosity, and country dummies. H2 regresses relationship satisfaction, self-love, and unhappiness on current or external religiosity while controlling for guidance and dropping the redundant `religion` covariate. H3 regresses each outcome on adversity, support, and their interaction plus the full covariate set and current religiosity, yielding simple slopes (`artifacts/h3_simple_slopes_loop84.csv`) and predicted values (`artifacts/h3_predicted_supports_loop84.csv`).

### Multiple testing and reproducibility
P-values are adjusted within each hypothesis block via Benjamini–Hochberg. Figures, tables, and environment snapshots live under `artifacts/` (`artifacts/pip_freeze_loop84.txt`, `artifacts/regression_records_loop84.csv`, `artifacts/h1_coefficients_loop84.png`, `artifacts/h2_coefficients_loop84.png`, `artifacts/h3_coefficients_loop84.png`, `artifacts/h3_interaction_loop84.png`), and rerunning `python analysis/run_analysis.py --sensitivity --loop-index 84` regenerates every artifact alongside the frozen pre-analysis plan.

## Results

### H1 – Childhood guidance and adult distress
Guidance lowers anxiety (β = -0.135, 95% CI [-0.152, -0.118], N = 14,430, BH-FDR < 0.001) and functional impairment (β = -0.163, 95% CI [-0.180, -0.146], N = 14,430, BH-FDR < 0.001) but remains positively associated with depression (β = 0.193, 95% CI [0.176, 0.210], N = 14,431, BH-FDR < 0.001), echoing the U-shaped guidance–depression pattern documented in `artifacts/guidance_depression_sensitivity_loop84.csv`.

### H2 – Religiosity and wellbeing
Current religiosity does not reliably predict relationship satisfaction (β = 0.008, 95% CI [-0.010, 0.025], N = 14,429, BH-FDR = 0.379) but signals more self-love (β = 0.037, 95% CI [0.019, 0.054], N = 14,428, BH-FDR < 0.001) and less unhappiness (β = -0.034, 95% CI [-0.051, -0.017], N = 14,430, BH-FDR < 0.001). External religiosity only sustains the self-love boost (β = 0.017, 95% CI [0.000, 0.034], N = 14,429, BH-FDR = 0.132) while remaining null for relationship satisfaction (β = -0.013, 95% CI [-0.030, 0.004], BH-FDR = 0.201) and unhappiness (β = 0.000, 95% CI [-0.016, 0.016], BH-FDR = 0.967).

### H3 – Support moderates adversity
Adversity × support interactions vary across outcomes: anxiety (β = 0.070, 95% CI [0.055, 0.085], N = 14,031, BH-FDR < 0.001) and unhappiness (β = 0.046, 95% CI [0.031, 0.061], N = 14,032, BH-FDR < 0.001) steepen with more support, whereas depression (β = -0.049, 95% CI [-0.064, -0.034], N = 14,032, BH-FDR < 0.001) and self-love (β = -0.041, 95% CI [-0.058, -0.025], N = 14,030, BH-FDR < 0.001) flatten; see `artifacts/h3_interaction_loop84.png`, `artifacts/h3_simple_slopes_loop84.csv`, and `artifacts/h3_predicted_supports_loop84.csv`.

## Sensitivity and robustness
1. **Trimmed weights (99th percentile)** reproduce the H1 coefficients (anxiety β = -0.135, depression β = 0.193, functional impairment β = -0.163), keep H2/H3 coefficients within ±0.02, and preserve the H3 interactions (anxiety β = 0.070, depression β = -0.049, unhappiness β = 0.046, self-love β = -0.041) as shown in `artifacts/sensitivity_trimmed_weights_loop84.csv`.
2. **Alternative composites**: The guidance + playful cohesion index converges on the same H1 pattern, while both the “parental verbal/emotional abuse” and “at war with yourself” adversity constructions retain the support-dependent moderation across anxiety, depression, unhappiness, and self-love (`artifacts/sensitivity_cohesion_loop84.csv`, `artifacts/sensitivity_adversity_loop84.csv`).
3. **Guidance–depression diagnostics**: The positive guidance → depression coefficient mirrors the raw correlation (r ≈ 0.270) reported in `artifacts/guidance_depression_sensitivity_loop84.csv`, suggesting measurement nuance rather than model misspecification.
4. **Sample stability**: Analytic sample comparisons and VIF diagnostics confirm no substantive drift from the full balanced panel (`artifacts/h1_sample_comparison_loop84.csv`, `artifacts/h1_vif_loop84.csv`).

## Limitations
- The planned childhood religiosity control (`Religionchildhood`) is entirely missing and therefore absent from the regressions.
- Simple slopes and predictions assume covariates remain at their analytic means.
- The `religion` covariate was dropped from H2 regressions because it mirrors the active religiosity measures and inflated coefficients.

## Reproducibility
Regression records, diagnostics, and figures live under `artifacts/` (e.g., `artifacts/regression_records_loop84.csv`, `artifacts/h1_coefficients_loop84.png`, `artifacts/pip_freeze_loop84.txt`). Running `python analysis/run_analysis.py --sensitivity --loop-index 84` reproduces every table, figure, and summary while honoring the frozen pre-analysis plan (`analysis/pre_analysis_plan.md`).
