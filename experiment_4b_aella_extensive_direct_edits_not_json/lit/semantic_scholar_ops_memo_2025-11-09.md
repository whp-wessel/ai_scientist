# Semantic Scholar Access Memo — Ops Submission (Due 2025-11-09 15:00Z)
Date prepared: 2025-11-08
Owner: Science Agent (experiment_4b)

## Summary
- Since Loop 008 (2025-11-08T14:10Z) every call to the dedicated Semantic Scholar CLI (`scripts/semantic_scholar_cli.py`) has returned **HTTP 403 Forbidden** despite honoring the 1 request/second policy.
- The outage now spans **35 consecutive loops (008–042)**. Each request/response pair—parameters, endpoint, timestamps, and error body—is archived under `lit/queries/loop_{loop}/query_001.json` for auditability.
- To keep the literature plan moving we captured DOI-backed evidence via CrossRef each loop (`lit/queries/loop_{loop}/crossref_query_*.json`) and synchronized those sources across `lit/evidence_map.csv`, `lit/bibliography.bib/.json`, and the waiver log (`lit/semantic_scholar_waiver_loop013.md`). Confirmatory analysis nevertheless remains blocked because the PAP cannot freeze without either restored S2 access or an approved waiver.

## Key Evidence
1. **Latest failure (Loop 042)** — Query `"childhood trusted adult mentorship adult depression buffer"` at 2025-11-08T22:01:30Z → `lit/queries/loop_042/query_001.json` (HTTP 403). Envelope references: `analysis/decision_log.csv` row `semantic_scholar_query_loop042`.
2. **Cumulative attempt ledger** — `lit/semantic_scholar_waiver_loop013.md` now documents loops 008–042 with timestamps plus fallback DOIs (e.g., Kuhar et al., 2024; DOI `10.5708/ejmh.19.2024.0031`).
3. **Reproducibility attachments** — `artifacts/session_info.txt` (22:00Z snapshot) and `artifacts/checksums.json` confirm the environment/seed (20251016) used for all requests.

## Request to Ops
- Confirm whether the dedicated Semantic Scholar key stored in `.env` was rate-limited, revoked, or misconfigured on 2025-11-08.
- If revoked: issue a replacement key or unblock the existing credential and notify the agent via comment in `analysis/decision_log.csv` (loop 042) plus Slack ticket `S2-Outage-2025-11-08`.
- If additional verification is required, provide the checklist and contact window so we can include it in the support ticket slated for 2025-11-10.

## Planned Follow-ups
- **2025-11-09 15:00Z** — Send this memo plus selected JSON payloads (`loop_040`–`loop_042`) to ops, request confirmation of receipt, and log the response in `analysis/decision_log.csv`.
- **2025-11-10 15:00Z** — If no remediation is in place, submit the prepared Semantic Scholar support ticket (draft below) and link the outbound request + response in the decision log.
- Continue daily CLI attempts plus CrossRef fallbacks until the credential is restored or a waiver is approved.

## Attachments / Pointers
- Error payload: `lit/queries/loop_042/query_001.json`
- CrossRef fallback: `lit/queries/loop_042/crossref_query_002.json`
- Waiver log: `lit/semantic_scholar_waiver_loop013.md`
- Evidence map snapshots: `lit/evidence_map.csv` rows ≥41 (Kuhar et al. 2024)
- Decision log reference rows: `review_sync_loop042`, `repro_checkpoint_loop042`, `semantic_scholar_query_loop042`, `crossref_scan_loop042`
