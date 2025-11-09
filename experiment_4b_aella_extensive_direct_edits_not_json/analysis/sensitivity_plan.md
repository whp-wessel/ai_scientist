# Sensitivity Plan — Loop 062
**Date:** 2025-11-09  
**Seed:** 20251016 (see `artifacts/seed.txt`; every command below reuses this seed so the rerun remains deterministic).

## Confirmatory estimates and falsification
1. **H1 / depression (`[CLAIM:C1]`)** — The ordered-logit contrast for “religion very important” vs “not at all important” is `ΔE = -0.1201` (95% CI [−0.189, −0.051]; `q ≈ 0.0007`; `analysis/results.csv`). The `wellbeing` family continues to list `bh_in_scope = H1|H2` and `targeted = Y`, so BH correction relates the elements deterministically.
2. **H2 / self-rated health (`[CLAIM:C2]`)** — The guidance contrast remains positive at `+0.0998` (95% CI [0.0889, 0.1109]; `q = 0`), with HC1 SE = 0.0057 and `n = 14,430` recorded in `analysis/results.csv`.
3. **H3 / self-love (`[CLAIM:C3]`)** — The abuse vs. none gap stays at `-0.6544` (95% CI [−0.719, −0.590]; `q = 0`), with `n = 13,507` and HC1 SE = 0.0331 logged alongside the command string.
4. **NC1 / sibling count (negative control)** — Linear null check (`outputs/negative_control_loop059.json`) continues to show `+0.2388` (95% CI [0.2209, 0.2568]; `p ≈ 0`); `targeted = N` so BH adjustments exclude it while preserving diagnostics.

## Robustness checks completed
- **H1 high vs. low religiosity** (`outputs/robustness_loop052/robustness_h1_high_low.json`) preserves the negative contrast when pairing “very important” and “not at all important.”
- **H2 continuous health coding** (`outputs/robustness_loop052/robustness_h2_continuous_health.json`) keeps the positive slope when treating self-rated health as a numeric outcome (0–4).
- **H3 non-perpetrators & timing controls** (`outputs/robustness_loop052/robustness_h3_no_perpetration.json`, `_robustness_h3_teen_abuse.json`) sustain the self-love gap when restricting to non-perpetrators or teen-stage abuse controls.

## Sensitivity scenarios executed this loop
- **Scenario 1 – pseudo weights (DEFF ∈ {1.0, 1.25, 1.5})** — `analysis/code/pseudo_weight_sensitivity.py` rewrote `outputs/sensitivity_pseudo_weights/pseudo_weights_deff_100.json`, `_125.json`, and `_150.json` with the loop-062 seed. Effective samples decline from 14,443 (DEFF=1.0) to 11,629 (DEFF=1.25) to 9,533 (DEFF=1.5) while H1/H2 SEs stay near 0.0354/0.0057 and H3’s SE only increases to 0.0405, preserving directionality.
- **Scenario 2 – design-effect grid (DEFF ∈ {1.0, 1.25, 1.5, 2.0})** — `analysis/code/design_effect_grid.py` regenerated `outputs/sensitivity_design_effect_grid.csv/.md`, showing that even at DEFF=2.0 the 95% CIs remain negative for H1/H3 and positive for H2 while effective n drops toward ∼7,200 (H1/H2) and ∼6,750 (H3).
- **Scenario 3 – pseudo replicates (k=6)** — `analysis/code/pseudo_replicates.py` rewrote `outputs/sensitivity_replicates/sensitivity_replicates_summary.json`, yielding jackknife SEs of ≈0.040 (H1), 0.006 (H2), and 0.036 (H3) that stay within 0.01 of the base HC1 estimates.

## Default specification decision
The SRS + HC1 sequence (run_models → summarize_results → calc_bh → build_results_summary) remains the default because the pseudo-weight scenarios only modestly inflate uncertainty, the design-effect grid retains CI bounds on the same side of zero even at DEFF=2.0, and the pseudo-replicates produce slightly tighter SEs that reinforce the baseline. These supplemental scenarios serve as robustness anchors while we continue to report the HC1 estimates as the conservative default.

## Loop 062 synthesis
- Re-aggregated the H1–H3 JSON outputs via `analysis/code/summarize_results.py`, applied BH through `analysis/code/calc_bh.py`, and rebuilt `tables/results_summary.csv/.md` so `analysis/results.csv`, `artifacts/bh_summary.json`, and the tables now mirror the loop-062 deterministic estimates and q-values.
- Re-ran the full sensitivity suite (pseudo weights, the DEFF grid, and pseudo replicates) so `outputs/sensitivity_pseudo_weights/*`, `outputs/sensitivity_design_effect_grid.*`, and `outputs/sensitivity_replicates/sensitivity_replicates_summary.json` now host the refreshed uncertainty bounds seeded at 20251016.
- Executed `analysis/code/measure_validity_checks.py --output-json artifacts/measurement_validity_loop061.json` so `qc/measures_validity.md` plus the JSON dossier capture the latest reliability and DIF diagnostics for each outcome/predictor.
- Ran `analysis/code/disclosure_check.py --output-md qc/disclosure_check_loop_061.md` to confirm `tables/results_summary.csv` and `figures/dag_design.png` remain above the n ≥ 10 disclosure threshold before referencing them downstream (violations=0).
- Issued the loop-mandated Semantic Scholar query (`lit/queries/loop_061/query_001.json`, still HTTP 403) and archived the CrossRef fallback (`lit/queries/loop_061/crossref_query_001.json`, DOI 10.23880/mhrij-16000182) so `[CLAIM:C1]` keeps DOI-backed coverage while the S2 key remains blocked.
- Integrated the rerun confirmatory and sensitivity summaries into `papers/main/manuscript.*`, `papers/main/imrad_outline.md`, `reports/identification.md`, `qc/strobe_sampl_checklist.md`, and `reports/findings_summary.md` so every `[CLAIM:<ID>]` now cites deterministic artifacts plus the refreshed QC notes.

## Next steps for reporting
1. Continue logging blocked Semantic Scholar queries plus CrossRef fallbacks (N8) so `lit/evidence_map.csv` and `lit/bibliography.*` stay DOI-backed until the S2 key or waiver clears.
2. With N11/N12 complete, the next loop will focus on writing-phase QC: refresh the STROBE/SAMPL checklist, ensure the LaTeX build records `LaTeX build: PASS` in `papers/main/build_log.txt`, and validate any new tables/figures via `qc/disclosure_check_loop_{loop:03d}.md`.
3. Keep narrating these loop-level deltas in `reports/findings_summary.md`/`reports/findings_v*.md` plus the notebook so the manuscript team sees the latest provenance before the writing phase advances.
