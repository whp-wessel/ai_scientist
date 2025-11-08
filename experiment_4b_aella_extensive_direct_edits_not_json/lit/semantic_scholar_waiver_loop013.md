# Semantic Scholar Access Waiver Request — Loop 013
Date: 2025-11-08
Status: draft (pending partner approval)

## Summary
Since Loop 008 the dedicated Semantic Scholar key stored in `.env` has rejected every authenticated `paper/search` request with HTTP 403. Each attempt complied with the 1 req/sec policy via `scripts/semantic_scholar_cli.py`, logged inputs/outputs under `lit/queries/loop_{loop}/`, and was referenced in `analysis/decision_log.csv`. We now have ≥6 consecutive failures paired with fallback DOI-backed evidence from CrossRef (Ross et al., 2019) to keep the literature plan moving. To unblock PAP freeze we request a temporary waiver acknowledging these logged failures while ops works with Semantic Scholar support to restore the key.

## Attempt Log (Loops 008–013)
| Loop | Timestamp (UTC) | Query | Status | Artifact |
| --- | --- | --- | --- | --- |
| 008 | 2025-11-08T14:10:07Z | "childhood abuse self love adult wellbeing" | 403 Forbidden | `lit/queries/loop_008/query_001.json` |
| 009 | 2025-11-08T14:19:14Z | "childhood emotional abuse adult self love wellbeing" | 403 Forbidden | `lit/queries/loop_009/query_001.json` |
| 010 | 2025-11-08T14:27:55Z | "childhood abuse adult self love resilience wellbeing" | 403 Forbidden | `lit/queries/loop_010/query_001.json` |
| 011 | 2025-11-08T14:46:00Z | "childhood abuse self love adult wellbeing" | 403 Forbidden | `lit/queries/loop_011/query_001.json` |
| 012 | 2025-11-08T14:39:16Z | "childhood resilience religious adherence depression" | 403 Forbidden | `lit/queries/loop_012/query_001.json` |
| 013 | 2025-11-08T15:06:30Z | "childhood resilience spiritual support adult depression" | 403 Forbidden | `lit/queries/loop_013/query_001.json` |

_All JSON payloads include the endpoint, query params, and Semantic Scholar error body for reproducibility._

## Fallback Evidence & Bibliography Updates
- **Ross et al. (2019), DOI `10.1016/j.chiabu.2019.03.016`** — CrossRef metadata captured in `lit/queries/loop_012/crossref_query_001.json` and propagated to `lit/evidence_map.csv` / `lit/bibliography.bib`. Supports H3 by documenting self-compassion as a mediator between childhood maltreatment and adult depressive symptoms/self-worth.
- Existing DOI-backed sources for H1–H2 (Ezra et al., 2025; Thompson et al., 2015) and H3 (Islam et al., 2022) remain current and are cited with claim IDs `C1–C3`.

## Request
1. **Waiver:** Allow continuation through PAP freeze relying on the documented CrossRef DOIs while Semantic Scholar restores API access. The attempt log above, paired with decision-log entries, demonstrates due diligence.
2. **Remediation Plan:**
   - Open support ticket with Semantic Scholar (ref: API key ending `***7d`).
   - Once access is restored, replay the queued queries (loop 008 onward) to confirm parity and add any newly returned papers to the evidence map/bibliography.
   - Update `analysis/decision_log.csv` and this memo with the resolution timestamp, then close backlog item N1 (query execution) and mark this waiver as satisfied.

## Contacts & Next Steps
- Owner: Research agent (this experiment)
- Dependencies: Ops team for API credential refresh
- Blocking artifacts: PAP freeze (status=draft) and confirmatory analyses until either a working key or an approved waiver is recorded in `artifacts/state.json` per governance rules.
