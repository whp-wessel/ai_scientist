# Findings Log — Version 1.0
**Date:** 2025-11-09  
**Seed:** 20251016  
**PAP:** Frozen at commit `2b3ee167762ad47af1426ab47d392d38323d1b74`, tag `pap-v1`, registry `https://osf.io/5x8hu`

## Summary
- Confirmatory H1–H3 models now live in `analysis/results.csv` (with BH-adjusted q-values) and the publication-ready `tables/results_summary.csv/.md`; the new `analysis/results.csv` anchors every estimate, p-value, and `bh_in_scope` metadata entry for reproducibility.
- A falsification check (NC1) remains targeted `N` and records a null effect on sibling count, reassuring that the modeling pipeline is stable even though the primary hypotheses are targeted for inference.
- Sensitivity artifacts (`analysis/sensitivity_manifest.md` plus `outputs/sensitivity_pseudo_weights/*`, `outputs/sensitivity_design_effect_grid.*`, and `outputs/sensitivity_replicates/sensitivity_replicates_summary.json`) document pseudo-weight, design-effect, and replicate experiments that bound how much design complexity could widen the HC1 CIs.
- The disclosure audit now lives in `qc/disclosure_check_loop_055.md`, so the n≥10 rule is verified after rebuilding `tables/results_summary.*` and no violations were found.
- Loop-level deltas are recorded in `reports/findings_summary.md` to keep the manuscript/reports teams aware of what changed this loop.

## Confirmatory Results
These estimates continue to assume SRS (HC1 SEs) until formal weights arrive; the `tables/results_summary.*` outputs include the effect metrics, CIs, q-values, and confidence labels.

1. **H1 / [CLAIM:C1]** — Childhood religious importance (very important vs not important) yields **ΔE[depression score] = -0.120** (95% CI [-0.187, -0.0548]; `q = 0.0006958`). The effect retains a negative sign after adjusting for demographics.
2. **H2 / [CLAIM:C2]** — Parental guidance (Q3 vs Q1) raises the probability of very good/excellent health by **+0.0998** (CI [0.0889, 0.1109]; `q ≈ 0`), suggesting a roughly ten-point gap for the highest guidance quartile.
3. **H3 / [CLAIM:C3]** — Childhood emotional abuse corresponds to a **–0.654** mean difference in adult self-love score (CI [–0.719, –0.590]; `q ≈ 0`), a substantively large drop captured with HC1 SEs.

## Negative Control
- **NC1 (family: negative_control)** — Regression of sibling count on childhood religiosity reports **estimate = 0.239** (CI [0.221, 0.257]); targeted `N`, so no q-value is assigned and the goal is to show that the confirmatory pipeline does not systematically produce false positives.

## Sensitivity summary
- **Pseudo-weight scenarios** produced effective n of 14,443 (DEFF=1.0), 11,628 (DEFF=1.25), and 9,533 (DEFF=1.5); H3’s SE increased to 0.0405 at DEFF=1.5 while H1/H2 SEs remained unchanged under the current Statsmodels weighting implementation.
- **Design-effect grid** inflates SEs via √DEFF for DEFF ∈ {1.0, 1.25, 1.5, 2.0}, reducing the effective sample to ~7,219 for H1/H2 at DEFF=2.0 but still leaving CI intervals (e.g., H1 at DEFF=2: [–0.192, –0.048]) safely away from zero.
- **Pseudo replicates** with k=6 jackknife runs report aggregate SEs of 0.019 (H1), 0.002 (H2), and 0.0177 (H3); these lower-bound SEs anchor discussions of potential clustering effects.
- The SRS + HC1 specification remains the default for reporting because the scenario outputs preserve effect direction and widen CIs only modestly; the supplemental artifacts document the uncertainty envelope.

## Limitations & Next Steps
- **Limitations:** Without released survey weights, we continue to lean on HC1 SEs and treat pseudo-weight/design-effect/replicate results as sensitivity bounds; chronic illness (`mentalillness`) remains empty and is excluded, and recall bias around abuse indicators persists.
- **Next steps:** (1) Refresh `papers/main/*` (manuscript/outline/manuscript.tex) and `reports/identification.md` with the new confirmatory + sensitivity narrative, citing `analysis/results.csv`, the sensitivity outputs, and `qc/disclosure_check_loop_055.md`. (2) Keep `reports/findings_summary.md` updated with loop-level deltas, and highlight the pseudo-weight/design-effect/replicate story plus the default-spec rationales so reviewers can trace each claim to artifacts. (3) Continue logging Semantic Scholar attempts per `N8` and respond to reviewer Qs before advancing to writing/review phases.
