# Pre-Analysis Plan
status: frozen
registry_url: https://github.com/whp-wessel/ai_scientist/blob/main/analysis/pre_analysis_plan.md
freeze_commit: pending

## 1. Research context and dataset
- **Dataset**: `childhoodbalancedpublic_original.csv` (14,443 respondents, 718 columns). `analysis/literature_descriptives.py` will be rerun at the start of every analytical pass; its logging output (sample size, geography, scale means, response distributions) will be archived beside the code to document the snapshot tied to this plan.
- **Survey structure**: No explicit strata/PSUs, so the design is treated as weighted only. The continuous `weight` column (observed values such as 130, 170, 310, with a few zeros) will be filtered for `>0` and inspected for extreme percentiles before modeling. Country is captured via `What country do you live in? (4bxk14u)` and will be collapsed into the five largest groups (United States, United Kingdom, Canada, Australia, Other) with dummy coding.
- **Key constructs**: Childhood guidance (`pqo6jmj`, `dcrx5ab`), verbal/emotional abuse indicators (`mds78zu`, `v1k988q`, `wtolilk`, `gitjzck`), current social support (`71mn55g`), religiosity/practice (`902tbll`, `externalreligion`, `Religionchildhood`), adult well-being (`npvfh98`-neg, `wz901dj`, `ix5iyv3`-neg, `hp9qz6f`, `2l8994l`, `kd4qc3z`), and covariates (`selfage`, `biomale`, `gendered`, `cis`, `education`, `classchild`, `classteen`, `classcurrent`, `networth`, `religion`, `country`).
- **Documentation**: Derivations of composites (guidance index, adversity index, abuse sums, support scores) will be recorded in a dedicated notebook or script (e.g., `analysis/h1_h2_h3_model.py`) with inline comments and version-tracked parameters, ensuring the plan can be executed by rerunning the same code base.

## 2. Data preparation and reproducibility
- **Weight handling**: Rows with missing/zero/nonpositive `weight` will be dropped; the remaining sample will be used for weighted analyses while an unweighted companion model retains the same sample for comparison. The weighting vector is passed to `statsmodels.api.WLS` with `HC3` robust standard errors.
- **Missingness**: Key predictors/outcomes must all be nonmissing for the analyses. We will report the final analytic sample size and share a small table comparing respondents included vs. excluded on age, gender, and class variables to demonstrate whether complete-case analysis is biased.
- **Scaling and orientation**: Exposures and outcomes will be standardized (z-scores) after confirming that higher values consistently represent more of the construct (reverse-coded when necessary, e.g., the `-neg` items are flipped so higher = worse). Standardizing exposures supports comparisons across hypotheses; outcomes will also be standardized for effect-size interpretation.
- **Country/gender encoding**: Country dummy references will be recorded in the script (United States reference, others dummied). Gender covariates will include `biomale`, `gendered` (to capture non-binary identity), and `cis` to account for gender binarity. Female-coded responses will be the implicit reference group.
- **Environment logging**: Before each modeling run we will capture the Python environment (package versions) via `pip freeze` output stored in `artifacts/` to ensure reproducibility.

## 3. Hypotheses, variables, and estimation plan

### H1 — Childhood family cohesion shields adult emotional health
- **Statement & literature**: Higher parental guidance and family warmth across childhood predicts lower adult emotional distress (Felitti et al. 1998, _AJPM_; Repetti, Taylor, & Seeman 2002, _Psychological Bulletin_; Bethell et al. 2019, _JAMA Pediatrics_).
- **Exposure**: Guidance index = mean of `during ages *0-12*: Your parents gave useful guidance (pqo6jmj)` and `during ages *13-18*: Your parents gave useful guidance (dcrx5ab)`. The index will be standardized (mean=0, SD=1). Alternative cohesion proxies (joking/pranks `qnzuq5n`, `i1g8u4j`) remain documented for sensitivity checks but are not part of the registered index.
- **Outcomes**: Three standardized scores: `I tend to suffer from anxiety (npvfh98)-neg`, `I tend to suffer from depression (wz901dj)`, `In the past 4 weeks ... difficulty accomplishing things due to emotional issues (kd4qc3z)`. All negative-coded items will be flipped so higher = worse, keeping direction consistent.
- **Model**: Weighted least squares regressions (one per outcome) with the guidance index as the primary predictor plus controls. Robust HC3 standard errors will be computed. Each model will also be estimated without weights for sensitivity; both coefficient sets are reported.
- **Covariates**: `selfage`, `biomale`, `gendered`, `cis`, country dummies (United States reference), `education`, childhood teen and current class (`classchild`, `classteen`, `classcurrent`), `networth`, `religion`, `Religionchildhood`, and a control for `externalreligion` to partial out religiosity from the cohesive family climate.
- **Inference**: Report unstandardized coefficients (β per 1-SD increase in guidance) and standardized betas, along with 95% confidence intervals. Apply Benjamini-Hochberg false discovery rate control across the three outcomes to limit Type I error. Provide R² for each model to describe variance explained.

### H2 — Religiosity and psychological well-being in adulthood
- **Statement & literature**: Current religiosity and childhood religious emphasis predict higher relationship satisfaction, self-love, and lower unhappiness (Koenig et al. 2012, _Handbook of Religion and Health_; Martin, Kirkcaldy, & Siefen 2003, _Journal of Managerial Psychology_; Jung 2017, _Research on Aging_).
- **Exposures**: Primary exposures are `Do you *currently* actively practice a religion? (902tbll)` (ordinal scale 0 = not at all to 3 = very seriously) and `In your childhood, how important was adherence... (xvlgpp5)` aka `externalreligion`. Each exposure is treated as continuous and standardized after confirming monotonic ordering. A secondary analysis will include `Religionchildhood` categories as dummy controls to capture baseline tradition.
- **Outcomes**: Standardized scores for `I am satisfied with my romantic relationships (hp9qz6f)`, `I love myself (2l8994l)`, and flipped `I am not happy (ix5iyv3)-neg` (so higher = greater unhappiness, to be reversed back for interpretability).
- **Model**: WLS regressing each outcome on the religiosity exposure, the guidance index (from H1) to control for family climate, and the same covariates as H1. For transparency, we will estimate models with both `externalreligion` and `902tbll` separately, reporting coefficients side by side.
- **Inference**: Display β per 1-SD religiosity increase, standard errors, and 95% CI. BH-FDR adjustment runs across the three outcomes for each exposure separately (i.e., six tests total). Report both weighted and unweighted models, and highlight consistency between the two.

### H3 — Current social support buffers the lasting effects of childhood adversity
- **Statement & literature**: Perceived social support moderates the association between childhood adversity and adult wellbeing (Cohen & Wills 1985, _Psychological Bulletin_; Cobb et al. 2024, _Psychological Trauma_; Košárková et al. 2020, _Journal of Religion and Health_).
- **Exposures**: Adversity index = standardized mean of emotional abuse items (`during ages *0-12*: your parents verbally or emotionally abused you (mds78zu)`, `during ages *13-18*: ... (v1k988q)`), internal conflict items (`wtolilk`, `gitjzck`), and parental separation (`jib24si`, `o47i7yr`) if available. Scores are standardized before aggregation. Current perceived support is `In general, people in my current social circles tend to treat me really well (tmt46e6)`; for robustness the nearly identical `71mn55g` item (if available without missingness) will corroborate.
- **Outcomes**: Standardized `npvfh98`-neg, `wz901dj`, `ix5iyv3`-neg (flipped), and `I love myself (2l8994l)`. Each outcome is regressed separately but results will be presented jointly.
- **Model**: WLS with the adversity index, support score, their interaction, and the standard covariates. Both exposures are mean-centered prior to interaction to ease interpretation. Interaction terms are tested with HC3 robust SE. If the interaction is significant (p<0.05 after BH-FDR correction across the four outcomes), we will plot simple slopes at mean ±1 SD of support and report Johnson-Neyman bounds if the data supports it.
- **Covariates**: Same as H1 plus current religiosity (`902tbll`), since religiosity is a parallel coping resource; also include `Religionchildhood` to control for childhood belief contexts.
- **Inference**: Report main effects and interaction coefficient with 95% CI. BH-FDR correction applied across the four interactions (one per outcome). Provide predicted values at low/average/high support to illustrate the buffering pattern, and attach the simple slope statistics.

## 4. Robustness and sensitivity checks
- Re-estimate all models without weights to ensure that weighting does not qualitatively change directional effects.
- Replace the guidance index with its components (e.g., `pqo6jmj` alone) to ensure no single item drives results.
- For H2, rerun models with `Religionchildhood` dummies to examine whether specific traditions modulate the overall religiosity association.
- For H3, alternate the adversity index by excluding the separation indicators or including parental emotional abuse toward fathers (`cwezk1r`, `aae6xmc`) and compare coefficients. 
- Check VIFs for the final models; report any values above 5 and note whether they influence interpretation.
- If missingness on key items exceeds 20%, consider multiple imputation via chained equations as a supplementary analysis, but primary inferences remain on the complete-case sample documented above.

## 5. Reporting, transparency, and next steps
- Each hypothesis will yield a figure (coefficients + 95% CI) and table (regression outputs with N, R²) saved under `artifacts/`. Interaction plots for H3 will also be saved for direct referencing in the final paper.
- Effect sizes will be described as “β per 1-SD increase”, and the percentage of variance explained (adjusted R²) will be reported to help interpret practical significance.
- The plan will remain frozen in `analysis/pre_analysis_plan.md`; any deviations or exploratory analyses will be recorded in `analysis/notes.md` with date and rationale before the transition to the analysis phase.
