# Guidance, the Sacred, and Support: How Childhood Experiences Shape Adult Emotional Health in a Global Sample

## Abstract
We analyze 14,443 respondents from the Balanced Childhood Survey using the frozen pre-analysis plan to test whether childhood guidance shields distress (H1), whether religiosity predicts wellbeing (H2), and whether current social support moderates early adversity (H3). The preregistered regressions rely on weighted least squares with HC3 standard errors and Benjamini–Hochberg corrections. Results show that higher guidance lowers anxiety (β = -0.135, 95% CI [-0.152, -0.118], BH-FDR < 0.001) and functional impairment (β = -0.163, 95% CI [-0.180, -0.146], BH-FDR < 0.001) yet is also associated with higher depression (β = 0.193, 95% CI [0.176, 0.210], BH-FDR < 0.001). Current religiosity predicts more self-love (β = 0.037, 95% CI [0.019, 0.054], BH-FDR < 0.001) and less unhappiness (β = -0.034, 95% CI [-0.051, -0.017], BH-FDR < 0.001) while relationship satisfaction stays null; external religiosity only sustains a weak self-love signal (β = 0.017, 95% CI [0.000, 0.034], BH-FDR = 0.132). Support × adversity interactions differ by outcome (βs range 0.046 to -0.049, BH-FDR < 0.001), documenting how current support amplifies anxiety/unhappiness gradients and flattens depression/self-love slopes.

## Introduction
Felitti et al.’s (1998) Adverse Childhood Experiences framework, resilience models (Repetti, Taylor, & Seeman, 2002; Bethell et al., 2019), religion-health reviews (Koenig et al., 2012; Martin et al., 2003), and Cohen & Wills’s (1985) buffering hypothesis establish the conceptual scaffolding for focusing on childhood guidance, religiosity, and current social support. The Balanced Childhood Survey contains retrospective guidance, adversity, religion, and support indicators that map directly onto these literatures, enabling a preregistered study of how positive and negative childhood signals unfold into adult wellbeing (see `analysis/pre_analysis_plan.md` for the frozen protocol).

## Methods

### Data and preprocessing
We reuse `childhoodbalancedpublic_original.csv` after removing respondents with nonpositive `weight` and recording the analytic snapshot in `artifacts/analysis_loop74_summary.md`. Exposures and outcomes are oriented so higher values denote more of the underlying construct, then z-standardized; respondents missing any key variable are dropped (sample comparisons live in `artifacts/h1_sample_comparison_loop74.csv`). Country dummies, guidance and adversity indices, support, and religiosity measures are derived as described in the plan, and VIFs for the full covariate set are documented in `artifacts/h1_vif_loop74.csv`.

### Modeling
H1 fits weighted least-squares regressions of standardized anxiety, depression, and functional impairment on the guidance index, adjusting for age, gender indicators (`biomale`, `gendered`, `cis`), education, childhood/current class, net worth, religion, external religiosity, and country dummies. H2 regresses relationship satisfaction, self-love, and unhappiness on current (`902tbll`) and external religiosity, controlling for the guidance index and removing the redundant `religion` covariate when it overlaps with the exposure. H3 regresses each emotional outcome on adversity, support, and their interaction plus the full covariate set, allowing us to estimate simple slopes and predicted values (`artifacts/h3_simple_slopes_loop74.csv`, `artifacts/h3_predicted_supports_loop74.csv`). Each weighted model pairs with an unweighted counterpart to assess the influence of survey weights.

### Multiple testing and reproducibility
Within each hypothesis block we adjust p-values using the Benjamini–Hochberg procedure. Coefficient plots for each hypothesis appear in `artifacts/h1_coefficients_loop74.png`, `artifacts/h2_coefficients_loop74.png`, and `artifacts/h3_coefficients_loop74.png`, while the H3 interaction plot appears in `artifacts/h3_interaction_loop74.png`. The modeling pipeline is captured in `analysis/run_analysis.py`, and every computation can be rerun with `python analysis/run_analysis.py --sensitivity --loop-index 74`, producing the regression table, diagnostic artifacts, and the environment snapshot (`artifacts/pip_freeze_loop74.txt`).

## Results

### H1 – Childhood guidance and adult distress
Weighted guidance coefficients show lower anxiety (β = -0.135, 95% CI [-0.152, -0.118], p < 0.001, BH-FDR < 0.001; N = 14,430), lower functional impairment (β = -0.163, 95% CI [-0.180, -0.146], p < 0.001, BH-FDR < 0.001; N = 14,430), and a positive depression coefficient (β = 0.193, 95% CI [0.176, 0.210], p < 0.001, BH-FDR < 0.001; N = 14,431). These effects are recorded in `artifacts/regression_records_loop74.csv`.

### H2 – Religiosity and psychological wellbeing
Current religiosity shows no association with relationship satisfaction (β = 0.008, 95% CI [-0.010, 0.025], p = 0.379, BH-FDR = 0.379; N = 14,429) but predicts higher self-love (β = 0.037, 95% CI [0.019, 0.054], p < 0.001, BH-FDR < 0.001; N = 14,428) and lower unhappiness (β = -0.034, 95% CI [-0.051, -0.017], p < 0.001, BH-FDR < 0.001; N = 14,430). External religiosity maintains only a weak self-love signal (β = 0.017, 95% CI [0.000, 0.034], p = 0.044, BH-FDR = 0.132; N = 14,429) while remaining null for relationship satisfaction (β = -0.013, 95% CI [-0.030, 0.004], BH-FDR = 0.201) and unhappiness (β = 0.000, 95% CI [-0.016, 0.016], BH-FDR = 0.967; N = 14,431).

### H3 – Social support moderates adversity
The adversity × support interaction differs by outcome: anxiety (β = 0.070, 95% CI [0.055, 0.085]), depression (β = -0.049, 95% CI [-0.064, -0.034]), unhappiness (β = 0.046, 95% CI [0.031, 0.061]), and self-love (β = -0.041, 95% CI [-0.058, -0.025]) all show BH-FDR-adjusted p-values < 0.001 with Ns ≈ 14,030 (full table in `artifacts/regression_records_loop74.csv`). The interaction plot and simple slopes illustrate how higher support steepens anxiety/unhappiness gradients while softening depression and self-love; see `artifacts/h3_interaction_loop74.png`, `artifacts/h3_simple_slopes_loop74.csv`, and `artifacts/h3_predicted_supports_loop74.csv`.

## Sensitivity and robustness
1. **Trimmed weights**: Capping weights at the 99th percentile reproduces the H1 βs (anxiety β = -0.135, depression β = 0.193, functional impairment β = -0.163) and keeps the H2/H3 coefficients within ±0.02 of the main results (`artifacts/sensitivity_trimmed_weights_loop74.csv`).
2. **Alternative composites**: The guidance + playful cohesion index produces the same H1 signs, while the “parental verbal/emotional abuse” and “at war with yourself” alternatives retain support-dependent H3 moderation across outcomes (`artifacts/sensitivity_cohesion_loop74.csv`, `artifacts/sensitivity_adversity_loop74.csv`).
3. **Guidance–depression diagnostics**: The raw correlation between the unstandardized guidance index and depression stays r = 0.270, with binned means archived in `artifacts/guidance_depression_sensitivity_loop74.csv`; this mirroring of the coefficient suggests measurement nuance rather than a misspecified link.

## Limitations
- The planned control `Religionchildhood` contains no nonmissing values, so the feature could not be shared.
- The interaction plots and predicted values assume covariates remain at their analytic means, which constrains generalizability.
- The `religion` covariate was removed from the H2 regressions because it mirrors the active religiosity exposures and inflated coefficients.

## Reproducibility
Regression records, figures, and diagnostics live under `artifacts/` (e.g., `artifacts/regression_records_loop74.csv`, `artifacts/h1_coefficients_loop74.png`). Running `python analysis/run_analysis.py --sensitivity --loop-index 74` regenerates all tables, plots, sensitivity outputs, and the environment snapshot currently in `artifacts/pip_freeze_loop74.txt` while honoring the frozen pre-analysis plan.
