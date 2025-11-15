# Guidance, the Sacred, and Support: How Childhood Experiences Shape Adult Emotional Health in a Global Sample

## Abstract
The Balanced Childhood Survey captures 14,443 respondents whose recollections of family climate, religiosity, and adult wellbeing coalesce into harmonized Likert constructs. We preregistered three hypotheses grounded in resilience, religion-health, and buffering literatures, then tested them with survey-aware weighted regressions (HC3 robust SEs) and Benjamini–Hochberg corrections. Childhood guidance lowers anxiety (β = -0.135, 95% CI [-0.152, -0.118], BH-FDR < 0.001) and functional impairment (β = -0.163, 95% CI [-0.180, -0.146], BH-FDR < 0.001) yet simultaneously predicts higher depression (β = 0.193, 95% CI [0.176, 0.210], BH-FDR < 0.001). Current religiosity predicts more self-love (β = 0.037, 95% CI [0.019, 0.054], BH-FDR < 0.001) and less unhappiness (β = -0.034, 95% CI [-0.051, -0.017], BH-FDR < 0.001), while the external religiosity rating only preserves a weak self-love signal (β = 0.017, 95% CI [0.000, 0.034], BH-FDR = 0.132). Support × adversity interactions vary by outcome (βs from 0.046 to -0.049, all BH-FDR < 0.001), confirming that current social support reshapes the emotional legacy of childhood adversity.

## Introduction
Felitti et al.’s (1998) Adverse Childhood Experiences framework and subsequent resilience work (Repetti, Taylor, & Seeman, 2002; Bethell et al., 2019) highlight how responsive caregiving steers adult distress trajectories, while religion-health scholarship (Koenig et al., 2012; Martin et al., 2003) identifies faith as a psychosocial resource. Cohen and Wills’s (1985) buffering model further proposes that current social support can amplify or cushion adversity’s lingering effects. The Balanced Childhood Survey includes retrospective guidance, adversity, religiosity, and support indicators, enabling a preregistered study (analysis/pre_analysis_plan.md) of whether guidance protects distress (H1), whether religiosity shapes wellbeing (H2), and whether support moderates childhood adversity (H3).

## Methods

### Data and preprocessing
We analyze `childhoodbalancedpublic_original.csv` after excluding respondents with nonpositive weights and documenting the analytic snapshot in `artifacts/analysis_loop73_summary.md`. The guidance index averages the ages 0–12 and 13–18 guidance items, the adversity index averages eight verbal/emotional abuse and conflict indicators, religiosity relies on the ordinal current practice item (`902tbll`) and the `externalreligion` follow-up, and social support uses `71mn55g`. Outcomes include anxiety (`npvfh98`), depression (`wz901dj`), functional impairment (`kd4qc3z`), relationship satisfaction (`hp9qz6f`), self-love (`2l8994l`), and unhappiness (`ix5iyv3`). All exposures and outcomes are standardized after orienting scales so higher scores denote more of the construct, and respondents with any missing key variables are dropped (sample comparison and VIF tables saved under `artifacts/h1_sample_comparison_loop73.csv` and `artifacts/h1_vif_loop73.csv`).

### Modeling
We estimated weighted least-squares regressions with HC3 robust standard errors; each weighted model has a paired unweighted counterpart to show how weighting affects inference. H1 regresses the standardized guidance index on anxiety, depression, and functional impairment, controlling for age, gender indicators (`biomale`, `gendered`, `cis`), education, class variables (`classchild`, `classteen`, `classcurrent`), net worth, religion, external religiosity, and country dummies (United States reference). H2 regresses each wellbeing outcome on either current or external religiosity, adding the guidance index but dropping the redundant `religion` covariate when it duplicates the exposure. H3 fits adversity, support, and their interaction with the full covariate set plus current religiosity, producing simple slopes and predicted values archived in `artifacts/h3_simple_slopes_loop73.csv` and `artifacts/h3_predicted_supports_loop73.csv`.

### Multiple testing and reproducibility
Benjamini–Hochberg corrections are applied within each hypothesis block to control the false discovery rate. The frozen protocol in `analysis/pre_analysis_plan.md` documents every construct derivation and covariate. `analysis/run_analysis.py --sensitivity --loop-index 73` regenerates all tables, regression records, figures, and sensitivity files—along with the package snapshot in `artifacts/pip_freeze_loop73.txt`—ensuring the workflow is fully reproducible.

## Results

### H1 – Childhood guidance and adult distress
Weighted guidance coefficients confirm lower anxiety (β = -0.135, 95% CI [-0.152, -0.118], p < 0.001, BH-FDR < 0.001) and lower functional impairment (β = -0.163, 95% CI [-0.180, -0.146], p < 0.001, BH-FDR < 0.001) yet replicate the positive depression coefficient (β = 0.193, 95% CI [0.176, 0.210], p < 0.001, BH-FDR < 0.001) across the ~14,430-person analytic sample (see `artifacts/regression_records_loop73.csv`).

### H2 – Religiosity and wellbeing
Current religiosity modestly predicts higher self-love (β = 0.037, 95% CI [0.019, 0.054], p < 0.001, BH-FDR < 0.001) and lower unhappiness (β = -0.034, 95% CI [-0.051, -0.017], p < 0.001, BH-FDR < 0.001) while remaining null for relationship satisfaction (β = 0.008, 95% CI [-0.010, 0.025], p = 0.379, BH-FDR = 0.379). External religiosity only sustains a weak self-love signal (β = 0.017, 95% CI [0.000, 0.034], p = 0.044, BH-FDR = 0.132); its relationship satisfaction and unhappiness coefficients stay indistinguishable from zero, pointing toward meaning-making over relational payoff.

### H3 – Support moderates adversity
Support × adversity interactions vary by outcome: anxiety (β = 0.070, 95% CI [0.055, 0.085], BH-FDR < 0.001) and unhappiness (β = 0.046, 95% CI [0.031, 0.061], BH-FDR < 0.001) slopes steepen with higher support, whereas depression (β = -0.049, 95% CI [-0.064, -0.034], BH-FDR < 0.001) and self-love (β = -0.041, 95% CI [-0.058, -0.025], BH-FDR < 0.001) gradients flatten. These patterns appear in the interaction figure (`artifacts/h3_coefficients_loop73.png`) and the simple slopes/predicted outcomes tables.

## Sensitivity and robustness
- Trimmed weights (capped at the 99th percentile) reproduce H1 βs (anxiety = -0.135, depression = 0.193, functional impairment = -0.163) and keep the H2/H3 coefficients within ±0.02 (`artifacts/sensitivity_trimmed_weights_loop73.csv`), reassuring that high-leverage respondents do not drive the patterns.
- Alternative cohesion/adversity composites preserve the primary signs: the guidance + playful cohesion index keeps the H1 pattern, while both the “parental verbal/emotional abuse” and “at war with yourself” constructions maintain support-dependent H3 moderation across outcomes (`artifacts/sensitivity_cohesion_loop73.csv`, `artifacts/sensitivity_adversity_loop73.csv`).
- The guidance–depression link mirrors the raw correlation (r = 0.270) and the binned means archived in `artifacts/guidance_depression_sensitivity_loop73.csv`, suggesting measurement nuance rather than a modeling artifact.
- Sample stability checks (age/gender/class comparisons and VIFs) live in `artifacts/h1_sample_comparison_loop73.csv` and `artifacts/h1_vif_loop73.csv`.

## Limitations
- The planned childhood religiosity control (`Religionchildhood`) is fully missing, so it could not be included.
- Simple slopes and predicted outcomes assume covariates remain at their analytic means, constraining external generalizability.
- The `religion` covariate was dropped from H2 models because it duplicates the active religiosity exposures and inflates coefficients.

## Reproducibility
Regression records, figures, sensitivity tables, and environmental snapshots now live under `artifacts/` (e.g., `artifacts/analysis_loop73_summary.md`, `artifacts/regression_records_loop73.csv`, `artifacts/h1_coefficients_loop73.png`, `artifacts/pip_freeze_loop73.txt`). Re-running `python analysis/run_analysis.py --sensitivity --loop-index 73` faithfully reproduces every number and figure cited here, honoring the frozen pre-analysis plan and making this release-ready paper fully transparent.
