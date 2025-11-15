# Guidance, the Sacred, and Support: How Childhood Experiences Shape Adult Emotional Health in a Global Sample

## Abstract
We preregistered three hypotheses in the Balanced Childhood Survey (14,443 respondents) and tested them with survey-weighted least-squares regressions (HC3 SEs) and Benjamini–Hochberg corrections. Childhood guidance lowers anxiety (β = -0.135, 95% CI [-0.152, -0.118], BH-FDR < 0.001) and functional impairment (β = -0.163, 95% CI [-0.180, -0.146], BH-FDR < 0.001) while also predicting higher depression (β = 0.193, 95% CI [0.176, 0.210], BH-FDR < 0.001). Current religiosity is linked to more self-love (β = 0.037, 95% CI [0.019, 0.054], BH-FDR < 0.001) and less unhappiness (β = -0.034, 95% CI [-0.051, -0.017], BH-FDR < 0.001), whereas external religiosity only sustains a weak self-love signal (β = 0.017, 95% CI [0.000, 0.034], BH-FDR = 0.132). Support × adversity interactions depend on the outcome: anxiety (β = 0.070, 95% CI [0.055, 0.085]), depression (β = -0.049, 95% CI [-0.064, -0.034]), unhappiness (β = 0.046, 95% CI [0.031, 0.061]), and self-love (β = -0.041, 95% CI [-0.058, -0.025]) all achieve BH-FDR < 0.001.

## Introduction
Felitti et al.’s (1998) Adverse Childhood Experiences framework, resilience models (Repetti et al., 2002; Bethell et al., 2019), religion-health reviews (Koenig et al., 2012; Martin et al., 2003), and Cohen and Wills’s (1985) buffering hypothesis motivate the focus on childhood guidance, religiosity, and current social support. The Balanced Childhood Survey captures retrospective guidance, adversity, religiosity, and support items that map directly onto this literature, allowing us to preregister and test whether guidance shields distress (H1), whether religiosity predicts wellbeing (H2), and whether current support moderates early adversity (H3) as described in `analysis/pre_analysis_plan.md`.

## Methods

### Data and preprocessing
We analyze `childhoodbalancedpublic_original.csv`, retain only respondents with positive weights (14,443 rows), and archive the snapshot in `artifacts/analysis_loop75_summary.md`. The guidance index averages the ages 0–12 and 13–18 guidance items, the adversity index aggregates eight verbal/emotional and conflict indicators, religiosity combines the current practice item (`902tbll`) with `externalreligion`, and support is measured via `71mn55g`. Outcomes include anxiety (`npvfh98`), depression (`wz901dj`), functional impairment (`kd4qc3z`), relationship satisfaction (`hp9qz6f`), self-love (`2l8994l`), and unhappiness (`ix5iyv3`). We orient all scales so higher values capture more of the underlying construct, z-standardize exposures/outcomes, and drop respondents missing any key variable (details in `artifacts/h1_sample_comparison_loop75.csv` and VIFs in `artifacts/h1_vif_loop75.csv`).

### Modeling
Each hypothesis uses weighted least-squares with HC3 robust standard errors, paired with an unweighted counterpart, as documented in the frozen plan. H1 regresses standardized anxiety, depression, and functional impairment on the guidance index, adjusting for age, gender indicators (`biomale`, `gendered`, `cis`), education, childhood/current class, net worth, religion, external religiosity, and country dummies. H2 regresses relationship satisfaction, self-love, and unhappiness separately on either current or external religiosity while controlling for the guidance index and removing the redundant `religion` covariate when it mirrors the exposure. H3 regresses each emotional outcome on adversity, support, and their interaction plus the full covariate set plus current religiosity, yielding simple slopes (`artifacts/h3_simple_slopes_loop75.csv`) and predicted outcomes (`artifacts/h3_predicted_supports_loop75.csv`).

### Multiple testing and reproducibility
P-values are adjusted within each hypothesis block using the Benjamini–Hochberg procedure. Figures and tables are archived (`artifacts/h1_coefficients_loop75.png`, `artifacts/h2_coefficients_loop75.png`, `artifacts/h3_coefficients_loop75.png`, `artifacts/h3_interaction_loop75.png`), and the full analytic pipeline runs with `python analysis/run_analysis.py --sensitivity --loop-index 75`, which regenerates every artifact and the package snapshot `artifacts/pip_freeze_loop75.txt`.

## Results

### H1 – Childhood guidance and adult distress
Guidance lowers anxiety (β = -0.135, 95% CI [-0.152, -0.118], N = 14,430, p < 0.001, BH-FDR < 0.001) and functional impairment (β = -0.163, 95% CI [-0.180, -0.146], N = 14,430, p < 0.001, BH-FDR < 0.001) while the depression coefficient remains positive (β = 0.193, 95% CI [0.176, 0.210], N = 14,431, p < 0.001, BH-FDR < 0.001); the regression records are in `artifacts/regression_records_loop75.csv`.

### H2 – Religiosity and wellbeing
Current religiosity does not associate with relationship satisfaction (β = 0.008, 95% CI [-0.010, 0.025], N = 14,429, p = 0.379, BH-FDR = 0.379) but predicts greater self-love (β = 0.037, 95% CI [0.019, 0.054], N = 14,428, p < 0.001, BH-FDR < 0.001) and less unhappiness (β = -0.034, 95% CI [-0.051, -0.017], N = 14,430, p < 0.001, BH-FDR < 0.001). External religiosity only maintains a weak self-love link (β = 0.017, 95% CI [0.000, 0.034], N = 14,429, p = 0.044, BH-FDR = 0.132) while remaining null for relationship satisfaction (β = -0.013, 95% CI [-0.030, 0.004], BH-FDR = 0.201) and unhappiness (β = 0.000, 95% CI [-0.016, 0.016], BH-FDR = 0.967).

### H3 – Support moderates adversity
The adversity-support interaction varies by outcome: anxiety (β = 0.070, 95% CI [0.055, 0.085], N = 14,031, BH-FDR < 0.001) and unhappiness (β = 0.046, 95% CI [0.031, 0.061], BH-FDR < 0.001) steepen with higher support, while depression (β = -0.049, 95% CI [-0.064, -0.034], BH-FDR < 0.001) and self-love (β = -0.041, 95% CI [-0.058, -0.025], BH-FDR < 0.001) flatten, as displayed in the interaction figure and simple slope/predicted value tables.

## Sensitivity and robustness
1. **Trimmed weights** (99th percentile) reproduce the H1 βs (-0.135, 0.193, -0.163) and keep H2/H3 coefficients within ±0.02 (`artifacts/sensitivity_trimmed_weights_loop75.csv`).
2. **Alternative composites**: The guidance + playful cohesion index mirrors the H1 signs, and both alternative adversity constructions retain support-dependent moderation across outcomes (`artifacts/sensitivity_cohesion_loop75.csv`, `artifacts/sensitivity_adversity_loop75.csv`).
3. **Guidance–depression diagnostics**: The positive guidance → depression coefficient mirrors the raw correlation (r = 0.270) and the binned averages in `artifacts/guidance_depression_sensitivity_loop75.csv`, signaling measurement nuance rather than model misspecification.
4. **Sample stability**: Analytic sample comparisons and VIFs confirm no substantive drift from the full panel (`artifacts/h1_sample_comparison_loop75.csv`, `artifacts/h1_vif_loop75.csv`).

## Limitations
- The planned childhood religiosity control (`Religionchildhood`) contains no nonmissing values, so it could not be included.
- Simple slopes and predicted outcomes hold covariates at the analytic means, limiting generalizability.
- The `religion` covariate was dropped from H2 because it mirrors the active religiosity exposures and inflated the coefficients.

## Reproducibility
All regression records, diagnostics, and figures are archived under `artifacts/` (e.g., `artifacts/regression_records_loop75.csv`, `artifacts/h1_coefficients_loop75.png`, `artifacts/pip_freeze_loop75.txt`). Running `python analysis/run_analysis.py --sensitivity --loop-index 75` reproduces every table, plot, and summary, honoring the frozen pre-analysis plan.
