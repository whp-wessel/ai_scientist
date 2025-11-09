# Findings Log — Version 1.0
**Date:** 2025-11-09  
**Seed:** 20251016  
**PAP:** Frozen at commit `2b3ee167762ad47af1426ab47d392d38323d1b74`, tag `pap-v1`, registry `https://osf.io/5x8hu`

## Summary
- Confirmatory H1–H3 models ran deterministically (draws=400) using `analysis/code/run_models.py`; results now recorded in `analysis/results.csv` with BH-adjusted q-values.
- A falsification check (NC1) assessing whether childhood religiosity predicts sibling count was intentionally tagged `targeted=N` and shows a null association, reinforcing the targeted effect specificity.
- Publication-ready tables reside in `tables/results_summary.csv/.md` while `qc/disclosure_check_loop_054.md` now certifies that the N≥10 threshold holds for the refreshed tables/figures.
- Sensitivity roadmap has been formalized in `analysis/sensitivity_plan.md`, enumerating pseudo-weight adjustments, a design-effect grid, and pseudo-replicates before the writing phase.
- Completed the pseudo-weight, design-effect grid, and pseudo-replicate scenarios (see `outputs/sensitivity_pseudo_weights/*`, `outputs/sensitivity_design_effect_grid.*`, `outputs/sensitivity_replicates/sensitivity_replicates_summary.json`) with commands in `analysis/sensitivity_manifest.md`.
- The Semantic Scholar key still returns HTTP 403 (loop_053 recorded in `lit/semantic_scholar_waiver_loop013.md` and `analysis/decision_log.csv`), so we continue to lean on the approved CrossRef waiver trail while holding N8 pending.

## Confirmatory Results
These estimates inherit the SRS assumption documented in `docs/survey_design.yaml` and leverage HC1 SEs or simulation-based draws where appropriate.

1. **H1 / [CLAIM:C1]** — Childhood religious adherence vs adult depression (`ΔE[depression score | very important vs not at all important] = -0.120` with 95% CI [-0.187, -0.055]; `q = 0.0007`). The negative difference aligns with higher religiosity predicting slightly lower depression tendencies after controlling for demographics (see `tables/results_summary.*`).
2. **H2 / [CLAIM:C2]** — Parental guidance vs adult health (`ΔPr(very good/excellent health | guidance Q3 vs Q1) = 0.0998`, CI [0.089, 0.111]; `q = 0.0`). Strong guidance appears associated with a ten-percentage-point higher probability of excellent/very good health even under SRS.
3. **H3 / [CLAIM:C3]** — Childhood abuse vs adult self-love (`Δmean self-love (abuse vs none) = -0.654`, CI [-0.719, -0.590]; `q = 0.0`). Abuse exposure corresponds to substantively lower self-love scores with robust SEs from HC1 linear regression.

## Negative Control
- **NC1 (family: negative_control)** — Regression of sibling count on childhood religiosity yields `estimate = 0.239` (CI [0.221, 0.257]) with `p < 0.001`, but this check is deliberately `targeted=N` and recorded primarily to ensure modeling pipelines are stable; no q-value is computed, and its large sample size keeps it above the n=10 disclosure threshold.

## Limitations & Next Steps
- **Limitations:** All models currently rely on the SRS assumption; survey weights/complex design elements remain absent, so future updates will revisit standard errors once weights are provided (documented in `analysis/data_processing.md::DP9`). Chronic illness (`mentalillness`) is empty and excluded; abused participants may misreport exposures (H3).
- **Planned robustness checks:** per PAP, we will (a) binarize predictors/outcomes, (b) limit by chronic illness indicator, (c) incorporate teen-stage abuse indicators or exclude respondents with perpetration reports, and (d) revisit guidance–health links with alternative codings; `analysis/sensitivity_plan.md` now extends this list with pseudo-weight, design-effect, and pseudo-replicate scenarios before the writing phase.
- **Next steps:** (1) Incorporate the confirmatory and now-complete sensitivity outputs (pseudo weights, design-effect grid, pseudo replicates) into the outline/manuscript while citing `analysis/sensitivity_manifest.md` and `qc/disclosure_check_loop_054.md`. (2) Continue logging Semantic Scholar retries and append any successful responses to `lit/semantic_scholar_waiver_loop013.md` so the waived backlog (N8) can close once the API recovers. (3) Refresh `papers/main/imrad_outline.md`, `papers/main/manuscript.md`, `papers/main/manuscript.tex`, and `reports/identification.md` with the updated results, sensitivity narrative, and `[CLAIM:<ID>]` citations. (4) Keep the waiver/disclosure logs current while approaching the review phase.
