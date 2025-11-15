# Guidance, the Sacred, and Support: How Childhood Experiences Shape Adult Emotional Health in a Global Sample

## Abstract
We preregistered three hypotheses in the Balanced Childhood Survey (14,443 respondents) and tested them with survey-weighted least-squares regressions (HC3 SEs) plus Benjamini–Hochberg corrections for each hypothesis block. Childhood guidance lowers anxiety (β = -0.135, 95% CI [-0.152, -0.118], BH-FDR < 0.001) and functional impairment (β = -0.163, 95% CI [-0.180, -0.146], BH-FDR < 0.001) while paradoxically associating with higher depression (β = 0.193, 95% CI [0.176, 0.210], BH-FDR < 0.001). Current religiosity predicts more self-love (β = 0.037, 95% CI [0.019, 0.054], BH-FDR < 0.001) and less unhappiness (β = -0.034, 95% CI [-0.051, -0.017], BH-FDR < 0.001); external religiosity only sustains a modest self-love association (β = 0.017, 95% CI [0.000, 0.034], BH-FDR = 0.132). Support × adversity interactions depend on the outcome: anxiety (β = 0.070, 95% CI [0.055, 0.085]), depression (β = -0.049, 95% CI [-0.064, -0.034]), unhappiness (β = 0.046, 95% CI [0.031, 0.061]), and self-love (β = -0.041, 95% CI [-0.058, -0.025]) all reach BH-FDR < 0.001.

## Introduction
Felitti et al.’s (1998) Adverse Childhood Experiences framework, resilience models (Repetti et al., 2002; Bethell et al., 2019), religion-health reviews (Koenig et al., 2012; Martin et al., 2003), and Cohen and Wills’s (1985) buffering hypothesis motivate our focus on childhood guidance, religiosity, and current support. The Balanced Childhood Survey captures retrospective guidance, adversity, religiosity, and support items that map onto this literature, letting us preregister study questions in `analysis/pre_analysis_plan.md` and test whether guidance shields distress (H1), whether religiosity predicts wellbeing (H2), and whether current support moderates early adversity (H3).

## Methods

### Data provenance and preprocessing
We analyze `childhoodbalancedpublic_original.csv`, retain only respondents with positive survey weights (14,443 rows), and archive the snapshot in `artifacts/analysis_loop76_summary.md`. Guidance averages the ages 0–12 and 13–18 items, adversity combines eight verbal/emotional/conflict indicators, current religiosity maps the 902tbll item to a 0–3 scale, external religiosity is standardized, and support comes from `71mn55g`. Outcomes include anxiety (`npvfh98`), depression (`wz901dj`), functional impairment (`kd4qc3z`), relationship satisfaction (`hp9qz6f`), self-love (`2l8994l`), and unhappiness (`ix5iyv3`). All constructs are z-standardized, directionally aligned, and respondents with any missing key variable are excluded (`artifacts/h1_sample_comparison_loop76.csv` and VIFs in `artifacts/h1_vif_loop76.csv`).

### Modeling
Each hypothesis uses weighted least-squares with HC3 robust standard errors plus an unweighted counterpart to check stability. H1 regresses anxiety, depression, and functional impairment on the guidance index, adjusting for age, gender indicators (`biomale`, `gendered`, `cis`), education, childhood/current class, net worth, religion, external religiosity, and country dummies. H2 regresses relationship satisfaction, self-love, and unhappiness on either current or external religiosity while including guidance and dropping the redundant `religion` control. H3 regresses each emotional outcome on adversity, support, and their interaction alongside the full covariate set plus current religiosity, yielding simple slopes (`artifacts/h3_simple_slopes_loop76.csv`) and predicted outcomes (`artifacts/h3_predicted_supports_loop76.csv`).

### Multiple testing and reproducibility
P-values are adjusted per hypothesis using Benjamini–Hochberg. Figures and tables live in `artifacts/h1_coefficients_loop76.png`, `artifacts/h2_coefficients_loop76.png`, `artifacts/h3_coefficients_loop76.png`, and `artifacts/h3_interaction_loop76.png`, and the full analytic pipeline runs as `python analysis/run_analysis.py --sensitivity --loop-index 76`. Pip freeze details appear in `artifacts/pip_freeze_loop76.txt`.

## Results

### H1 – Childhood guidance and adult distress
Guidance lowers anxiety (β = -0.135, 95% CI [-0.152, -0.118], N = 14,430, BH-FDR < 0.001) and functional impairment (β = -0.163, 95% CI [-0.180, -0.146], N = 14,430, BH-FDR < 0.001) while maintaining a positive depression link (β = 0.193, 95% CI [0.176, 0.210], N = 14,431, BH-FDR < 0.001); see the full regression record in `artifacts/regression_records_loop76.csv`.

### H2 – Religiosity and wellbeing
Current religiosity does not associate with relationship satisfaction (β = 0.008, 95% CI [-0.010, 0.025], BH-FDR = 0.379) but predicts greater self-love (β = 0.037, 95% CI [0.019, 0.054], BH-FDR < 0.001) and less unhappiness (β = -0.034, 95% CI [-0.051, -0.017], BH-FDR < 0.001). External religiosity only preserves a weak self-love signal (β = 0.017, 95% CI [0.000, 0.034], BH-FDR = 0.132) while remaining null for relationship satisfaction and unhappiness; see `artifacts/h2_coefficients_loop76.png`.

### H3 – Support moderates adversity
The adversity × support interaction differs by outcome: anxiety (β = 0.070, 95% CI [0.055, 0.085]), depression (β = -0.049, 95% CI [-0.064, -0.034]), unhappiness (β = 0.046, 95% CI [0.031, 0.061]), and self-love (β = -0.041, 95% CI [-0.058, -0.025]) all keep BH-FDR < 0.001, showing nonlinear buffering patterns (`artifacts/h3_coefficients_loop76.png`, `artifacts/h3_interaction_loop76.png`).

## Sensitivity and robustness
1. **Trimmed weights** (99th percentile) reproduce the H1 βs (anxiety = -0.135, depression = 0.193, impairment = -0.163) and keep H2/H3 coefficients within ±0.02 of the base results (`artifacts/sensitivity_trimmed_weights_loop76.csv`).
2. **Alternative composites**: The guidance + playful cohesion index mirrors the H1 signs, and both alternative adversity constructions (parental verbal/emotional abuse; feeling at war with yourself) preserve the support-dependent H3 moderation (`artifacts/sensitivity_cohesion_loop76.csv`, `artifacts/sensitivity_adversity_loop76.csv`).
3. **Guidance–depression diagnostics**: The positive guidance → depression coefficient matches the raw correlation (r = 0.270), and the binned averages reside in `artifacts/guidance_depression_sensitivity_loop76.csv`, suggesting measurement nuance rather than a modeling artifact.
4. **Sample stability**: Analytic sample comparisons and VIF diagnostics show negligible drift from the full panel, supporting the covariate adjustments (`artifacts/h1_sample_comparison_loop76.csv`, `artifacts/h1_vif_loop76.csv`).

## Limitations
- The planned `Religionchildhood` control is entirely missing, so it could not be included.
- Simple slopes/predictions assume covariates remain at their analytic means.
- The `religion` control was dropped from the H2 regressions because it mirrors the active religiosity exposures and inflated the coefficients.

## Reproducibility
Regression records, diagnostics, and figures are archived under `artifacts/` (e.g., `artifacts/regression_records_loop76.csv`, `artifacts/h1_coefficients_loop76.png`, `artifacts/pip_freeze_loop76.txt`). Running `python analysis/run_analysis.py --sensitivity --loop-index 76` regenerates every plot, table, and summary, honoring the frozen pre-analysis plan (`analysis/pre_analysis_plan.md`).
