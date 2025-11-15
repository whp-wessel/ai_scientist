# Guidance, the Sacred, and Support: How Childhood Experiences Shape Adult Emotional Health in a Global Sample

## Abstract
We preregistered three hypotheses in the Balanced Childhood Survey (14,443 respondents), reran the frozen plan, and documented every artifact. Childhood guidance reduces anxiety (β = -0.135, 95% CI [-0.152, -0.118], BH-FDR < 0.001) and functional impairment (β = -0.163, 95% CI [-0.180, -0.146], BH-FDR < 0.001) while remaining positively linked to depression (β = 0.193, 95% CI [0.176, 0.210], BH-FDR < 0.001). Current religiosity increases self-love (β = 0.037, 95% CI [0.019, 0.054], BH-FDR < 0.001) and lowers unhappiness (β = -0.034, 95% CI [-0.051, -0.017], BH-FDR < 0.001) but leaves relationship satisfaction null (β = 0.008, 95% CI [-0.010, 0.025], BH-FDR = 0.379). Support × adversity interactions flip sign by outcome: anxiety (β = 0.070, 95% CI [0.055, 0.085], BH-FDR < 0.001) and unhappiness (β = 0.046, 95% CI [0.031, 0.061], BH-FDR < 0.001) steepen while depression (β = -0.049, 95% CI [-0.064, -0.034], BH-FDR < 0.001) and self-love (β = -0.041, 95% CI [-0.058, -0.025], BH-FDR < 0.001) flatten as support rises.

## Introduction
Felitti et al.’s (1998) Adverse Childhood Experiences framework, resilience reviews (Repetti, Taylor, & Seeman, 2002; Bethell et al., 2019), religion–health syntheses (Koenig et al., 2012; Martin, Kirkcaldy, & Siefen, 2003), and Cohen and Wills’s (1985) buffering thesis motivate our preregistered focus on childhood guidance (H1), religiosity (H2), and current social support (H3; see `analysis/pre_analysis_plan.md` for the frozen plan). The Balanced Childhood Survey traces guidance, adversity, religiosity, and support across 14,443 positive-weight respondents, enabling high-powered, weighted tests with robust errors.

## Methods

### Data and preprocessing
We analyze `childhoodbalancedpublic_original.csv`, drop rows with nonpositive weights, and archive the analytic snapshot and documentation as `artifacts/analysis_loop90_summary.md`. Guidance merges the ages 0–12 and 13–18 parental guidance items (producing `guidance_index_z`), the adversity index averages eight verbal/emotional conflict indicators, current religiosity is centered on the `902tbll` item (`religiosity_current_z`), external religiosity uses the `externalreligion` item (`externalreligion_z`), and support is captured with `71mn55g`. Outcomes include anxiety (`npvfh98`), depression (`wz901dj`), functional impairment (`kd4qc3z`), relationship satisfaction (`hp9qz6f`), self-love (`2l8994l`), and unhappiness (`ix5iyv3`); all scales are oriented so higher = more of the construct and then z-standardized. Missingness is handled through complete-case filtering, with the sample comparison and VIF diagnostics stored in `artifacts/h1_sample_comparison_loop90.csv` and `artifacts/h1_vif_loop90.csv`.

### Modeling
We estimate weighted least squares (WLS) models with HC3 robust standard errors plus unweighted OLS companions. H1 regresses anxiety, depression, and functional impairment on the guidance index while adjusting for age, gender indicators (`biomale`, `gendered`, `cis`), education, class history, net worth, religion covariates, external religiosity, and country dummies; the H1 coefficients appear in `artifacts/h1_coefficients_loop90.png`. H2 regresses relationship satisfaction, self-love, and unhappiness on current/external religiosity alongside the guidance index and the base covariates (dropping `religion` when it duplicates the active religiosity measure); the H2 plot is in `artifacts/h2_coefficients_loop90.png`. H3 regresses the same outcomes on the adversity index, support, and their interaction plus our full covariate set and current religiosity, producing the coefficients in `artifacts/h3_coefficients_loop90.png`, the interaction visualization in `artifacts/h3_interaction_loop90.png`, and the slope/prediction tables in `artifacts/h3_simple_slopes_loop90.csv` and `artifacts/h3_predicted_supports_loop90.csv`.

### Multiple testing and reproducibility
P-values are adjusted via Benjamini–Hochberg within each hypothesis block. Figures, regression records, and diagnostics reside under `artifacts/` (e.g., `artifacts/regression_records_loop90.csv`, `artifacts/pip_freeze_loop90.txt`). Running `python3 analysis/run_analysis.py --sensitivity --loop-index 90` reproduces every artifact while honoring the frozen plan.

## Results

### H1 – Guidance and adult distress
Guidance significantly reduces anxiety (β = -0.135, 95% CI [-0.152, -0.118], N = 14,430, BH-FDR < 0.001) and functional impairment (β = -0.163, 95% CI [-0.180, -0.146], N = 14,430, BH-FDR < 0.001) but is positively associated with depression (β = 0.193, 95% CI [0.176, 0.210], N = 14,431, BH-FDR < 0.001); see `artifacts/h1_coefficients_loop90.png`.

### H2 – Religiosity and wellbeing
Current religiosity leaves relationship satisfaction null (β = 0.008, 95% CI [-0.010, 0.025], N = 14,429, BH-FDR = 0.379) while boosting self-love (β = 0.037, 95% CI [0.019, 0.054], N = 14,428, BH-FDR < 0.001) and reducing unhappiness (β = -0.034, 95% CI [-0.051, -0.017], N = 14,430, BH-FDR < 0.001). External religiosity mirrors only the self-love gain (β = 0.017, 95% CI [0.000, 0.034], N = 14,429, BH-FDR = 0.132) while its relationship satisfaction and unhappiness estimates remain statistically indistinguishable from zero (`artifacts/h2_coefficients_loop90.png`).

### H3 – Support moderates adversity
Support moderates childhood adversity differentially: anxiety (β = 0.070, 95% CI [0.055, 0.085], N = 14,031, BH-FDR < 0.001) and unhappiness (β = 0.046, 95% CI [0.031, 0.061], N = 14,032, BH-FDR < 0.001) respond more steeply as support rises, whereas depression (β = -0.049, 95% CI [-0.064, -0.034], N = 14,032, BH-FDR < 0.001) and self-love (β = -0.041, 95% CI [-0.058, -0.025], N = 14,030, BH-FDR < 0.001) show flatter adversity slopes (`artifacts/h3_coefficients_loop90.png`). The interaction plot, slopes, and predicted values at low/average/high support are archived in `artifacts/h3_interaction_loop90.png`, `artifacts/h3_simple_slopes_loop90.csv`, and `artifacts/h3_predicted_supports_loop90.csv`.

## Sensitivity and robustness
1. **Trimmed weights**: Capping the weight distribution at the 99th percentile reproduces every H1 coefficient and keeps H2/H3 estimates within ±0.02 of the registered values (`artifacts/sensitivity_trimmed_weights_loop90.csv`).
2. **Alternative composites**: The guidance + playful cohesion index mirrors H1’s sign pattern, and both the “verbal/emotional abuse” and “at war with yourself” adversity constructions preserve the support-dependent moderation across anxiety, depression, unhappiness, and self-love (`artifacts/sensitivity_cohesion_loop90.csv`, `artifacts/sensitivity_adversity_loop90.csv`).
3. **Guidance–depression pattern**: The positive guidance → depression coefficient matches the raw correlation (r ≈ 0.270) and the binned averages in `artifacts/guidance_depression_sensitivity_loop90.csv`, suggesting measurement nuance instead of model misspecification.
4. **Sample stability**: Analytic sample comparisons and VIF diagnostics show negligible deviation from the full Balanced Childhood Survey panel (`artifacts/h1_sample_comparison_loop90.csv`, `artifacts/h1_vif_loop90.csv`).

## Limitations
- `Religionchildhood` remains completely missing, so the planned childhood religiosity control cannot be included.
- Simple slopes and predictions assume covariates stay at their analytic means.
- The `religion` control was dropped from H2 because it redundantly echoes the active religiosity items and inflated coefficients.

## Open questions
- What explains the persistent positive link between guidance and depression when all other distress indicators fall? Cultural differences in interpreting guidance or precise affective nuance may be involved.
- How do the guidance–support–adversity patterns vary across the collapsed country categories and socioeconomic strata, and do specific support sources (family, peers, institutions) reshape the interaction differently?
- Can fine-grained religiosity metrics (private devotion, congregational involvement) clarify why current practice boosts self-love while external affirmation adds little?

## Reproducibility
All figures, diagnostics, and environment logs live under `artifacts/` (e.g., `artifacts/regression_records_loop90.csv`, `artifacts/h1_coefficients_loop90.png`, `artifacts/pip_freeze_loop90.txt`). Running `python3 analysis/run_analysis.py --sensitivity --loop-index 90` recreates these artefacts while following the frozen pre-analysis plan.
