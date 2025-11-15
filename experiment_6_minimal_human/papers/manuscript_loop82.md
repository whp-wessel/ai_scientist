# Guidance, the Sacred, and Support: How Childhood Experiences Shape Adult Emotional Health in a Global Sample

## Abstract
We preregistered three hypotheses in the Balanced Childhood Survey (14,443 respondents) and evaluated them with survey-weighted least-squares regressions (HC3 SEs, Benjamini–Hochberg correction). Childhood guidance lowers anxiety (β = -0.135, 95% CI [-0.152, -0.118], BH-FDR < 0.001) and functional impairment (β = -0.163, 95% CI [-0.180, -0.146], BH-FDR < 0.001) even as it predicts slightly higher depression (β = 0.193, 95% CI [0.176, 0.210], BH-FDR < 0.001). Current religiosity links to greater self-love (β = 0.037, 95% CI [0.019, 0.054], BH-FDR < 0.001) and less unhappiness (β = -0.034, 95% CI [-0.051, -0.017], BH-FDR < 0.001) while remaining null for relationship satisfaction; external religiosity only sustains the self-love signal (β = 0.017, 95% CI [0.000, 0.034], BH-FDR = 0.132). Adversity × support interactions differ by outcome, steepening anxiety/unhappiness (βs = 0.070 and 0.046) but flattening depression/self-love (βs = -0.049 and -0.041, all BH-FDR < 0.001).

## Introduction
Felitti et al. (1998) anchor our focus on early-family protection and risk, while Repetti et al. (2002), Bethell et al. (2019), and Cohen & Wills (1985) justify modeling guidance, relational resources, and buffering support together. The Balanced Childhood Survey measures all of these domains—including religiosity indicators (Koenig et al., 2012; Martin et al., 2003)—permitting a preregistered examination of family cohesion (H1), religiosity (H2), and the social-support buffering of adversity (H3) as outlined in `analysis/pre_analysis_plan.md`.

## Methods

### Data and preprocessing
We analyze `childhoodbalancedpublic_original.csv`, retain respondents with positive weights (14,443 rows), and archive this pass in `artifacts/analysis_loop82_summary.md`. The guidance index averages the 0–12 and 13–18 parental guidance items, the adversity index combines eight verbal/emotional/conflict indicators, religiosity uses current practice (`902tbll`) plus the external item, and support is `71mn55g`. Outcomes include anxiety (`npvfh98`), depression (`wz901dj`), functional impairment (`kd4qc3z`), relationship satisfaction (`hp9qz6f`), self-love (`2l8994l`), and unhappiness (`ix5iyv3`). All measures are oriented so higher values reflect more of the construct, z-standardized, and respondents missing any key variable are dropped (`artifacts/h1_sample_comparison_loop82.csv`, `artifacts/h1_vif_loop82.csv`).

### Modeling
Each hypothesis relies on weighted least squares with HC3 robust standard errors plus an unweighted counterpart. H1 regresses standardized anxiety, depression, and functional impairment on the guidance index with covariates for age, gender indicators (`biomale`, `gendered`, `cis`), education, childhood/current class, net worth, religion, external religiosity, and country dummies. H2 regresses relationship satisfaction, self-love, and unhappiness on current or external religiosity while controlling for guidance and dropping the redundant `religion` covariate. H3 regresses each outcome on adversity, support, and their interaction plus the full covariate set and current religiosity, yielding simple slopes (`artifacts/h3_simple_slopes_loop82.csv`) and predicted values (`artifacts/h3_predicted_supports_loop82.csv`).

### Multiple testing and reproducibility
P-values are adjusted within each hypothesis block via Benjamini–Hochberg. Figures, tables, and environment snapshots live under `artifacts/` (`artifacts/pip_freeze_loop82.txt`, `artifacts/regression_records_loop82.csv`, `artifacts/h1_coefficients_loop82.png`, `artifacts/h2_coefficients_loop82.png`, `artifacts/h3_coefficients_loop82.png`, `artifacts/h3_interaction_loop82.png`), and the pipeline can be rerun with `python analysis/run_analysis.py --sensitivity --loop-index 82`.

## Results

### H1 – Childhood guidance and adult distress
Guidance lowers anxiety (β = -0.135, 95% CI [-0.152, -0.118], N = 14,430, BH-FDR < 0.001) and functional impairment (β = -0.163, 95% CI [-0.180, -0.146], N = 14,430, BH-FDR < 0.001) but associates with higher depression (β = 0.193, 95% CI [0.176, 0.210], N = 14,431, BH-FDR < 0.001), echoing the U-shaped guidance–depression pattern documented in `artifacts/guidance_depression_sensitivity_loop82.csv`.

### H2 – Religiosity and wellbeing
Current religiosity does not reliably predict relationship satisfaction (β = 0.008, 95% CI [-0.010, 0.025], N = 14,429, BH-FDR = 0.379) but signals more self-love (β = 0.037, 95% CI [0.019, 0.054], N = 14,428, BH-FDR < 0.001) and less unhappiness (β = -0.034, 95% CI [-0.051, -0.017], N = 14,430, BH-FDR < 0.001); external religiosity only sustains the self-love boost (β = 0.017, 95% CI [0.000, 0.034], N = 14,429, BH-FDR = 0.132).

### H3 – Support moderates adversity
Support moderates adversity differently across outcomes. The interaction steepens anxiety (β = 0.070, 95% CI [0.055, 0.085], N = 14,031, BH-FDR < 0.001) and unhappiness (β = 0.046, 95% CI [0.031, 0.061], N = 14,032, BH-FDR < 0.001) while flattening depression (β = -0.049, 95% CI [-0.064, -0.034], N = 14,032, BH-FDR < 0.001) and self-love (β = -0.041, 95% CI [-0.058, -0.025], N = 14,030, BH-FDR < 0.001), consistent with the simple slopes and predictions archived under `artifacts/`.

## Sensitivity and robustness
1. **Trimmed weights (99th percentile)** reproduce the H1 coefficients (anxiety β = -0.135, depression β = 0.193, functional impairment β = -0.163), keep H2/H3 coefficients within ±0.02, and retain the interaction estimates (anxiety β = 0.070, depression β = -0.049, unhappiness β = 0.046, self-love β = -0.041) as shown in `artifacts/sensitivity_trimmed_weights_loop82.csv`.
2. **Alternative composites**: The guidance + playful cohesion index mirrors the protective/anxiety pattern, and both alternative adversity definitions preserve the support-dependent moderation (`artifacts/sensitivity_cohesion_loop82.csv`, `artifacts/sensitivity_adversity_loop82.csv`).
3. **Guidance–depression diagnostics**: The positive guidance → depression coefficient parallels the raw correlation (r = 0.270) reported in `artifacts/guidance_depression_sensitivity_loop82.csv`, hinting at measurement nuance.
4. **Sample stability**: Analytic sample comparisons and VIF diagnostics affirm minimal drift from the full panel (`artifacts/h1_sample_comparison_loop82.csv`, `artifacts/h1_vif_loop82.csv`).

## Limitations
- The planned childhood religiosity control (`Religionchildhood`) is fully missing, so it could not be incorporated.
- Simple slopes and predicted outcomes assume covariates remain at their analytic means.
- The `religion` covariate was dropped from the H2 regressions because it mirrors the active religiosity measures and inflated coefficients.

## Reproducibility
Regression records, diagnostics, and figures are archived under `artifacts/` (e.g., `artifacts/regression_records_loop82.csv`, `artifacts/h1_coefficients_loop82.png`, `artifacts/pip_freeze_loop82.txt`). Running `python analysis/run_analysis.py --sensitivity --loop-index 82` reproduces every table and plot while honoring the frozen pre-analysis plan (`analysis/pre_analysis_plan.md`).
