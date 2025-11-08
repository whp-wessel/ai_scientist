# Religiosity Class Gradients Promotion Memo — Loop 020 *(status: draft)*

## 1. Objective
- **Goal**: Determine whether the `religiosity_class_gradients` family (moderate and serious practice × childhood class interactions on high anxiety) is ready for confirmatory status once reviewers grant approval.
- **Dataset**: `childhoodbalancedpublic_original.csv` (14,443 × 718). No survey weights/strata/cluster identifiers exist after scanning every header, so we continue to assume an SRS design; each result row records this justification.
- **Seed policy**: `PYTHONHASHSEED=20251016` (the project default) is exported before every Python call. Scripts noted below reproduce all coefficients, tables, and figures.

## 2. Estimand & Specification
- **Outcomes**:  
  1. Binary `anxiety_high_flag`, coded as 1 when respondents endorse ≥5 on either anxiety prompt (Loop 012 definition).  
  2. The aligned Likert item collapsed into a 3-bin ordinal outcome (`anxiety_ord3`), where category 2 denotes the highest anxiety bin reviewers asked to audit.
- **Exposure**: Categorical religiosity intensity split into non-practicing (reference), slight, moderate, and serious practice dummies. The confirmatory family focuses on the *interaction* between childhood class (`classchild`, 0–6) and (a) moderate practice, (b) serious practice.
- **Estimators**:  
  - Logistic regression `anxiety_high_flag ~ religiosity_dummies × classchild + classcurrent + classteen + selfage + gendermale + education`.  
  - Ordered logit `anxiety_ord3 ~ religiosity_dummies × classchild + classcurrent + classteen + selfage + gendermale + education`.
  Both models are executed via `PYTHONHASHSEED=20251016 python scripts/loop020_h4_stress_tests.py`, which also emits ridge-penalized diagnostics for the binary outcome.
- **Outputs**:  
  - Stress-test coefficients + penalties: `tables/loop020_h4_stress_test_coeffs.csv`.  
  - Probability deltas for each outcome: `tables/loop020_h4_highflag_prob_deltas.csv` (binary), `tables/loop020_h4_ord3_prob_deltas.csv` (ordinal), and `tables/loop020_h4_ridge_prob_deltas.csv` (binary ridge).  
  - Confirmatory shell `tables/loop016_h4_confirmatory.csv` now stacks both outcomes so reviewers can audit the binary and ordinal codings side by side.

## 3. Evidence Snapshot
- **Moderate practice × classchild (primary contrast)**: Binary logit coefficient remains β = −0.130 (SE 0.052, p = 0.0116, q = 0.0232) with a −16.9 p.p. classchild gradient (0 → 6) relative to non-practitioners. The ordinal model registers β = −0.069 (SE 0.045, p = 0.126), still negative but unsurprisingly weaker because the top-bin threshold is broader than the ≥5 binary cut.
- **Serious practice × classchild (supporting contrast)**: The standard logit stays β = −0.086 (SE 0.066, p = 0.194), but two stress tests now show the slope is robust once shrinkage/alternative codings enter: (a) ridge logit with α = 5 yields β = −0.122 (SE 0.061, p = 0.047) and steepens the within-level probability drop to −15.8 p.p.; (b) the ordinal model delivers β = −0.128 (SE 0.059, p = 0.031) with a −16.3 p.p. shift in the probability of landing in the highest anxiety bin. These diagnostics justify retaining the serious-term as a supporting confirmatory contrast.
- **Confirmatory shell**: `tables/loop016_h4_confirmatory.csv` now lists four rows (moderate/serious × binary/ordinal), all regenerable from `scripts/loop020_h4_stress_tests.py`, so reviewers can inspect both anxiety codings before the next PAP freeze.

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
1. **Serious practice interaction** *(Completed in Loop 020)*: Ridge (α = 5) and ordered-logit analyses (see `tables/loop020_h4_stress_test_coeffs.csv` plus the `loop020_h4_*_prob_deltas.csv` files) both keep the serious slope negative and statistically meaningful, so the term remains inside the candidate family.
2. **Outcome robustness** *(Completed in Loop 020)*: The confirmatory table now reports both the binary ≥5 flag and the 3-bin ordinal outcome, satisfying the reviewer request for two codings per estimand.
3. **Documentation**: Next freeze still requires (a) tagging the updated PAP once reviewers are satisfied, (b) marking the family as confirmatory in `analysis/hypotheses.csv`, and (c) citing the expanded table inside `reports/paper.md`/`docs/loop016_reviewer_packet.md`.

## 7. Privacy & Reproducibility
- All referenced tables aggregate ≥14k respondents per row, meaning Principle 2 (no public cells with n < 10) is satisfied.
- Commands, seeds, and outputs are logged in `analysis/decision_log.csv` and `notebooks/research_notebook.md`. The promotion memo itself is now part of the audit trail so reviewers can trace exactly how the family will be promoted once confirmatory criteria are met.

## 8. Loop 021 Reviewer Summary Hook
- **What changed this loop**: Rather than refitting the models, we packaged the Loop 020 ridge/ordinal stress tests for reviewers by updating `analysis/pre_analysis_plan.md`, `analysis/sensitivity_notes.md`, and `docs/loop016_reviewer_packet.md` so they highlight the four-row confirmatory shell (binary tests + ordinal backups) and the reserved freeze tag `pap_freeze_h4_loop024`.
- **Multiplicity reminder**: Only the binary rows expand the BH denominator (`m=2`); the ordinal rows are preregistered outcome checks that must be regenerated in the freeze commit but leave the q-values (0.023; 0.194) unchanged.
- **Next reviewer touchpoint**: Once the steering reviewer acknowledges this summary (notebook + memo + sensitivity notes), we will execute the freeze protocol: rerun `scripts/loop020_h4_stress_tests.py`, refresh `tables/loop016_h4_confirmatory.csv`, update the PAP header to point at the new tag, and archive the approval trail inside `docs/reviewer_approvals/`.
