# Working Manuscript — Status: Outline

## Title
**Childhood Socio-Emotional Contexts and Adult Wellbeing in the Global Flourishing Study**

## Abstract (placeholder)
We investigate how childhood socio-emotional environments (parental abuse, guidance, class position, religiosity) relate to adult mental health, self-regard, and wealth outcomes using the public balanced sample (`childhoodbalancedpublic_original.csv`). This draft documents data sources, analytic designs, and preliminary exploratory estimates; confirmatory claims will follow once the PAP is frozen.

## 1. Introduction
Childhood adversity remains a consistent predictor of adult depression and anxiety across global samples (e.g., Zhang et al., 2025). At the same time, supportive parenting buffers internalizing symptoms by reinforcing self-esteem and self-acceptance trajectories (Moore & Shell, 2017). Socioeconomic origins also shape adult wealth accumulation through persistent class-linked advantages and intergenerational transfers (Hansen, 2014). The present project leverages the balanced Global Flourishing Study (GFS) sample to jointly study these pathways, focusing on: (H1) emotional abuse → adult depression, (H2) parental guidance → adult self-love, (H3) childhood class → adult net worth, and (H4) religiosity → anxiety.

## 2. Data & Methods
- **Data**: `childhoodbalancedpublic_original.csv` (14,443 × 718). No survey weights/strata were provided after header scans, so we maintain an SRS assumption (see `analysis/pre_analysis_plan.md`).
- **Measurement**: Loop 002 extended the priority codebook to cover teen-period exposures plus adjustment covariates, with public tables under `tables/loop002_teen_covariate_numeric.csv` and `tables/loop002_teen_covariate_categorical.csv`. Loop 003 added `scripts/likert_utils.py` + `scripts/loop003_scale_audit.py`, confirming that the survey encodes *Strongly Agree = -3* for all seven-point items; all H1–H4 Likerts are now sign-flipped and z-scored before modeling (diagnostics in `tables/loop003_likert_alignment.csv`) per Sumin (2022).
- **Modeling**: The refreshed pipeline (`scripts/run_loop003_models.py`) refits OLS for H1–H2 with aligned z-scores, adds an ordered logit spanning all ten wealth brackets plus the legacy ≥$1M binary logit (H3), and introduces both OLS and binary logit religiosity→anxiety models (H4). Coefficients live in `tables/loop003_model_estimates.csv`, while key estimates propagate to `analysis/results.csv`. All models include adolescent class, age, gender, and education controls.
- **Loop 004 extensions**: `scripts/loop004_h1_diagnostics.py` sequences the H1 models (bivariate through interaction specs) and exports `tables/loop004_h1_diagnostics.csv` / `tables/loop004_h1_correlations.csv`, while `scripts/run_loop004_models.py` finalizes the ordered-logit (H3) and religiosity (H4) specifications with childhood-class × male and religiosity × classchild/male interactions (`tables/loop004_model_estimates.csv`).

## 3. Preliminary Results (Exploratory)
- The Likert orientation audit verified that all seven-point items share the *Strongly Agree = -3* convention. After sign-flipping + z-scoring, measurement is now monotonic with the literal statements (higher = more abuse/guidance/depression/self-love/anxiety).
- Childhood abuse remains negatively associated with adult depression (β = -0.08 SD, p<1e-7) after alignment, and Loop 004 diagnostics show the inverse slope already appears bivariately (β = -0.34 SD). Moderation scans reveal a positive abuse × guidance interaction (β = +0.068, p<1e-15) and a negative abuse × male interaction (β = -0.103, p<1e-10), implying the paradoxical slope is concentrated among men and mitigated when guidance is high.
- Childhood parental guidance still shows a positive association with self-love (β = 0.09 SD, p<1e-11) using aligned scores, reinforcing the protective interpretation.
- Childhood class retains a small, non-significant association in the full ordered logit once teen class is included (β = 0.025, p=0.24), while teen class dominates both the ordered and ≥$1M binary models.
- Religiosity intensity was previously inverse to anxiety, but once class-based interactions enter (`tables/loop004_model_estimates.csv`) the main effect is null while the religiosity × childhood-class interaction is negative (β = -0.021 SD, p=0.0046), suggesting religion is most protective among respondents from higher childhood classes; the male interaction remains indistinguishable from zero.

All estimates remain exploratory and subject to revision after the orientation review and PAP freeze.

## 4. Next Steps
1. Decide whether the confirmatory H1 family will emphasize the moderation effects (guidance buffering, male concentration) or collapse abuse across age windows; document the chosen estimands in the PAP before freezing.
2. Freeze/tag the PAP once the ordered-logit and religiosity interaction specs coded in `scripts/run_loop004_models.py` are accepted, then rerun the pipeline with a reproducible seed to obtain confirmatory coefficients.
3. Implement the drafted Benjamini–Hochberg plan (per `analysis/pre_analysis_plan.md`) and carry that multiplicity language into the manuscript immediately after PAP freeze.

## References
- Hansen, M. N. (2014). *Self-Made Wealth or Family Wealth? Changes in Intergenerational Wealth Mobility.* *Social Forces, 93*(2), 457–481. https://doi.org/10.1093/SF/SOU078
- Moore, L., & Shell, M. D. (2017). *The Effects of Parental Support and Self-Esteem on Internalizing Symptoms in Emerging Adulthood.* *Psi Chi Journal of Psychological Research, 22*(2), 131–140. https://doi.org/10.24839/2325-7342.JN22.2.131
- Zhang, C., Chen, J., & Lai, Y. (2025). *The mediating role of childhood emotional neglect...* *Child Abuse & Neglect.* https://doi.org/10.1016/j.chiabu.2025.107294
- Sumin, S. (2022). *The Impact of Z-Score Transformation Scaling on the Validity, Reliability, and Measurement Error of Instrument SATS-36.* *JP3I, 11*(2). https://doi.org/10.15408/jp3i.v11i2.26591
