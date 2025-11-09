# Findings Summary — Loop 074
**Date:** 2025-11-09  
**Seed:** 20251016

## Loop updates
- Logged the CrossRef fallback for Morris & Hays-Grudo 2023 (World Psychiatry 2023) in `lit/queries/loop_073/crossref_query_001.json`, `lit/evidence_map.csv`, and `lit/bibliography.*` so `[CLAIM:C1]` stays DOI-backed while Semantic Scholar remains offline.
- Updated the release-phase dossiers (review checklist, findings log, manuscript, identification memo, imprint manifest, and STROBE/SAMPL checklist) as part of `N16`, keeping the frozen PAP and final tables in sync before public release.
- Reran the disclosure audit for the release candidate (`qc/disclosure_check_loop_074.md` references `tables/results_summary.*` and `figures/dag_design.png`) so every published artifact still satisfies the $n \geq 10$ guardrail.

## Next actions
1. Finalize the release package by completing the LaTeX build (log `papers/main/build_log.txt`), sealing the manuscript/manuscript.md parity, and preparing the final `reports/findings_v2.0` version.
2. Keep the CrossRef/waiver ledger ready for `N8` (resume Semantic Scholar once OPS restores the S2 credential) so every claim continues to cite DOI-backed sources without throttling the release gate.
3. Watch `review/research_findings.md` for new reviewer instructions, log any follow-ups that arrive, and tie them to future next actions before declaring the release-phase gate satisfied.
