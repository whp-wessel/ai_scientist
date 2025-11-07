# Working Manuscript — Status: Outline

## Title
**Childhood Socio-Emotional Contexts and Adult Wellbeing in the Global Flourishing Study**

## Abstract (placeholder)
We investigate how childhood socio-emotional environments (parental abuse, guidance, class position, religiosity) relate to adult mental health, self-regard, and wealth outcomes using the public balanced sample (`childhoodbalancedpublic_original.csv`). This draft documents data sources, analytic designs, and preliminary exploratory estimates; confirmatory claims will follow once the PAP is frozen.

## 1. Introduction
Childhood adversity remains a consistent predictor of adult depression and anxiety across global samples (e.g., Zhang et al., 2025). At the same time, supportive parenting buffers internalizing symptoms by reinforcing self-esteem and self-acceptance trajectories (Moore & Shell, 2017). Socioeconomic origins also shape adult wealth accumulation through persistent class-linked advantages and intergenerational transfers (Hansen, 2014). The present project leverages the balanced Global Flourishing Study (GFS) sample to jointly study these pathways, focusing on: (H1) emotional abuse → adult depression, (H2) parental guidance → adult self-love, (H3) childhood class → adult net worth, and (H4) religiosity → anxiety.

## 2. Data & Methods
- **Data**: `childhoodbalancedpublic_original.csv` (14,443 × 718). No survey weights/strata were provided after header scans, so we maintain an SRS assumption (see `analysis/pre_analysis_plan.md`).
- **Measurement**: Loop 002 extended the priority codebook to cover teen-period exposures plus adjustment covariates, with public tables under `tables/loop002_teen_covariate_numeric.csv` and `tables/loop002_teen_covariate_categorical.csv`. Reverse-coded items are tracked via `tables/loop002_reverse_code_check.csv`.
- **Modeling**: The prototype pipeline (`scripts/run_loop002_models.py`) fits OLS for H1–H2 and a binary logit for H3 (≥$1M net worth), exporting coefficients to `tables/loop002_model_estimates.csv` and logging summary rows in `analysis/results.csv`. All models include adolescent class, age, gender, and education controls; further robustness (ordered logit for net-worth deciles, anxiety outcome models) is queued for the next loop.

## 3. Preliminary Results (Exploratory)
- Childhood and teen parental abuse responses remain highly correlated (r=0.86) yet yield counter-intuitive negative coefficients on adult depression (-0.07 and -0.20, respectively) when coded as provided; this flags the need to reconcile Likert polarity before confirmatory testing.
- Childhood parental guidance shows a positive coefficient (0.085) on self-love, but raw scales appear inverted relative to theoretical expectations, reinforcing the measurement-audit priority.
- Childhood class has near-zero association with the ≥$1M wealth indicator once controlling for teen class, age, gender, and education; teen class absorbs most predictive power (log-odds 0.43).
- Anxiety reverse-code checks confirm that the `npvfh98` “-neg” column is aligned with worse mental health, so no additional flipping is required for H4.

All estimates remain exploratory and subject to revision after the orientation review and PAP freeze.

## 4. Next Steps
1. Resolve Likert directionality so “higher” scores monotonically reflect greater exposure/outcome intensity; update tables/models accordingly.
2. Expand the H3 specification to ordered logits across all ten wealth brackets and add H4 anxiety models (OLS/logit) leveraging the religious-practice exposure.
3. Freeze the PAP (git-tag) once measurement conventions are settled, then proceed to confirmatory estimation.

## References
- Hansen, M. N. (2014). *Self-Made Wealth or Family Wealth? Changes in Intergenerational Wealth Mobility.* *Social Forces, 93*(2), 457–481. https://doi.org/10.1093/SF/SOU078
- Moore, L., & Shell, M. D. (2017). *The Effects of Parental Support and Self-Esteem on Internalizing Symptoms in Emerging Adulthood.* *Psi Chi Journal of Psychological Research, 22*(2), 131–140. https://doi.org/10.24839/2325-7342.JN22.2.131
- Zhang, C., Chen, J., & Lai, Y. (2025). *The mediating role of childhood emotional neglect...* *Child Abuse & Neglect.* https://doi.org/10.1016/j.chiabu.2025.107294
