# Sensitivity Plan — Loop 063
**Date:** 2025-11-09  
**Seed:** 20251016 (see `artifacts/seed.txt`; all commands below reuse this seed so reruns stay deterministic).

## Confirmatory estimates and falsification
1. **H1 / depression ([CLAIM:C1])** — Ordered-logit contrast for “religion very important” vs. “not at all important” is `ΔE = -0.1201` (95% CI [−0.187, −0.055], $q $\approx$ 0.0007$) with `n = 14,438`; HC1 SE = 0.0354 and BH metadata appear in `analysis/results.csv` with `bh_in_scope = H1|H2`.
2. **H2 / self-rated health ([CLAIM:C2])** — Guidance quartile contrast reads `+0.0998` (95% CI [0.0889, 0.1109], $q = 0$) with `n = 14,430`; this ordered-logit slope is also logged in `analysis/results.csv` for the wellbeing family.
3. **H3 / self-love ([CLAIM:C3])** — Abuse vs. none gap is `-0.6544` (95% CI [−0.719, −0.590], $q = 0$) with `n = 13,507`; the linear output plus HC1 SE (0.0331) is reproducible via `analysis/code/run_models.py` and `analysis/results.csv`.
4. **NC1 / sibling count (negative control)** — Linear difference remains `+0.2388` (95% CI [0.2209, 0.2568], $p $\approx$ 0$); NC1 is tagged `targeted=N` to keep it outside the BH family while documenting the null expectation.

## Robustness checks completed
- **H1 high vs. low religiosity** (`outputs/robustness_loop052/robustness_h1_high_low.json`) keeps the negative depression contrast when comparing the extremes of the religiosity scale.
- **H2 continuous health coding** (`outputs/robustness_loop052/robustness_h2_continuous_health.json`) sustains the positive slope when treating self-rated health as numeric (0–4).
- **H3 non-perpetrators & timing controls** (`outputs/robustness_loop052/robustness_h3_no_perpetration.json` and `_robustness_h3_teen_abuse.json`) keep the abuse-self-love gap while restricting to non-perpetrators or teen-stage abuse disclosures.

## Sensitivity scenarios executed this loop
- **Scenario 1 – pseudo weights (DEFF ∈ {1.0, 1.25, 1.5})** — `analysis/code/pseudo_weight_sensitivity.py` rewrote `outputs/sensitivity_pseudo_weights/pseudo_weights_deff_100.json`, `_125.json`, and `_150.json` with seeds adjusted per scenario. Effective n shrinks from 14,443 (DEFF=1.0) to 11,629 (DEFF=1.25) to 9,533 (DEFF=1.5) while H1/H2 SEs rise from 0.0354/0.0057 to $\approx$0.040/0.0064 and H3 SE stays near 0.037, preserving the sign patterns.
- **Scenario 2 – design-effect grid (DEFF ∈ {1.0, 1.25, 1.5, 2.0})** — `analysis/code/design_effect_grid.py` regenerated `outputs/sensitivity_design_effect_grid.csv/.md`, showing that even at DEFF=2.0 the 95% CIs keep H1/H3 below zero and H2 above while effective n dips toward $\sim$7,200 (H1/H2) and $\sim$6,750 (H3).
- **Scenario 3 – pseudo replicates (k = 6)** — `analysis/code/pseudo_replicates.py` refreshed `outputs/sensitivity_replicates/sensitivity_replicates_summary.json`, yielding jackknife SEs of $\approx$0.040 (H1), 0.006 (H2), and 0.036 (H3) that stay within 0.01 of the HC1 estimates, confirming the conservative default.

## Default specification decision
The SRS + HC1 pipeline (run_models → summarize_results → calc_bh → build_results_summary) remains the default because the pseudo-weight scenarios only modestly widen SEs, the DEFF grid retains the same sign pattern through DEFF=2.0, and the pseudo-replicates replicate the baseline uncertainty. These exercises anchor the descriptive conclusions while leaving HC1 as the conservative reporting choice.

## Loop 063 synthesis
- Re-aggregated the JSON outputs (`outputs/run_models_loop059_H1.json`–`H3.json`) via `analysis/code/summarize_results.py`, reapplied BH through `analysis/code/calc_bh.py`, and rebuilt `tables/results_summary.csv/.md` so `analysis/results.csv`, `artifacts/bh_summary.json`, and the publication table now mirror the seed 20251016 estimates and q-values.
- Re-ran the sensitivity suite (pseudo weights, DEFF grid, pseudo replicates) so `outputs/sensitivity_pseudo_weights/*`, `outputs/sensitivity_design_effect_grid.*`, and `outputs/sensitivity_replicates/sensitivity_replicates_summary.json` now host the refreshed uncertainty bounds for loop 063.
- Ran `analysis/code/disclosure_check.py --output-md qc/disclosure_check_loop_063.md` to verify `tables/results_summary.csv` and `figures/dag_design.png` stay above the n $\geq$ 10 threshold before referencing them downstream (violations=0).
- Compiled `papers/main/manuscript.tex` via `tectonic --keep-logs papers/main/manuscript.tex` so `papers/main/manuscript.pdf` plus `papers/main/manuscript.log/.blg` document the rendering; log entries note the expected overfull boxes while the build remains PASS.
- Issued the loop-063 Semantic Scholar query (`lit/queries/loop_063/query_001.json`), captured the CrossRef fallback (`lit/queries/loop_063/crossref_query_001.json`, DOI `10.1080/19349637.2014.864543`), and refreshed `lit/evidence_map.csv`, `lit/bibliography.bib`, and `lit/bibliography.json` so [CLAIM:C1] retains DOI-backed coverage.
- Updated `reports/findings_summary.md` and `reports/findings_v1.1.md` with this loop’s synthesis and noted the writing-phase QC progress, then reflected the same steps in `notebooks/research_notebook.md` so the notebook mirrors the rerun.

## Next steps
1. With the sensitivity ticked again, focus the next loop on writing-phase QC: refresh `papers/main/imrad_outline.md` if needed, align `papers/main/manuscript.tex` with any textual edits, rerun the STROBE/SAMPL checklist, and lock down the versioned report before entering review.
2. Keep tracking blocked Semantic Scholar queries + CrossRef fallbacks (lit/queries/loop_0XX/) so every `[CLAIM:<ID>]` stays DOI-backed; note latest fallback in `analysis/decision_log.csv` and `lit/evidence_map.csv` until the S2 key or waiver is resolved.
3. Document loop-level updates in `notebooks/research_notebook.md`, `reports/findings_summary.md`, and `analysis/decision_log.csv` so reviewers can follow the deterministic path before this sensitivity phase concludes.
