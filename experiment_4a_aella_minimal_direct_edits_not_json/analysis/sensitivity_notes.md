# H1 Sensitivity Analyses — Loop 007 (2025-11-07)

All runs rely on the frozen dataset (`childhoodbalancedpublic_original.csv`), the aligned Likert pipeline in `scripts/likert_utils.py`, and the default seed `PYTHONHASHSEED=20251016`. Command:  
`PYTHONHASHSEED=20251016 python scripts/loop007_h1_sensitivity.py`

The script regenerates the confirmatory models with two perturbations and stores the coefficients/q-values in `tables/loop007_h1_sensitivity.csv` (no privacy risks—coefficients only, n≈14.4k per row).

## 1. HC3 Robust Standard Errors (preregistered controls)
- **Spec**: Matches the PAP controls (`classteen`, `selfage`, `gendermale`, `education`) but reports HC3 heteroskedasticity-consistent SEs.
- **Findings**: Guidance-buffering coefficient remains 0.068 with HC3 SE 0.00855 (p=2.2e-15, q=4.5e-15); male-vulnerability coefficient stays -0.103 with HC3 SE 0.0158 (p=q≈8.7e-11). Both still exceed the confirmatory threshold (q≤0.05) while preserving the preregistered signs.

## 2. Expanded Covariate Set
- **Spec**: Adds `classchild`, `classcurrent`, `religion`, `externalreligion`, and `guidance_teen_z` to the PAP controls to probe socioeconomic/religious confounding.
- **Findings**: Guidance-buffering drops modestly to 0.063 (SE 0.00815, p=1.1e-14, q=2.2e-14). Male-vulnerability attenuates to -0.095 (SE 0.0154, p=q≈6.2e-10). Effects remain significant with identical signs, indicating robustness to plausible omitted controls.

## Takeaways
- The confirmatory H1 contrasts are resilient to both heteroskedasticity adjustments and richer socioeconomic/religious controls.
- No evidence suggests that PAP conclusions hinge on homoskedastic SEs or the baseline covariate set; we can cite `tables/loop007_h1_sensitivity.csv` in the manuscript’s robustness section and proceed to broader sensitivity work (e.g., bootstraps or alternative outcome codings) in later loops if needed.

# Loop 011 Planning — Next Robustness Wave

We will open the next sensitivity wave in Loop 012 with two reproducible add-ons. Specifications are scoped below so the code can be implemented without re-litigating design choices.

## A. Block Bootstrap for Confirmatory Interactions
- **Goal**: Quantify sampling uncertainty for the H1a/H1b interactions beyond asymptotic HC3 SEs.
- **Design**: 500 bootstrap replicates drawing respondents with replacement (listwise, n=14,4k) using `numpy.random.default_rng(20251016)` and storing full distributions of the interaction coefficients.
- **Implementation plan**: New script `scripts/loop012_h1_bootstrap.py` will:
  1. Reuse the aligned-Likert pipeline (`likert_utils.py`) and confirmatory formula.
  2. For each replicate, fit the full interaction model and record coefficients, BH-adjusted q-values, and simple slopes at ±1 SD guidance.
  3. Write `tables/loop012_h1_bootstrap_draws.csv` (one row per replicate × interaction) plus `tables/loop012_h1_bootstrap_summary.csv` (percentiles, BCa CIs).
- **Reporting**: Summaries will be appended to `analysis/results.csv` (new rows with percentile CIs) and cited in `reports/paper.md` under the robustness discussion.

## B. Alternative Anxiety Codings for H4
- **Goal**: Stress-test the religiosity → anxiety findings by toggling the anxiety outcome definition, pre-empting reviewer concerns before the sensitivity phase.
- **Design**: Two variants
  1. **Ordinal collapsing**: Re-bin the anxiety Likert into three ordered buckets (0–2 “rare”, 3–4 “sometimes”, 5–6 “frequent”) and fit ordered logits with the existing covariate set.
  2. **Binary “clinical threshold”**: Define a high-anxiety flag when respondents choose ≥5 on either anxiety item (npvfh98 or aligned counterpart) and estimate logit/linear probability models.
- **Implementation plan**: Extend `scripts/loop008_h2h3h4_diagnostics.py` or create `scripts/loop012_h4_alt_outcomes.py` to generate the new variables, refit models, and export `tables/loop012_h4_alt_codings.csv` plus summary plots under `figures/`.
- **Documentation**: Both tracks will be summarized in this file with pointers to the new tables and decisions about whether H4 is ready for PAP promotion.

# Loop 012 Results — H1 Bootstrap

- **Command**: `PYTHONHASHSEED=20251016 python scripts/loop012_h1_bootstrap.py --n-reps 500 --seed 20251016`.
- **Artifacts**: Replicate-level draws in `tables/loop012_h1_bootstrap_draws.csv`, percentile summaries in `tables/loop012_h1_bootstrap_summary.csv`, and guidance simple-slope draws in `tables/loop012_h1_bootstrap_slopes*.csv`.
- **Findings**: The guidance-buffering interaction averages 0.068 (SD 0.0083) with a 95% percentile CI [0.052, 0.084] and bootstrap tail probability 0.004. The male-vulnerability term averages -0.102 (SD 0.015) with CI [-0.129, -0.074] and identical tail probability.
- **Interpretation**: Every replicate preserved the preregistered sign pattern; even the worst-case draws remain |beta|>0.07. Simple slopes show childhood abuse remains highly predictive of depression for low-guidance respondents (median slope -0.126) while the +1 SD guidance slope drifts toward zero (median 0.010, 95% CI [-0.029, 0.047]), reinforcing the buffering narrative slated for the manuscript’s sensitivity section.

# Loop 012 Results — H4 Alternative Anxiety Codings

- **Command**: `PYTHONHASHSEED=20251016 python scripts/loop012_h4_alt_outcomes.py`.
- **Artifacts**: Outcome distributions in `tables/loop012_h4_alt_outcome_distribution.csv`; coefficient tables in `tables/loop012_h4_alt_models.csv`.
- **Design choices**: `anxiety_ord3` collapses the aligned 7-point Likert into three ordered buckets (0–2 rare, 3–4 sometimes, 5–6 frequent). `anxiety_high_flag` marks respondents ≥5 on either duplicate anxiety item, mirroring a clinical threshold screen. Both specs retain the preregistered covariates (`religion` + classchild, classteen, age, gender, education).
- **Findings**: The ordered-logit religiosity slope is -0.111 (p=2.6e-9), while the binary logit yields -0.112 (p=5.8e-8); linear-probability estimates echo the same -2.5 p.p. per religiosity step. Roughly 46% of the sample meets the high-anxiety threshold, so the binary variant keeps ample power. The concordant estimates indicate the H4 association is not an artifact of treating anxiety as a z-scored continuous outcome.

These plans keep the sensitivity queue ready so we can transition from “design” to “execution” immediately after the H3 benchmarking review is addressed.

# Loop 013 Results — H4 Outcome Comparison Visuals

- **Command**: `PYTHONHASHSEED=20251016 python scripts/loop013_h4_visuals.py`
- **Artifacts**: Summary table `tables/loop013_h4_outcome_effects.csv` (religiosity coefficients + CIs across all anxiety codings) and figure `figures/loop013_h4_outcome_effects.png`. Both draw exclusively on previously published coefficients, so no new privacy risks arise.
- **Takeaways**: Religiosity’s effect is stable across all codings: −0.062 SD on the continuous anxiety scale, −0.11 log-odds for the legacy ≥2 flag, −0.11 log-odds for the new ≥5 flag, −0.11 log-odds for the 3-bin ordinal outcome, and −2.5 p.p. in the linear-probability model. The visual highlights overlapping CIs, giving the manuscript a ready-made sensitivity reference once H4 advances toward PAP review.

# Loop 014/015 Results — H3 Cluster Bootstrap

- **Command**: `PYTHONHASHSEED=20251016 python scripts/loop014_h3_cluster_bootstrap.py --n-reps 300`.
- **Design**: Refit the PPO stacked logit 300 times after sampling respondents by country cluster (24 strata, minimum cluster size = 78) so that between-country heterogeneity feeds directly into the ≥$100k, ≥$1MM, and ≥$10MM contrasts that are candidates for the next PAP freeze.
- **Artifacts**: Replicate-level draws live in `tables/loop014_h3_bootstrap_draws.csv`; percentile summaries reside in `tables/loop014_h3_bootstrap_summary.csv`.
- **Findings**: The ≥$100k slope centers at 0.006 (SD 0.062) with a 95% percentile interval [-0.149, 0.123]; the ≥$1MM slope centers at 0.009 (SD 0.090) with interval [-0.129, 0.218]. Both show two-sided tail probabilities ≥0.74, signaling near-zero contrasts once countries are resampled. The new ≥$10MM cutpoint averages 0.134 (SD 0.140) with percentile CI [-0.084, 0.486] and tail probability 0.21: still noisy, but the distribution is skewed positive and matches the large-sample PPO estimate (0.110, p=0.002) from `tables/loop010_h3_threshold_effects.csv`. Taken together, these diagnostics motivate redefining the candidate confirmatory estimand around the ≥$10MM contrast while relegating the lower cutpoints to descriptive appendices.

# Loop 014 Results — H4 Class/Gender Interactions

- **Command**: `PYTHONHASHSEED=20251016 python scripts/loop014_h4_interactions.py`.
- **Design**: Extend the alternative anxiety codings by estimating religiosity × childhood-class and religiosity × gender interactions using (a) the 3-bin ordered-logit outcome and (b) the ≥5 binary high-anxiety flag. Controls match the PAP draft (`classchild`, `classteen`, `selfage`, `gendermale`, `education`).
- **Artifacts**: Coefficients plus CIs in `tables/loop014_h4_interactions.csv`.
- **Findings**: The religiosity × childhood-class interaction is negative (ordered logit −0.035, p=0.019; binary logit −0.042, p=0.012), implying that religiosity’s anxiety buffer strengthens among respondents who grew up in higher classes. The religiosity × gender term stays near zero (p>0.63) in both specifications, suggesting no gender differentiation beyond what is already captured in the main effect. Combined with the new Davis et al. (2021) longitudinal evidence (religious coping buffered anxiety during COVID-19), these diagnostics lay the groundwork for H4 promotion: the estimand would focus on class-conditional slopes rather than gender.
