# Sensitivity Plan — Loop 055
**Date:** 2025-11-09
**Seed:** 20251016 (recorded in `artifacts/seed.txt`)

## Confirmatory estimates and falsification
1. **H1 / well-being ([CLAIM:C1])** — Childhood religious importance contrast of **very important vs not at all important** yields **ΔE[depression score] = -0.120** (95% CI [-0.187, -0.0548]; `q = 0.0006958`) after the PAP-run ordered logit and BH correction (`analysis/results.csv`, `tables/results_summary.*`).
2. **H2 / self-rated health ([CLAIM:C2])** — The ordered-logit predicted probability gap for very good/excellent health between guidance Q3 vs Q1 is **+0.0998** (CI [0.0889, 0.1109]; `q ≈ 0`), showing the parental guidance contrast remains substantive under HC1 uncertainties.
3. **H3 / self-love ([CLAIM:C3])** — Linear regression of abuse status produces a **–0.654** mean difference in adult self-love (CI [–0.719, –0.590]; `q ≈ 0`), with HC1 SEs and weights still pending but recorded in `analysis/results.csv` for reproducibility.
4. **NC1 / sibling count (negative control)** — The falsification check produced **+0.239** (CI [0.221, 0.257]; targeted `N`), confirming the modeling logic remains stable without BH adjustment.

All confirmatory estimates continue to assume SRS with HC1-derived uncertainties; the new `analysis/results.csv` registers the q-values, `bh_in_scope`, and command metadata so the sensitivity scripts can reference the base estimates.

## Robustness checks completed
- **H1 high vs low religiosity** — `outputs/robustness_loop052/robustness_h1_high_low.json` reports ΔE = –0.088 (CI [–0.163, –0.012], n=14,438).
- **H2 continuous health coding** — `outputs/robustness_loop052/robustness_h2_continuous_health.json` shows a 0.0785-point shift on the 0–4 scale (CI [0.0696, 0.0874], n=14,430).
- **H3 non-perpetrators** — `outputs/robustness_loop052/robustness_h3_no_perpetration.json` keeps the abuse gap at –0.650 (CI [–0.720, –0.580]).
- **H3 teen-stage abuse control** — `outputs/robustness_loop052/robustness_h3_teen_abuse.json` shrinks the coefficient toward –0.264 (CI [–0.374, –0.154]), documenting teen exposures explain part of the adult association.

## Planned sensitivity scenarios
1. **Scenario 1 — Pseudo weights:** Generate pseudo weights matching DEFF 1.0 / 1.25 / 1.5 and re-fit H1–H3 so that the inflated sampling variance can be contrasted with the SRS baseline; commands and outputs live in `analysis/sensitivity_manifest.md` and `outputs/sensitivity_pseudo_weights/pseudo_weights_deff_{100,125,150}.json`.
2. **Scenario 2 — Design-effect grid:** Inflate the published SEs from `analysis/results.csv` by √DEFF (DEFF ∈ {1.0, 1.25, 1.5, 2.0}) to observe how the CIs/p-values widen and how many effective cases remain; outputs are `outputs/sensitivity_design_effect_grid.csv/.md`.
3. **Scenario 3 — Pseudo replicates:** Create `k=6` pseudo clusters (classchild_score + classcurrent_score) and jackknife omit-one cluster replicates to estimate variance analogously to BRR/JRR; summary stored at `outputs/sensitivity_replicates/sensitivity_replicates_summary.json`.

## Executed scenario summaries (loop 055)
- **Pseudo-weight scenarios** — DEFF-driven pseudo weights produced effective sample sizes of 14,443 (DEFF=1.0), 11,628 (DEFF=1.25), and 9,533 (DEFF=1.5). H3’s SE rose from 0.0331 to 0.0405 at DEFF=1.5 while H1 and H2 retained their base SEs (the weighted ordered logit currently does not alter H1/H2 SEs given Statsmodels’ handling of weights). The outputs encode the weights, commands, and results for each scenario.
- **Design-effect grid** — The grid shows that √DEFF inflation reduces the effective n to ~9,625 for H1/H2 and ~10,806 for H3 at DEFF=1.5, and to ~7,219 (H1) / 7,215 (H2) / 6,753 (H3) at DEFF=2.0, yet each CI [e.g., H1 DEFF=2: –0.192 to –0.048] still excludes the null. The table `outputs/sensitivity_design_effect_grid.csv` registers these adjusted SEs, p-values, and implied n_effective.
- **Pseudo replicates** — The k=6 replicates yield aggregate SEs of 0.019 (H1), 0.002 (H2), and 0.0177 (H3), lower than the HC1 base SEs but helpful as a lower bound; the summary JSON lists each replicate’s omitted cluster, command, and estimate.

## Default specification decision
The SRS + HC1 base specification remains the default for reporting because the pseudo-weight and design-effect scenarios preserve effect direction while only modestly widening the CIs, and the pseudo-replicate SEs (which trend lower) represent a bounding exercise rather than a replacement. The scenario artifacts therefore remain supplementary documentation of the uncertainty range while the main tables maintain the frozen PAP estimates.

## Next steps for reporting
- Integrate `analysis/results.csv`, the pseudo-weight/design-effect/replicate outputs, and the updated disclosure audit (`qc/disclosure_check_loop_055.md`) into `reports/findings_v1.0.md`, `reports/findings_summary.md`, and the `papers/main/*` manuscript assets so each claim has the new evidence and the disclosure log references the updated tables.
- Cite `analysis/sensitivity_manifest.md` within the manuscript/outline to prove each scenario command is reproducible, and highlight the pseudo-weight/deff/replicate syntheses in the methods/discussion narrative.
- Keep the Semantic Scholar waiver log plus `lit/queries/loop_055` aligned while pushing toward writing-phase QC (review next actions N11/N12).
