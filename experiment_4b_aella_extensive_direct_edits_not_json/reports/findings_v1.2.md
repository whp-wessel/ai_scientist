# Findings Log — Version 1.2
**Date:** 2025-11-09  
**Seed:** 20251016  
**PAP:** Frozen at commit `2b3ee167762ad47af1426ab47d392d38323d1b74`, tag `pap-v1`, registry `https://osf.io/5x8hu`

## Summary
- Confirmatory H1–H3 outputs plus `tables/results_summary.csv/.md` continue to mirror the deterministic pipeline that builds `analysis/results_pre_bh.csv` → `analysis/results.csv` with BH q-values, so every summary row now matches the PAP-seeded JSONs and `analysis/results.csv` includes the `bh_in_scope` metadata defined in the plan.
- The sensitivity suite (pseudo weights, design-effect grid, pseudo replicates) was rerun with loop-064's commands so `analysis/sensitivity_plan.md` and the `outputs/sensitivity_*` artifacts log the new uncertainty envelope; the pseudo weights report the effective n drop to ~9,500 at DEFF=1.5 and H3’s SE growth, while the DEFF grid and jackknife replicates keep the sign pattern intact.
- Disclosure control was re-verified via `analysis/code/disclosure_check.py --output-md qc/disclosure_check_loop_064.md` and the Semantic Scholar 403 plus CrossRef fallback (DOI 10.1080/19349637.2014.864543) were recorded in `lit/queries/loop_064/` plus a new `lit/evidence_map.csv` row so [CLAIM:C1] remains DOI-backed while the API remains blocked.
- The loop-064 notes landed in `notebooks/research_notebook.md` and `reports/findings_summary.md`, keeping the ledger synchronized with the deterministic commands before the writing-phase QC pass begins.

## Next steps
1. Advance the writing-phase QC pass: refresh the manuscript + outline for any textual edits, rerun `qc/strobe_sampl_checklist.md`, verify `reports/identification.md` against `figures/dag_design.png`, rerun the LaTeX build (per `papers/main/build_log.txt`), and draft `reports/findings_v1.3.md` once the checklist and DAG remain stable.
2. Keep issuing Semantic Scholar searches and CrossRef fallbacks (lit/queries/loop_0XX/) until the S2 key recovers; each attempt must be logged in `analysis/decision_log.csv` and the evidence map so every `[CLAIM:<ID>]` stays DOI-backed.
3. Keep the notebook/report ledger (notebooks, reports/findings_*.md, decision log) current so reviewers can track the deterministic path before review-phase adjudication.
