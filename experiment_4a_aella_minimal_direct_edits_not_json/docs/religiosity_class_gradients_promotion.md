# Religiosity Class Gradients Promotion Memo — Loop 019 *(status: draft)*

## 1. Objective
- **Goal**: Determine whether the `religiosity_class_gradients` family (moderate and serious practice × childhood class interactions on high anxiety) is ready for confirmatory status once reviewers grant approval.
- **Dataset**: `childhoodbalancedpublic_original.csv` (14,443 × 718). No survey weights/strata/cluster identifiers exist after scanning every header, so we continue to assume an SRS design; each result row records this justification.
- **Seed policy**: `PYTHONHASHSEED=20251016` (the project default) is exported before every Python call. Scripts noted below reproduce all coefficients, tables, and figures.

## 2. Estimand & Specification
- **Outcome**: `anxiety_high_flag`, coded as 1 when respondents endorse ≥5 on either anxiety prompt (npvfh98 or its aligned companion). This matches the binary specification introduced in Loop 012.
- **Exposure**: Categorical religiosity intensity split into non-practicing (reference), slight, moderate, and serious practice dummies. The confirmatory candidate focuses on the *interaction* between childhood class (`classchild`, 0–6) and (a) moderate practice, (b) serious practice.
- **Estimator**: Logistic regression `anxiety_high_flag ~ religiosity_dummies × classchild + classcurrent + classteen + selfage + gendermale + education`, executed via  
  `PYTHONHASHSEED=20251016 python scripts/loop015_h4_rich_interactions.py`.
- **Outputs**:  
  - Coefficient table `tables/loop015_h4_interactions_rich.csv`.  
  - Predicted class gradients grid `tables/loop015_h4_predicted_grid.csv` and visualization `figures/loop015_h4_classinteraction.png`.  
  - Confirmatory shell `tables/loop016_h4_confirmatory.csv` (produced with `python scripts/loop016_h4_confirmatory_tables.py`).

## 3. Evidence Snapshot
- **Moderate practice × classchild**: β = −0.130 (SE 0.052, p = 0.0116, q = 0.0232). Predicted high-anxiety probability drops from 0.504 at classchild = 0 to 0.335 at classchild = 6 (−16.9 p.p.), and the within-level contrast is −18.9 p.p. relative to non-practicing peers (`tables/loop016_h4_confirmatory.csv`).
- **Serious practice × classchild**: β = −0.086 (SE 0.066, p = 0.1942, q = 0.1942). Probability shift is −10.1 p.p. within serious practitioners and −12.1 p.p. relative to non-practitioners. Precision remains limited, so the term currently serves as a supporting contrast pending stress tests (see Section 6).
- **Alternative anxiety codings**: Loop 012’s ordinal/alternate-flag outcomes and Loop 013’s summary table (`tables/loop013_h4_outcome_effects.csv`) show congruent religiosity benefits, indicating the binary flag is not an outlier specification.

## 4. Multiplicity & Reporting Plan
- **Family**: `religiosity_class_gradients` contains up to two contrasts. If only the moderate slope is preregistered, its p-value acts as the q-value. If both contrasts enter, apply Benjamini–Hochberg at q ≤ 0.05 using the two Wald p-values from the confirmatory shell.
- **Current BH metrics** (already logged in `analysis/results.csv`):  
  - Moderate: rank 1/2 ⇒ q = 0.0116 × 2 = 0.0232.  
  - Serious: rank 2/2 ⇒ q = 0.1942 (equal to its p-value).  
- **Reporting**: `analysis/results.csv` and `tables/loop016_h4_confirmatory.csv` stay synchronized with these q-values so reproducibility reviewers can audit multiplicity without re-running models.

## 5. Literature Support
- **Mechanism**: Longitudinal high-risk cohorts find that sustained religious involvement dampens anxiety trajectories by bolstering coping resources (Kasen et al., 2014; DOI: 10.1002/da.22131).
- **Stress-era evidence**: Among chronically ill adults navigating the COVID-19 period, religious importance and positive coping lowered anxiety and supported resilience (Davis et al., 2021; DOI: 10.1037/hea0001079).
- **Class heterogeneity**: Religious practice and private prayer reduce cognitive decline primarily for modest-income Black men, implying socioeconomic gradients in the benefits of religiosity (Bruce et al., 2024; DOI: 10.1093/geroni/igae098.1596).
- These sources (recorded in `lit/evidence_map.csv`) justify a class-conditional estimand and provide citations for `reports/paper.md`.

## 6. Stress Tests & Outstanding Checks
1. **Serious practice interaction**: Evaluate shrinkage-prior (ridge/logit) versions or alternative anxiety codings (e.g., 3-bin ordinal, latent factor) to determine whether the serious slope should remain inside the confirmatory family or drop to exploratory support. Command sketch: extend `scripts/loop015_h4_rich_interactions.py` with a ridge penalty grid while holding the covariate set fixed.
2. **Outcome robustness**: Re-run the confirmatory grid using the Loop 012 ordinal outcome (`scripts/loop012_h4_alt_outcomes.py`) so reviewers can see that the moderate interaction persists beyond the binary flag.
3. **Documentation**: Once stress tests resolve, freeze the PAP with a new git tag, update `analysis/hypotheses.csv` to flip `confirmatory=TRUE` for the family, and mirror the change in `reports/paper.md`.

## 7. Privacy & Reproducibility
- All referenced tables aggregate ≥14k respondents per row, meaning Principle 2 (no public cells with n < 10) is satisfied.
- Commands, seeds, and outputs are logged in `analysis/decision_log.csv` and `notebooks/research_notebook.md`. The promotion memo itself is now part of the audit trail so reviewers can trace exactly how the family will be promoted once confirmatory criteria are met.
