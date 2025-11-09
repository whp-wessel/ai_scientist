# Findings Summary — Loop 074
**Date:** 2025-11-09  
**Seed:** 20251016

## Loop updates
- Added the Conkbayir (2023) CrossRef fallback (DOI `10.4324/b23180`) via `lit/queries/loop_075/crossref_query_001.json`, the evidence map, and bibliography so `[CLAIM:C1]` retains DOI coverage while Semantic Scholar still returns 403; the waiver log also notes loop 075.
- Completed the N17 release packaging steps (review checklist, findings log, manuscript/manuscript.md parity, and the final build) so the release candidate now cites `qc/disclosure_check_loop_074.md` and the imported CrossRef evidence.
- Confirmed the disclosure scan (`qc/disclosure_check_loop_074.md`) still covers `tables/results_summary.*` and `figures/dag_design.png`, so the $n \geq 10$ guardrail holds for the public artifacts.

## Next actions
1. Monitor `review/research_findings.md` for any new reviewer directives, document responses in `analysis/decision_log.csv`, and only move toward actual public release once the reviewer records `DECISION: CONTINUE`.
2. Keep the CrossRef/waiver ledger (lit/semantic_scholar_waiver_loop013.md and lit/evidence_map.csv) current so `[CLAIM:C1]` stays DOI-backed until the Semantic Scholar credential is restored.
3. Maintain the release artifact bundle (manuscript PDF, build log, disclosure report, review checklist, and findings log) in sync while waiting for reviewer clearance so the release-phase gate can close immediately once allowed.
