# Findings Summary — Loop 057
**Date:** 2025-11-09  
**Seed:** 20251016  

## Loop updates
- Rebuilt the confirmatory pipeline (`analysis/code/run_models.py`, `analysis/code/negative_control.py`, `analysis/code/summarize_results.py`, `analysis/code/calc_bh.py`) so `analysis/results.csv`, `artifacts/bh_summary.json`, and `tables/results_summary.csv/.md` now exist again and document the PAP q-values/limitations under the frozen registry entry.
- Documented `qc/disclosure_check_loop_056.md` (n ≥ 10 threshold) after rerunning `analysis/code/disclosure_check.py`, which now flags `tables/results_summary.csv` and `figures/dag_design.png` with zero violations so the small-cell audit is complete.
- Logged the mandated Semantic Scholar attempts for loops 056 (`lit/queries/loop_056/query_001.json`) and 057 (`lit/queries/loop_057/query_001.json`); both responses were HTTP 403 and the outage log in `lit/semantic_scholar_waiver_loop013.md` now captures them so the literature gate stays auditable while the credential remains offline.
- The sensitivity scenarios (pseudo weights, design-effect grid, pseudo replicates) continue to support the SRS + HC1 default, and the new results/tables bring those confidence intervals into the reproducible reporting stack.

## Next actions
1. Pull `analysis/results.csv`, `tables/results_summary.*`, the pseudo-weight/design-effect/replicate outputs, and `qc/disclosure_check_loop_056.md` into `papers/main/*`, `reports/identification.md`, and `reports/findings_v1.0.md` (per N11) so every `[CLAIM:<ID>]` cites regenerable evidence.
2. Keep the Semantic Scholar outage/waiver log current (N8) while awaiting a working S2 key and refresh `qc/strobe_sampl_checklist.md` + `qc/measures_validity.md` before shifting fully to the writing/review QC suite (N12).
