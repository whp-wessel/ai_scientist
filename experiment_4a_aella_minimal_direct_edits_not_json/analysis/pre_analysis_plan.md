status: draft

# Pre-Analysis Plan (Bootstrap Outline)

## Study Overview
- **Dataset**: `childhoodbalancedpublic_original.csv`
- **Goal**: Understand how childhood socio-emotional environments shape adult well-being (mental health, self-regard, economic security, anxiety).
- **Design note**: No survey weights/strata located; assume SRS while documenting diagnostics in the analysis phase. Will update or freeze once official design guidance arrives.

## Hypothesis Register (linked to `analysis/hypotheses.csv`)
1. **H1 – Childhood emotional abuse → Adult depression**  
   - Exposure: `during ages *0-12*: your parents verbally or emotionally abused you (mds78zu)` (Likert).  
   - Outcome: `I tend to suffer from depression (wz901dj)` (Likert).  
   - Estimand: Difference in mean depression score between top vs bottom abuse tertiles; secondary linear trend.
2. **H2 – Parental guidance → Adult self-love**  
   - Exposure: `during ages *0-12*: Your parents gave useful guidance (pqo6jmj)`.  
   - Outcome: `I love myself (2l8994l)`.  
   - Estimand: Slope from OLS of self-love on standardized guidance score with demographics as covariates.
3. **H3 – Childhood class → Adult net worth**  
   - Exposure: `When you were a child (0-12 years old), your family was (classchild)`.  
   - Outcome: `Your CURRENT net worth is closest to (nhoz8ia)` (ordered scale).  
   - Estimand: Ordered logit (primary) + linear probability of being in top two wealth brackets.
4. **H4 – Religious practice → Anxiety**  
   - Exposure: `Do you *currently* actively practice a religion? (902tbll)` / `religion`.  
   - Outcome: `I tend to suffer from anxiety (npvfh98)-neg` (reverse-coded).  
   - Estimand: Mean difference in anxiety score between current practitioners vs non-practitioners controlling for age, gender, childhood class.

_All hypotheses currently exploratory; confirmatory status will be frozen after literature + PAP refinement._

## Planned Covariates & Controls
- Demographics: age (`selfage`), gender indicators (`biomale`, `gendermale`, `cis`), education, current class (`classcurrent`).
- Childhood context: class (`classchild`, `classteen`), abuse indicators.
- Missingness strategy: document % missing per variable; default to listwise deletion for exploratory work, impute (multiple imputation chained equations) if missingness >15% during confirmatory phase.

## Survey Design & Weighting
- TODO: Search for design documentation or contact data provider.  
- Interim finding (Loop 001): automated scan of all 718 headers found no columns containing `weight`, `strata`, or `cluster` other than the literal anthropometric “weight” question, so we proceed under an SRS assumption while documenting diagnostics.  
- Fallback: justify SRS via balanced sample description (balanced panel per filename) and replicate weights absent.

## Analysis Workflow
1. Data audit + codebook reconstruction (variable labels, scales, valid ranges).
2. Feature engineering (reverse-code "-neg" items, create standardized exposures/outcomes).
3. Exploratory descriptives + correlation matrices for each hypothesis family.
4. Model estimation as listed above, with heteroskedasticity-robust SEs.
5. Multiplicity: Hypotheses grouped by thematic family for q-value control once confirmatory.

## Data Audit Status (Loop 001)
- Priority variable codebook drafted in `docs/codebook_priority.md`, referencing deterministic summaries under `tables/loop001_numeric_descriptives.csv` and `tables/loop001_categorical_counts.csv`.
- Missingness across H1–H4 variables is ≤0.12%, so listwise deletion remains defensible for exploratory work.
- Public table exports follow the n≥10 rule (smallest revealed cell = 135 respondents in the “Elite class” childhood category).

## Reproducibility Checklist
- Track commands + seeds in `analysis/decision_log.csv`.
- All scripts/notebooks run via deterministic commands logged in `notebooks/research_notebook.md`.
- Results + figures exported under `tables/` and `figures/` with n<10 suppression.

## Loop 002 Updates
- **Teen exposures + covariates**: `scripts/make_loop002_descriptives.py` exports `tables/loop002_teen_covariate_numeric.csv` and `tables/loop002_teen_covariate_categorical.csv`, documenting adolescent abuse/guidance plus the adjustment set (`classteen`, `selfage`, `education`, `gendermale`, `cis`, `classcurrent`).
- **Model prototypes**: `scripts/run_loop002_models.py` runs two OLS models (H1, H2) and one logit (H3 high-net-worth) with controls listed above, writing estimates to `tables/loop002_model_estimates.csv` and populating `analysis/results.csv` with exploratory coefficients.
- **Reverse-code audit**: `tables/loop002_reverse_code_check.csv` records that the provided anxiety item (`npvfh98)-neg`) is already aligned with worse outcomes (positive correlation with depression). Remaining Likert items show counter-intuitive signs, so the next loop will formally verify directionality before freezing the PAP.
- **Next actions before PAP freeze**: (1) resolve Likert orientation so “higher” consistently means greater risk/protection; (2) expand ordered logit specs for net-worth deciles and anxiety outcome models (H4); (3) fold the new literature (Moore & Shell, 2017; Hansen, 2014) into hypothesis justifications.

## Loop 003 Updates
- **Likert polarity resolved**: `scripts/likert_utils.py` + `scripts/loop003_scale_audit.py` show the GFS Likert coding uses *Strongly Agree = -3*. All H1–H4 items are now aligned by multiplying the raw scores by -1 and standardizing to z-scores before modeling; diagnostics live in `tables/loop003_likert_alignment.csv`.
- **Model refresh**: `scripts/run_loop003_models.py` refits H1/H2 with aligned variables, adds an ordered logit across all ten net-worth brackets (H3), and introduces both OLS and binary logit religiosity→anxiety models (H4). Estimates live in `tables/loop003_model_estimates.csv` and `analysis/results.csv` (result_ids prefixed `loop003_`).
- **Measurement citation**: Literature query `lit/queries/loop_003/query_001.json` adds Sumin (2022) to ground the rescaling/standardization choice in psychometric practice.
- **Next steps toward PAP freeze**: (1) Document any remaining scale transformations (e.g., create binary outcomes for interpretability) and lock estimands; (2) re-run ordered logit with interaction terms (e.g., gender × childhood class) expected for the confirmatory plan; (3) freeze the PAP and git-tag once estimands/commands cease changing, then mark confirmatory hypotheses.

## Loop 004 Updates
- **H1 diagnostics**: `scripts/loop004_h1_diagnostics.py` (outputs: `tables/loop004_h1_diagnostics.csv`, `tables/loop004_h1_correlations.csv`) shows the childhood-abuse coefficient stays negative even in a bivariate OLS (-0.34 SD) and in sequential models. Moderation scans reveal a positive abuse × guidance interaction and a negative abuse × male interaction, implying the unexpected sign is concentrated among men and attenuated when guidance is high.
- **Ordered-logit & religiosity specs finalized**: `scripts/run_loop004_models.py` reuses the aligned-Likert pipeline but now (a) augments the H3 ordered-logit/net-worth models with a childhood-class × male interaction and (b) adds religiosity × classchild and religiosity × male interactions to the H4 anxiety models. Estimates are stored in `tables/loop004_model_estimates.csv` and propagated to `analysis/results.csv` (result_ids prefixed `loop004_`).
- **Deterministic commands**: Reproduce the current modeling state by running `python scripts/loop004_h1_diagnostics.py` followed by `python scripts/run_loop004_models.py` from the repository root. Both scripts read the frozen dataset (`childhoodbalancedpublic_original.csv`) directly, perform in-script feature engineering, and write public tables only (n≥10 by design).
- **Multiplicity plan drafted**: See below for explicit hypothesis families and Benjamini–Hochberg (BH) control at q=0.05 wherever a family has ≥2 confirmatory tests. Exploratory rows remain labeled `confirmatory=FALSE` until we freeze/tag.

### Draft Confirmatory Families & FDR Plan
1. **Family: childhood_emotional_support (H1)**  
   - **Confirmatory contrasts (locked)**: (a) abuse × childhood guidance interaction (`abuse_child_guidance_int`) from `loop004_h1_guidance_interaction`; (b) abuse × male interaction (`abuse_child_male_int`) from `loop004_h1_gender_interaction`. The main effects for childhood/teen abuse remain exploratory until we can reconcile the unexpected sign.  
   - **Plan**: For each contrast, estimate a two-sided OLS with aligned z-scores, teen abuse, and the standard control set (classteen, selfage, gendermale, education). The confirmatory command sequence is `python scripts/loop004_h1_diagnostics.py` (fits the interaction models) followed by `python scripts/loop005_h1_simple_slopes.py` (records simple slopes that interpret the interactions). Apply Benjamini–Hochberg at q=0.05 across the two interaction tests.  
   - **Diagnostics**: `tables/loop004_h1_diagnostics.csv` supplies the coefficients and `tables/loop005_h1_simple_slopes.csv` shows that the abuse slope is -0.13 SD at low guidance/among men versus ≈0 at high guidance, aligning with the buffering (Zhao et al., 2022) and gender heterogeneity (Assari et al., 2025) literature.

2. **Family: parental_guidance_self_regard (H2)**  
   - Single confirmatory estimand: childhood guidance main effect in OLS on self-love with the same controls and teen guidance to soak shared variance.  
   - Plan: No FDR adjustment needed (family size = 1); still report two-sided p-value and 95% CI.

3. **Family: childhood_class_networth (H3)**  
   - Confirmatory estimands: (a) classchild main effect in the 10-level ordered logit; (b) classchild × gendermale interaction in the same model.  
   - Plan: Apply BH at q=0.05 across the two tests if both are retained; otherwise treat as single-test family. Binary ≥$1M logit remains exploratory robustness. Command: `python scripts/run_loop004_models.py`.

4. **Family: religiosity_and_anxiety (H4)**  
   - Confirmatory estimands: (a) religiosity main effect on anxiety z-score; (b) religiosity × classchild interaction capturing differential returns; optional (c) religiosity × male if pre-registered.  
   - Plan: Use BH at q=0.05 across included contrasts. Report both the continuous (OLS) and binary high-anxiety specifications for robustness, but only the OLS family is slated as confirmatory unless reviewers request the logit.

The PAP remains `status: draft` until we formally lock which subsets from each family will be confirmatory and git-tag the frozen commit.

## Loop 005 Updates
- **Simple-slope diagnostics**: `python scripts/loop005_h1_simple_slopes.py` consumes the aligned-interaction models and exports `tables/loop005_h1_simple_slopes.csv`, which quantifies the abuse slope at childhood guidance -1/0/+1 SD and by gender. Results confirm that guidance buffering (slope shifts from -0.13 SD at low support to +0.01 SD at +1 SD guidance) and male-specific vulnerability (slope = -0.13 SD for men vs. -0.02 SD for women) drive the paradoxical main effect.  
- **Confirmatory choice recorded**: Based on those diagnostics plus Zhao et al. (2022) and Assari et al. (2025), the PAP now locks the H1 confirmatory family to the two moderation effects only. Childhood/teen abuse main effects remain exploratory, and this decision will be cited when the PAP is frozen/tagged.  
- **Next**: Freeze/tag once the ordered-logit (H3) and religiosity (H4) specs stop changing, then rerun `scripts/run_loop004_models.py` and `scripts/loop004_h1_diagnostics.py` with a recorded seed to generate confirmatory estimates before applying BH corrections.
