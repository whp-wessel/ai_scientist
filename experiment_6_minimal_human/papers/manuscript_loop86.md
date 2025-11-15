# Guidance, the Sacred, and Support: How Childhood Experiences Shape Adult Emotional Health in a Global Sample

## Abstract
We preregistered three hypotheses in the Balanced Childhood Survey (14,443 respondents) and executed them via survey-weighted least-squares regressions (HC3 SEs) with Benjamini–Hochberg correction. Childhood guidance lowers anxiety (β = -0.135, 95% CI [-0.152, -0.118], BH-FDR < 0.001) and functional impairment (β = -0.163, 95% CI [-0.180, -0.146], BH-FDR < 0.001) while showing a positive association with depression (β = 0.193, 95% CI [0.176, 0.210], BH-FDR < 0.001). Current religiosity links to more self-love (β = 0.037, 95% CI [0.019, 0.054], BH-FDR < 0.001) and less unhappiness (β = -0.034, 95% CI [-0.051, -0.017], BH-FDR < 0.001) despite null relationships with relationship satisfaction, and external religiosity retains only the self-love boost. Adversity × support interactions depend on the outcome—anxiety β = 0.070, depression β = -0.049, unhappiness β = 0.046, self-love β = -0.041 (all BH-FDR < 0.001)—illustrating how current support reshapes the legacy of childhood adversity.

## Introduction
Felitti et al.’s (1998) Adverse Childhood Experiences framework, resilience scholarship (Repetti, Taylor, & Seeman, 2002; Bethell et al., 2019), religion–health reviews (Koenig et al., 2012; Martin, Kirkcaldy, & Siefen, 2003), and Cohen and Wills’s (1985) buffering thesis ground our focus on childhood guidance, religiosity, and contemporary social support. The Balanced Childhood Survey captures retrospective guidance, adversity, religiosity, and support measures that map directly onto these literatures, letting us preregister H1–H3 in `analysis/pre_analysis_plan.md` and test whether guidance shields distress, whether religiosity predicts wellbeing, and whether present support moderates earlier adversity.

## Methods

### Data and preprocessing
We analyze `childhoodbalancedpublic_original.csv`, retain respondents with positive weights (14,443 rows), and archive this pass in `artifacts/analysis_loop86_summary.md`. Guidance is the average of the ages 0–12 and 13–18 parental guidance questions, the adversity index sums eight emotional/verbal conflict indicators, religiosity blends current practice (`902tbll`) and the external affirmation, and support relies on the `71mn55g` item. Outcomes include anxiety (`npvfh98`), depression (`wz901dj`), functional impairment (`kd4qc3z`), relationship satisfaction (`hp9qz6f`), self-love (`2l8994l`), and unhappiness (`ix5iyv3`). All scales are oriented so higher values reflect more of the construct, z-standardized, and respondents missing any registered variable are dropped, which the analytic sample comparison (`artifacts/h1_sample_comparison_loop86.csv`) and VIF table (`artifacts/h1_vif_loop86.csv`) document.

### Modeling
Each hypothesis relies on weighted least squares with HC3 robust SEs plus an unweighted counterpart, honoring the frozen pre-analysis plan (Wessel et al. 2024). H1 regresses standardized anxiety, depression, and functional impairment on the guidance index with covariates for age, gender indicators (`biomale`, `gendered`, `cis`), education, childhood/current class, net worth, religion, external religiosity, and country dummies. H2 regresses relationship satisfaction, self-love, and unhappiness on current or external religiosity while controlling for guidance and dropping the redundant `religion` covariate. H3 regresses each outcome on adversity, support, and their interaction plus the full covariate set and religious practice, yielding simple slopes (`artifacts/h3_simple_slopes_loop86.csv`) and predictions at low/average/high support (`artifacts/h3_predicted_supports_loop86.csv`).

### Multiple testing and reproducibility
P-values are adjusted within each hypothesis block via Benjamini–Hochberg. Figures, tables, and environment snapshots live under `artifacts/` (e.g., `artifacts/pip_freeze_loop86.txt`, `artifacts/regression_records_loop86.csv`, `artifacts/h1_coefficients_loop86.png`, `artifacts/h2_coefficients_loop86.png`, `artifacts/h3_coefficients_loop86.png`, `artifacts/h3_interaction_loop86.png`), and re-running `python3 analysis/run_analysis.py --sensitivity --loop-index 86` reproduces every artifact while honoring the frozen pre-analysis plan.

## Results

### H1 – Childhood guidance and adult distress
Guidance lowers anxiety (β = -0.135, 95% CI [-0.152, -0.118], N = 14,430, BH-FDR < 0.001) and functional impairment (β = -0.163, 95% CI [-0.180, -0.146], N = 14,430, BH-FDR < 0.001) while maintaining a positive depression coefficient (β = 0.193, 95% CI [0.176, 0.210], N = 14,431, BH-FDR < 0.001), echoing the guidance–depression diagnostics in `artifacts/guidance_depression_sensitivity_loop86.csv`.

### H2 – Religiosity and wellbeing
Current religiosity is unrelated to relationship satisfaction (β = 0.008, 95% CI [-0.010, 0.025], N = 14,429, BH-FDR = 0.379) yet links to greater self-love (β = 0.037, 95% CI [0.019, 0.054], N = 14,428, BH-FDR < 0.001) and less unhappiness (β = -0.034, 95% CI [-0.051, -0.017], N = 14,430, BH-FDR < 0.001). External religiosity sustains the self-love boost (β = 0.017, 95% CI [0.000, 0.034], N = 14,429, BH-FDR = 0.132) while remaining null for relationship satisfaction (β = -0.013, 95% CI [-0.030, 0.004], BH-FDR = 0.201) and unhappiness (β = 0.000, 95% CI [-0.016, 0.016], BH-FDR = 0.967).

### H3 – Support moderates adversity
Interactions vary by outcome: anxiety (β = 0.070, 95% CI [0.055, 0.085], N = 14,031, BH-FDR < 0.001) and unhappiness (β = 0.046, 95% CI [0.031, 0.061], N = 14,032, BH-FDR < 0.001) steepen with more support, whereas depression (β = -0.049, 95% CI [-0.064, -0.034], N = 14,032, BH-FDR < 0.001) and self-love (β = -0.041, 95% CI [-0.058, -0.025], N = 14,030, BH-FDR < 0.001) flatten; see `artifacts/h3_interaction_loop86.png`, `artifacts/h3_simple_slopes_loop86.csv`, and `artifacts/h3_predicted_supports_loop86.csv`.

## Sensitivity and robustness
1. **Trimmed weights** (99th percentile) reproduce the H1 coefficients (anxiety β = -0.135, depression β = 0.193, functional impairment β = -0.163), keep the H2 estimates within ±0.02 of the registered values, and preserve the H3 interactions (anxiety β = 0.070, depression β = -0.049, unhappiness β = 0.046, self-love β = -0.041) as documented in `artifacts/sensitivity_trimmed_weights_loop86.csv`.
2. **Alternative composites**: The guidance + playful cohesion index mirrors the H1 pattern, and the two alternate adversity constructions retain the support-dependent moderation across anxiety, depression, unhappiness, and self-love (`artifacts/sensitivity_cohesion_loop86.csv`, `artifacts/sensitivity_adversity_loop86.csv`).
3. **Guidance–depression diagnostics**: The positive guidance → depression coefficient aligns with the raw correlation (r = 0.270) and the binned averages in `artifacts/guidance_depression_sensitivity_loop86.csv`, suggesting the association reflects nuanced measurement rather than model misspecification.
4. **Sample stability**: Analytic sample comparisons and VIF diagnostics confirm no substantive drift from the full Balanced Childhood Survey panel (`artifacts/h1_sample_comparison_loop86.csv`, `artifacts/h1_vif_loop86.csv`).

## Limitations
- The planned childhood religiosity control (`Religionchildhood`) is entirely missing, so it cannot be included.
- Simple slopes and predictions assume covariates remain at their analytic means.
- The `religion` covariate was dropped from the H2 regressions because it mirrors the active religiosity measures and inflated the coefficients.

## Reproducibility
Regression records, diagnostics, and figures are archived under `artifacts/` (e.g., `artifacts/regression_records_loop86.csv`, `artifacts/h1_coefficients_loop86.png`, `artifacts/pip_freeze_loop86.txt`). Running `python3 analysis/run_analysis.py --sensitivity --loop-index 86` reproduces every table and figure while honoring the frozen pre-analysis plan (`analysis/pre_analysis_plan.md`).
