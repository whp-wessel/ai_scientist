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
