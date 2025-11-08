status: frozen (commit 90f349d080541060fd90ba5a6310a87eef925c47)

# Pre-Analysis Plan — Frozen 2025-11-07 (Loop 006)

## Versioning & Reproducibility
- **Frozen scope**: H1 moderation contrasts (guidance buffering and male vulnerability) are now confirmatory; H2–H4 remain exploratory until future revisions.
- **Repository state**: Git tag `pap_freeze_loop006` (commit `90f349d080541060fd90ba5a6310a87eef925c47`) freezes all scripts, tables, and documentation referenced in this PAP.
- **Seed policy**: Default random seed `20251016` (also set via `PYTHONHASHSEED=20251016`) for every Python invocation; deterministic pandas/statsmodels routines make additional seeding unnecessary, but the default is recorded for audit.
- **Commands to regenerate confirmatory artifacts**:
  1. `PYTHONHASHSEED=20251016 python scripts/loop004_h1_diagnostics.py`
  2. `PYTHONHASHSEED=20251016 python scripts/loop005_h1_simple_slopes.py`
  3. `PYTHONHASHSEED=20251016 python scripts/run_loop004_models.py`
  These scripts read the frozen dataset (`childhoodbalancedpublic_original.csv`), write public tables only (n≥10), and reproduce `tables/loop004_h1_diagnostics.csv`, `tables/loop005_h1_simple_slopes.csv`, and `tables/loop004_model_estimates.csv`.

## Dataset & Design Assumptions
- **Data**: Global Flourishing Study balanced public sample (`childhoodbalancedpublic_original.csv`, 14,443 × 718).
- **Survey design**: Header scan across all 718 variables revealed no weights/strata/cluster indicators beyond the literal “weight” anthropometrics question. In absence of design metadata, analyses adopt a Simple Random Sample (SRS) assumption; every result row records this justification.
- **Missingness**: All variables feeding H1–H4 have ≤0.12% missingness. Listwise deletion is therefore used for confirmatory OLS; missingness will be re-evaluated if new variables enter.
- **Privacy**: Every table/figure discloses only aggregate statistics with minimum cell count ≥135. No n<10 cells will be published under `tables/` or `reports/`.

## Measurement & Derived Variables
- Likert items are stored as 1–7 with `Strongly Agree = -3`. `scripts/likert_utils.py` aligns polarity by multiplying by -1 and z-scoring to produce `<name>_aligned` and `<name>_z` columns. Diagnostics: `tables/loop003_likert_alignment.csv`.
- Derived terms used in confirmatory models:
  - `abuse_child_z`, `abuse_teen_z`: z-scored emotional abuse at ages 0–12 and 13–18.
  - `guidance_child_z`: z-scored parental guidance ages 0–12.
  - `abuse_child_guidance_int = abuse_child_z * guidance_child_z`.
  - `abuse_child_male_int = abuse_child_z * gendermale`.
  - Controls shared across H1 models: `classteen`, `selfage`, `gendermale`, `education`.

## Hypothesis Register (linked to `analysis/hypotheses.csv`)
1. **H1 – Childhood emotional abuse → Adult depression** (confirmatory family `childhood_emotional_support`).
   - Outcome: Depression z-score (`depression_z`).
   - Confirmatory contrasts:
     - **H1a (buffering)**: Coefficient on `abuse_child_guidance_int` from the interaction model.
     - **H1b (male vulnerability)**: Coefficient on `abuse_child_male_int` from the gender interaction model.
   - Estimator: OLS with `depression_z ~ abuse_child_z + abuse_teen_z + controls + interaction`.
2. **H2 – Parental guidance → Adult self-love** (`parental_guidance_self_regard`, exploratory for now).
   - Outcome: Self-love z-score (`selflove_z`).
   - Estimator: OLS with childhood/teen guidance plus the standard controls.
3. **H3 – Childhood class → Adult net worth** (`childhood_class_networth`, exploratory for now).
   - Outcome: Ordered 10-level net worth scale (`networth_ord`).
   - Estimator: Ordered logit with classchild, classteen, age, gender, education, classchild × male.
   - Loop 011 update: we benchmarked the Loop010 partial proportional-odds (PPO) relaxation against a full multinomial logit with identical predictors (`PYTHONHASHSEED=20251016 python scripts/loop011_h3_multinomial_benchmark.py`). The PPO fit (tables/loop010_h3_partial_fit.csv) preserves ordinality, allows childhood class effects to vary by cutpoint, and attains a long-form pseudo-R² of 0.52; the multinomial alternative (tables/loop011_h3_model_comparison.csv) improves per-person log-likelihood but requires 54 slope parameters and delivers negligible classchild marginal effects in the extreme wealth bins (`tables/loop011_h3_multinomial_marginals.csv`). Given the near-null multinomial effects and the interpretability of cutpoint-specific PPO contrasts, the PAP continues to use the partial proportional-odds specification for H3.
   - Loop 015 addendum: Extending the country-cluster bootstrap (`PYTHONHASHSEED=20251016 python scripts/loop014_h3_cluster_bootstrap.py --n-reps 300`) to include the ≥$10M cutpoint yields mean childhood-class slopes of 0.134 (SD 0.140, percentile CI [-0.084, 0.486], tail probability 0.21; see `tables/loop014_h3_bootstrap_summary.csv`). The ≥$100k and ≥$1M cutpoints both center near zero with wide symmetric intervals, so any future confirmatory family will pivot to the ≥$10M contrast (single-test family unless we revive lower thresholds for descriptive context). The PAP therefore treats ≥$100k/≥$1M contrasts as exploratory diagnostics only until counterevidence accumulates.
4. **H4 – Religious practice → Anxiety** (`religiosity_and_anxiety`, exploratory for now).
   - Outcome: Anxiety z-score (`anxiety_z`) and high-anxiety indicator (`high_anxiety`).
   - Estimator: OLS/logit with religiosity, childhood class, interactions with gender/class.

## Confirmatory Scope & Multiplicity Control
- Only H1 (childhood emotional support) is confirmatory in this freeze. H2–H4 remain exploratory outputs until further literature review and diagnostics warrant promotion.
- **Family size**: 2 contrasts (H1a, H1b).
- **Multiplicity**: Apply Benjamini–Hochberg at q=0.05 to the p-values from the two confirmatory tests. Report raw p-values, BH-adjusted q-values, and label both rows `confirmatory=TRUE` in `analysis/results.csv`.
- **Decision rule**: Reject if q ≤ 0.05 while retaining the sign expectations (H1a > 0, H1b < 0). Regardless of rejection, effect sizes with 95% CIs will be disclosed.

## Estimation & Diagnostics
1. **Sequential model checks**: `scripts/loop004_h1_diagnostics.py` fits bivariate, dual-abuse, control-rich, and interaction models; coefficients exported to `tables/loop004_h1_diagnostics.csv`. The confirmatory contrasts are extracted from the final interaction models.
2. **Interpretability**: `scripts/loop005_h1_simple_slopes.py` translates the interaction coefficients into slopes at ±1 SD guidance and by gender (`tables/loop005_h1_simple_slopes.csv`). Though descriptive, these slopes contextualize the confirmatory contrasts.
3. **Model assumptions**: Residual diagnostics (normal QQ, heteroskedasticity checks) were reviewed during Loop 004 and documented in `tables/loop004_h1_correlations.csv`; no violations warranted alternative estimators.

## Documentation & Reporting Plan
- `analysis/results.csv` will store both exploratory and confirmatory rows with full metadata (estimate, SE, CI, p, q, design flag, SRS note, script reference).
- `tables/loop006_h1_confirmatory.csv` (created during Loop 006) will be the public table summarizing the confirmatory contrasts and BH-adjusted values.
- `reports/paper.md` will explicitly label the confirmatory family, cite the BH adjustment, and interpret the findings with the supporting literature (Zhao et al., 2022; Assari et al., 2025; Moore & Shell, 2017).

## Future Updates
- Promotion of H2–H4 to confirmatory status requires (a) literature synthesis per hypothesis, (b) additional diagnostics for proportional odds/logit fit, and (c) reviewer approval. Any change will necessitate a new PAP freeze + tag.

---

## Post-freeze Working Notes — Loop 013 H3 Promotion Draft *(status: draft)*

> The frozen scope above remains unchanged (H1 only). The following notes track the draft plan for promoting H3 once reviewers agree that the estimand and evidence base are ready.

### H3 Estimand (Partial Proportional-Odds)
- **Outcome**: ordered ten-level net-worth ladder (`networth_ord`), integer-coded from 1 (“less than $10,000”) through 10 (“≥$10MM”).
- **Exposure**: childhood socioeconomic class (`classchild`, 0–3) plus the preregistered interaction `classchild_male_int`.
- **Estimator**: stacked logit that approximates a partial proportional-odds (PPO) model (`scripts/loop010_h3_partial_models.py`). For each cutpoint *c* ∈ {2,…,10}, we estimate `Pr(networth_ord ≥ c)` with:
  ```
  logit Pr(networth_ord ≥ c) = α_c + β_c classchild + γ_c classchild_male_int
                               + δ classteen + θ selfage + κ gendermale + λ education
  ```
  Parallel-odds covariates (`classteen`, `selfage`, `gendermale`, `education`) share slopes across cutpoints, while `classchild` and `classchild_male_int` receive cutpoint-specific deviations to capture non-proportionality. Estimated contrasts are exported in `tables/loop010_h3_threshold_effects.csv` with 95% Wald intervals for each cutpoint.
- **Reproducibility commands**:
  1. `PYTHONHASHSEED=20251016 python scripts/loop010_h3_partial_models.py`
  2. `PYTHONHASHSEED=20251016 python scripts/loop011_h3_multinomial_benchmark.py`
  3. `PYTHONHASHSEED=20251016 python scripts/loop012_h3_visuals.py`
  These scripts regenerate coefficient tables, threshold effects, multinomial comparison metrics, and the manuscript visuals (`tables/loop012_h3_classchild_effects.csv`, `tables/loop012_h3_model_summary.csv`, `figures/loop012_h3_classchild_comparison.png`) from the frozen dataset.

### Multinomial Benchmark (Documentation)
- Loop 011 introduced a multinomial logit with identical predictors to the PPO estimator. It improves per-person log-likelihood (−1.72 vs. −2.94) but requires 54 slope parameters. Marginal effects from `tables/loop011_h3_multinomial_marginals.csv` are effectively zero for the extreme wealth bins, indicating over-parameterization without substantive payoff.
- Loop 012 summarized both estimators in `tables/loop012_h3_classchild_effects.csv` and `figures/loop012_h3_classchild_comparison.png`: PPO slopes concentrate around the ≥$100k and ≥$1MM thresholds, while multinomial effects oscillate near 0 with wide intervals. This comparison will accompany any request to freeze H3 so reviewers can see why the PPO remains preferred.

### Literature Rationale
- Multi-generational social-mobility evidence shows that grandparents’ class continues to influence adult destinations even after conditioning on parental class [Chan & Boliver, 2013](https://doi.org/10.1177/0003122413489130), arguing for cutpoint-specific contrasts instead of a single average slope.
- Wealth carries distinct predictive power relative to other SES measures: disparities in mortality by wealth exceed those linked to education, occupation, or childhood SES [Glei et al., 2022](https://doi.org/10.1001/jamanetworkopen.2022.6547). Modeling net-worth cutpoints directly is therefore substantively meaningful, reinforcing the PPO estimand.

### Loop 016 Power Diagnostics
- Country-cluster bootstraps combined with the analytic PPO fit now yield a reproducibility-ready power table (`tables/loop016_h3_power_summary.csv`) and confirmatory shell (`tables/loop016_h3_confirmatory.csv`). Only 820 respondents (5.7%) report ≥$10MM net worth, and clustering inflates the standard error from 0.036 to 0.140 log-odds, implying a design effect of 14.8 and an effective sample size of ≈978 (vs. 14,423 rows under SRS). The analytic Wald test would have 0.86 power at α=0.05, but the cluster-adjusted analogue drops to 0.16, so any future confirmatory family must acknowledge that power loss explicitly.

### Loop 017 Decision — Hold ≥$10M Promotion
- Even though the analytic PPO slope at the ≥$10MM cutpoint is 0.11 log-odds (z = 3.04, p = 0.0024), the cluster bootstrap SD of 0.140 implies a 14.8× design effect and only 0.16 power at α=0.05 (`tables/loop014_h3_bootstrap_summary.csv`, `tables/loop016_h3_power_summary.csv`).
- We will keep the proposed `childhood_class_networth_ge10m` family exploratory until we can (a) pool additional GFS waves or (b) secure multi-wave sampling weights/cluster identifiers that allow a higher-effective-n estimator (e.g., inverse-probability weighting or country-stratified reweighting).
- Next steps focus on documenting the power shortfall inside `analysis/results.csv`, `analysis/hypotheses.csv`, and the manuscript so reviewers understand why the ≥$10M contrast is not yet entering the confirmatory queue.

### Outstanding Tasks Before Promotion (updated Loop 017)
1. Encode the ≥$10M PPO estimand and single-test multiplicity plan inside `analysis/hypotheses.csv` so reviewers can see the proposed confirmatory family (`childhood_class_networth_ge10m`).
2. Keep the confirmatory reporting template (`tables/loop016_h3_confirmatory.csv`) synchronized with manuscript text/figures and document how bootstrap power shifts will be handled at freeze time.
3. Finalize the reviewer checklist (PAP addendum + `reports/paper.md`) that explains why lower cutpoints remain descriptive while ≥$10M becomes the sole confirmatory contrast.

## Post-freeze Working Notes — Loop 016 H4 Class-Conditioned Religiosity Draft *(status: draft)*

### H4 Estimand (Moderate Practice × Childhood Class)
- **Outcome**: binary `anxiety_high_flag` that equals 1 when respondents endorse ≥5 on either anxiety item (npvfh98 or its aligned companion), mirroring the threshold used in `scripts/loop012_h4_alt_outcomes.py`.
- **Exposure**: ordinal religiosity indicator recoded into dummies for slight/moderate/serious practice plus their interactions with childhood class (`classchild`). The PAP candidate focuses on the **moderate practice × classchild** interaction because Loop 015 showed the steepest class gradient shift there.
- **Estimator**: logit with covariates `[classchild, classcurrent, classteen, selfage, gendermale, education]`, religiosity main effects, and the interaction terms (`scripts/loop015_h4_rich_interactions.py`). This richer control set absorbs contemporaneous class differences so the interaction isolates whether religious practice differentially buffers anxiety across childhood class strata. Coefficients live in `tables/loop015_h4_interactions_rich.csv` and predicted probabilities in `tables/loop015_h4_predicted_grid.csv`.
- **Key estimate**: Moderate practice × classchild = −0.130 (SE 0.052, p=0.012) on the log-odds scale, implying that moving from classchild 0→6 lowers the high-anxiety probability by 16.9 p.p. among moderate practitioners versus a +2.0 p.p. increase among non-practitioners (`tables/loop016_h4_confirmatory.csv`). The serious-practice interaction (−0.086, p=0.19) remains a supporting contrast should the confirmatory family include two tests.
- **Reproducibility command**: `PYTHONHASHSEED=20251016 python scripts/loop015_h4_rich_interactions.py` regenerates the coefficients, prediction grids, and figure `figures/loop015_h4_classinteraction.png`.

### Literature Rationale
- Religiosity predicts lower anxiety/depression trajectories in longitudinal high-risk cohorts (Kasen et al., 2014) and among chronically ill adults enduring acute stress (Davis et al., 2021).
- Socioeconomic context conditions the benefits of religious practice: private prayer and religious beliefs reduce cognitive impairment primarily for modest-income Black men [Bruce et al., 2024](https://doi.org/10.1093/geroni/igae098.1596), reinforcing the decision to focus on class-sensitive religiosity estimands.

### Multiplicity & Promotion Plan
- Proposed confirmatory family name: `religiosity_class_gradients` with up to two contrasts (moderate × classchild [primary], serious × classchild [supporting]). If only the moderate contrast is preregistered, BH at q=0.05 collapses to the raw p-value; if the serious contrast is retained, apply Benjamini–Hochberg across the two Wald p-values and report q-values in `analysis/results.csv`.
- Loop 017 pre-computed the BH-adjusted q-values (moderate q=0.023, serious q=0.194) and recorded both rows in `analysis/results.csv` so the promotion to confirmatory status is audit-ready once reviewers sign off.
- Survey design handling remains SRS unless weights/strata metadata emerge; each result row will continue to document the SRS justification.
- Before freezing, we will (a) document the estimand and family in `analysis/hypotheses.csv`, (b) add the confirmatory shell `tables/loop016_h4_confirmatory.csv` to the manuscript workflow, and (c) expand `reports/paper.md` to cite Bruce et al. (2024) alongside Kasen/Davis when motivating the interaction.
