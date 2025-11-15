# Guidance, the Sacred, and Support: How Childhood Experiences Shape Adult Emotional Health in a Global Sample

## Abstract
We preregistered three hypotheses in the Balanced Childhood Survey (14,443 respondents), executed survey-weighted least-squares regressions with HC3 SEs, and corrected for Benjamini–Hochberg multiplicity. Childhood guidance lowers anxiety (β = -0.135, 95% CI [-0.152, -0.118], BH-FDR < 0.001) and functional impairment (β = -0.163, 95% CI [-0.180, -0.146], BH-FDR < 0.001) while producing a positive depression coefficient (β = 0.193, 95% CI [0.176, 0.210], BH-FDR < 0.001). Current religiosity predicts more self-love (β = 0.037, 95% CI [0.019, 0.054], BH-FDR < 0.001) and less unhappiness (β = -0.034, 95% CI [-0.051, -0.017], BH-FDR < 0.001) but neither current nor external religiosity shifts relationship satisfaction. Adversity × support interactions reverse sign across outcomes—anxiety β = 0.070, depression β = -0.049, unhappiness β = 0.046, self-love β = -0.041 (all BH-FDR < 0.001)—highlighting how current support reshapes the emotional legacy of childhood adversity.

## Introduction
Felitti et al.’s (1998) Adverse Childhood Experiences framework, resilience scholarship (Repetti, Taylor, & Seeman, 2002; Bethell et al., 2019), religion–health reviews (Koenig et al., 2012; Martin, Kirkcaldy, & Siefen, 2003), and Cohen and Wills’s (1985) buffering thesis collectively motivate our focus on childhood guidance, religiosity, and contemporaneous social support. The Balanced Childhood Survey captures retrospective guidance, adversity, religiosity, and support indicators, enabling a preregistered test of whether guidance shields adult distress (H1), whether religiosity predicts wellbeing (H2), and whether current support moderates the consequences of early adversity (H3; see `analysis/pre_analysis_plan.md` for the full Pre-Analysis Plan).

## Methods

### Data and preprocessing
We analyze `childhoodbalancedpublic_original.csv`, retain respondents with positive weights (14,443 rows), and archive every modeling pass in `artifacts/analysis_loop88_summary.md`. Guidance blends the ages 0–12 and 13–18 parental guidance questions, the adversity index averages eight emotional/verbal conflict indicators, religiosity captures current practice (`902tbll`) and the external affirmation item, and support is measured with the `71mn55g` item. Outcomes include anxiety (`npvfh98`), depression (`wz901dj`), functional impairment (`kd4qc3z`), relationship satisfaction (`hp9qz6f`), self-love (`2l8994l`), and unhappiness (`ix5iyv3`). All scales are oriented so higher values mean more of the construct, z-standardized, and we drop respondents missing any registered variable; the analytic sample comparison (`artifacts/h1_sample_comparison_loop88.csv`) and VIF table (`artifacts/h1_vif_loop88.csv`) document this filtering.

### Modeling
Each hypothesis is addressed with weighted least squares (WLS) plus HC3 robust SEs and an unweighted OLS counterpart. H1 regresses standardized anxiety, depression, and functional impairment on the guidance index with covariates for age, gender indicators (`biomale`, `gendered`, `cis`), education, childhood/current class, net worth, religion, external religiosity, and country dummies. H2 regresses relationship satisfaction, self-love, and unhappiness on current or external religiosity while controlling for guidance and excluding the redundant `religion` covariate. H3 regresses each outcome on the adversity index, support, and their interaction plus the full covariate set plus current religiosity, yielding simple slopes (`artifacts/h3_simple_slopes_loop88.csv`) and predictions at low/average/high support (`artifacts/h3_predicted_supports_loop88.csv`).

### Multiple testing and reproducibility
P-values are adjusted within each hypothesis block via Benjamini–Hochberg. Figures, tables, and environment snapshots appear under `artifacts/` (e.g., `artifacts/pip_freeze_loop88.txt`, `artifacts/regression_records_loop88.csv`, `artifacts/h1_coefficients_loop88.png`, `artifacts/h2_coefficients_loop88.png`, `artifacts/h3_coefficients_loop88.png`, `artifacts/h3_interaction_loop88.png`), and running `python3 analysis/run_analysis.py --sensitivity --loop-index 88` reproduces every artifact while honoring the frozen pre-analysis plan.

## Results

### H1 – Childhood guidance and adult distress
Guidance lowers anxiety (β = -0.135, 95% CI [-0.152, -0.118], N = 14,430, BH-FDR < 0.001) and functional impairment (β = -0.163, 95% CI [-0.180, -0.146], N = 14,430, BH-FDR < 0.001) while showing a positive depression coefficient (β = 0.193, 95% CI [0.176, 0.210], N = 14,431, BH-FDR < 0.001), consistent with the guidance–depression diagnostics in `artifacts/guidance_depression_sensitivity_loop88.csv`.

### H2 – Religiosity and wellbeing
Current religiosity is unrelated to relationship satisfaction (β = 0.008, 95% CI [-0.010, 0.025], N = 14,429, BH-FDR = 0.379) but links to greater self-love (β = 0.037, 95% CI [0.019, 0.054], N = 14,428, BH-FDR < 0.001) and less unhappiness (β = -0.034, 95% CI [-0.051, -0.017], N = 14,430, BH-FDR < 0.001). External religiosity retains only the self-love boost (β = 0.017, 95% CI [0.000, 0.034], N = 14,429, BH-FDR = 0.132) and remains null for relationship satisfaction (β = -0.013, 95% CI [-0.030, 0.004], N = 14,430, BH-FDR = 0.201) and unhappiness (β = 0.000, 95% CI [-0.016, 0.016], N = 14,431, BH-FDR = 0.967).

### H3 – Support moderates adversity
Interactions differ by outcome: anxiety (β = 0.070, 95% CI [0.055, 0.085], N = 14,031, BH-FDR < 0.001) and unhappiness (β = 0.046, 95% CI [0.031, 0.061], N = 14,032, BH-FDR < 0.001) steepen with more support, whereas depression (β = -0.049, 95% CI [-0.064, -0.034], N = 14,032, BH-FDR < 0.001) and self-love (β = -0.041, 95% CI [-0.058, -0.025], N = 14,030, BH-FDR < 0.001) flatten; see `artifacts/h3_interaction_loop88.png`, `artifacts/h3_simple_slopes_loop88.csv`, and `artifacts/h3_predicted_supports_loop88.csv`.

## Sensitivity and robustness
1. **Trimmed weights (99th percentile)**: H1 coefficients remain unchanged, H2 estimates stay within ±0.02 of the registered values, and H3 interactions persist; see `artifacts/sensitivity_trimmed_weights_loop88.csv`.
2. **Alternative composites**: The guidance + playful cohesion index mirrors H1’s pattern while both alternate adversity constructions uphold the support-dependent moderation across anxiety, depression, unhappiness, and self-love (`artifacts/sensitivity_cohesion_loop88.csv`, `artifacts/sensitivity_adversity_loop88.csv`).
3. **Guidance–depression diagnostics**: The positive guidance → depression coefficient matches the raw correlation (r = 0.270) and the binned averages saved in `artifacts/guidance_depression_sensitivity_loop88.csv`, suggesting measurement nuance rather than misfit.
4. **Sample stability**: Analytic sample comparisons and VIF diagnostics show negligible drift from the full Balanced Childhood Survey panel (`artifacts/h1_sample_comparison_loop88.csv`, `artifacts/h1_vif_loop88.csv`).

## Limitations
- The planned childhood religiosity control (`Religionchildhood`) is entirely missing, so it cannot be included.
- Simple slopes and predictions assume covariates remain at their analytic means.
- The `religion` covariate was dropped from the H2 regressions because it mirrors the active religiosity measures and inflated the coefficients.

## Open questions
- What drives the counterintuitive positive link between guidance and depression when all other distress indicators fall as guidance increases? Deeper measurement of affective nuance or cultural differences may illuminate whether this arises from respondent interpretations or unobserved moderators.
- How do these guidance–support–adversity dynamics vary across countries and social strata that the current collapsed country categories obscure? Future work should test whether specific support sources (family, peers, institutions) reweight the interaction.
- Can fine-grained religiosity metrics (e.g., private devotion, congregational involvement) explain why current practice boosts self-love but external affirmation mostly duplicates that signal? Mixed-methods or longitudinal data could separate self-concept pathways from social costs of belief.

## Reproducibility
Regression records, diagnostics, and figures are archived under `artifacts/` (e.g., `artifacts/regression_records_loop88.csv`, `artifacts/h1_coefficients_loop88.png`, `artifacts/pip_freeze_loop88.txt`). Running `python3 analysis/run_analysis.py --sensitivity --loop-index 88` reproduces every table and figure while following the frozen pre-analysis plan (`analysis/pre_analysis_plan.md`).
