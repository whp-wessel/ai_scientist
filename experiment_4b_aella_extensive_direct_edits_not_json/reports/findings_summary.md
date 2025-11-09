# Findings Summary — Loop 056
**Date:** 2025-11-09  
**Seed:** 20251016  

## Loop updates
- Rebuilt the confirmatory table via `analysis/code/run_models.py`, `analysis/code/negative_control.py`, `analysis/code/summarize_results.py`, and `analysis/code/calc_bh.py` so `analysis/results.csv` now hosts H1–H3 with HC1 SEs, BH q-values (`q = 0.0006958` for H1 and 0 for H2/H3), and the flagged falsification row (`NC1` targeted `N`).
- Logged the mandated Semantic Scholar query for loop_055 under `lit/queries/loop_055/query_001.json` (403 Forbidden) and noted the failure in the waiver ledger so the literature gate remains auditable while we wait for ops to restore the key.
- Executed every sensitivity scenario from `analysis/sensitivity_manifest.md`: pseudo weights (`outputs/sensitivity_pseudo_weights/pseudo_weights_deff_{100,125,150}.json`), the design-effect grid (`outputs/sensitivity_design_effect_grid.csv/.md`), and the pseudo-replicate summary (`outputs/sensitivity_replicates/sensitivity_replicates_summary.json`). These outputs document the moderate variance inflation that keeps the frozen PAP estimates directionally stable and justify retaining SRS + HC1 as the default.

## Next actions
1. Pull `analysis/results.csv`, the new sensitivity artifacts, and the disclosure audit (`qc/disclosure_check_loop_055.md`) into `papers/main/*`, `reports/identification.md`, and `reports/findings_v1.0.md` so each `[CLAIM:<ID>]` references regenerable evidence (per N11).
2. Continue the literature/waiver log (N8) and update the STROBE/SAMPL and measurement validity checklists (`qc/strobe_sampl_checklist.md`, `qc/measures_validity.md`) before we transition toward the writing/review QC suite (N12).
