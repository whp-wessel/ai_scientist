# Findings Log — Version 1.7
**Date:** 2025-11-09  
**Seed:** 20251016  
**PAP:** Frozen at commit `2b3ee167762ad47af1426ab47d392d38323d1b74`, tag `pap-v1`, registry `https://osf.io/5x8hu`

## Summary
- The mandated Semantic Scholar search for “childhood religiosity adult depression protective factors” still returned HTTP 403, so we captured the CrossRef fallback `Poole et al. 2017` (Child Abuse & Neglect, DOI `10.1016/j.chiabu.2016.12.012`) via `lit/queries/loop_069/crossref_query_002.json`; the evidence map and bibliography entries now document this resilience-based protective mechanism for `[CLAIM:C1]`.
- Synchronized the Markdown twin, LaTeX manuscript, IMRaD outline, STROBE+SAMPL checklist, identification memo, and research notebook so every claim, estimate, and sensitivity note references the updated resilience literature, the deterministic artifact paths, and the new disclosure audit (`qc/disclosure_check_loop_069.md`) before review-phase handoff.
- No new public tables or figures were released beyond the existing `tables/results_summary.*` and `figures/dag_design.png`, whose deterministic commands/seed are logged (`analysis/code/build_results_summary.py`, `analysis/code/plot_dag.py`) and whose n ≥ 10 safety continues to be enforced by `qc/disclosure_check_loop_069.md`.

## Next steps
1. Move toward the review phase: collect review-checklist responses under `reports/review_checklist.md`, ensure the >latest Tectonic run is recorded in `papers/main/build_log.txt`, and log any reviewer instructions in `review/research_findings.md` before handing off.
2. Continue documenting Semantic Scholar attempts (loop 070+) and CrossRef fallbacks so each `[CLAIM:<ID>]` keeps at least one DOI-backed source; add every new entry to `lit/evidence_map.csv` and `lit/bibliography.*`.
3. Track the remaining review-phase gatekeepers (STROBE/SAMPL, DAG identifications, small-cell disclosures) so the next findings log entry names the artifacts that cleared the reviewer list.
