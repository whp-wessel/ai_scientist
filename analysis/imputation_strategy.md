# Imputation Strategy for Wellbeing and Abuse Items

Generated: 2025-10-16T13:30:45Z (seed 20251016)

## Summary of Diagnostics (Exploratory)
- Missingness rates remain below the disclosure threshold; the self-love item has <10 missing responses after suppression, while the parental emotional abuse item has 17 missing responses (0.12%).
- Logistic regressions using age, childhood class, current net worth, education, and sex at birth indicate that missing self-love responses are modestly associated with older age (+0.06 log-odds per year) and lower education (-0.72). Missing abuse responses are more common among respondents reporting higher childhood class (+0.65) and among those assigned male at birth (+1.72).

## Planned Approach
1. **Primary Method**: Multiple Imputation by Chained Equations (MICE) using predictive mean matching for continuous/ordinal scores and logistic/ordinal logistic models for categorical predictors. Implement with `mice` (R) or `statsmodels`/`sklearn` pipelines in Python to maintain compatibility with survey workflows.
2. **Imputation Model Variables**: Include wellbeing outcomes, childhood adversity indicators, demographic controls (`selfage`, `classchild`, `education`, `networth`, `biomale`, `gendermale`, `cis`, `liberal`), and any auxiliary variables correlated with non-response (e.g., survey mode, religious practice).
3. **Iterations and Seeds**: Run 20 imputations with 10 burn-in iterations each, seeding all randomness with 20251016 to satisfy reproducibility requirements.
4. **Survey Design Considerations**: Once official weights arrive, incorporate them via weighted imputation or passive imputation diagnostics; until then, assume SRS and document the limitation.
5. **Robustness Checks**:
   - Compare complete-case estimates with multiply-imputed estimates for key hypotheses (HYP-001, HYP-002).
   - Re-run imputations with reduced predictor sets (dropping auxiliary variables) to evaluate sensitivity of imputed distributions.
6. **Diagnostics**: Inspect convergence plots, distribution overlays, and posterior predictive checks; flag any persistent model misfit before confirmatory analyses.

## Next Steps
- Await clarification/documentation on official survey weights (see Draft Request).
- Expand the codebook to document coding for suppressed categories prior to implementing the imputation scripts.

## 2025-10-16 Update — Imputed vs Complete-Case Review
- Ran `analysis/code/review_imputed_vs_complete.py` using seed 20251016; summary in `tables/imputed_vs_complete_summary.csv`.
- Mean shifts across key variables remained within ±15% relative to complete-case estimates, supporting MI as primary strategy.
- `Religionchildhood` and `mentalillness` remain excluded due to zero observed values; retain placeholder for future coding review.

## Updated Robustness Actions
- Confirmatory analyses will report both MI-pooled and complete-case estimates for HYP-001 and HYP-002.
- Add sensitivity re-running MI with the auxiliary predictor set reduced to demographic core variables to test stability.
- Document any deviations (e.g., alternative convergence criteria) in `analysis/imputation_strategy.md` with timestamps.

## 2025-10-16T14:08Z — Reduced Auxiliary Sensitivity Plan
- Documented `analysis/imputation/mi_reduced_aux_plan.md` detailing a trimmed MICE run (`run_label=reduced_aux`) limited to outcome/predictor/control variables for HYP-001/002.
- Future diagnostics: compare reduced-auxiliary imputations against both complete-case and full-auxiliary (`prototype`) runs, highlighting shifts >15% in pooled estimates or SEs.
- Results will feed into PAP robustness clauses before freeze and inform whether auxiliary covariates materially influence inference.
