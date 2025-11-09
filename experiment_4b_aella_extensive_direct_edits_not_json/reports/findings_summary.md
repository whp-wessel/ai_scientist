# Findings Summary — Loop 058
**Date:** 2025-11-09  
**Seed:** 20251016  

## Loop updates
- Rebuilt the confirmatory pipeline (`analysis/code/run_models.py`, `analysis/code/negative_control.py`, `analysis/code/summarize_results.py`, `analysis/code/calc_bh.py`, and `analysis/code/build_results_summary.py`) so `analysis/results.csv`, `artifacts/bh_summary.json`, and `tables/results_summary.csv/.md` now exist again with deterministic commands tied to the frozen PAP (`pap-v1`).
- Logged the disclosure audit via `analysis/code/disclosure_check.py`, which rescanned `tables/results_summary.csv` and `figures/dag_design.png` and produced `qc/disclosure_check_loop_058.md` with `violations: 0` at the n ≥ 10 threshold.
- Archived the new Semantic Scholar 403 attempt (`lit/queries/loop_058/query_001.json`) and the CrossRef fallback (`lit/queries/loop_058/crossref_query_001.json`), adding the DOI-backed row for `https://doi.org/10.1080/13674676.2018.1504906` to `lit/evidence_map.csv`, so literature logging stays auditable while the waiver/credential repair proceeds.
- Re-ran the sensitivity pipelines (pseudo weights, design-effect grid, pseudo replicates) so the `outputs/sensitivity_*` artifacts document how DEFF variations and jackknife replicates affect the HC1 estimates while the SRS + HC1 default remains the reporting specification.

## Next actions
1. Integrate `analysis/results.csv`, `tables/results_summary.*`, the new sensitivity outputs, and `qc/disclosure_check_loop_058.md` into the manuscript/outline/`reports/identification.md` per N11 so every `[CLAIM:<ID>]` cites regenerable evidence.
2. Keep the Semantic Scholar outage/waiver log current (N8) while the S2 credential is fixed and continue adding DOI-backed entries whenever a query or fallback yields new sources.
3. Update `qc/strobe_sampl_checklist.md`, `qc/measures_validity.md`, and other QC artifacts with the latest confirmatory + sensitivity data before transitioning toward the writing/review suite (per N12).
