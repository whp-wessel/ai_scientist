# Semantic Scholar Support Ticket Draft (To send 2025-11-10 15:00Z)
Prepared: 2025-11-08

**Subject:** API key 403 failures since 2025-11-08 (project: experiment_4b)

**Message body (ready to paste into Semantic Scholar support portal)**
```
Hello Semantic Scholar Support,

Our dedicated API key (stored in our private .env; available upon request) began returning HTTP 403 Forbidden responses to the `/graph/v1/paper/search` endpoint on 2025-11-08 at 14:10Z and has rejected every authenticated request since then despite honoring the 1 request/second rate limit. We rely on the API for preregistered survey research, so the outage currently blocks our PAP freeze gate.

Reproduction steps:
1. Authenticate via `scripts/semantic_scholar_cli.py` (wrapper uses the key from .env) on macOS 26.1 / Python 3.12.7; seed 20251016.
2. Run: `python scripts/semantic_scholar_cli.py search --query "childhood trusted adult mentorship adult depression buffer" --limit 5 --output lit/queries/loop_042/query_001.json`
3. Response: HTTP 403 with body `{ "message": "Forbidden" }` (see attached JSON with timestamp 2025-11-08T22:01:30Z).

Attachments / links:
- Latest failing payload: lit/queries/loop_042/query_001.json
- Prior attempts + rate-limit history: lit/semantic_scholar_waiver_loop013.md (covers loops 008–042)
- Environment snapshot (seed, git SHA, pip): artifacts/session_info.txt

Could you confirm whether the key was rate-limited, disabled, or requires re-verification? We are happy to provide log excerpts or rotate to a new key if needed. Please advise on the expected timeline so we can unblock preregistered confirmatory work.

Thank you,
Science Agent (experiment_4b)
```

**Next Steps Once Submitted**
1. Record submission timestamp, ticket ID, and any immediate support responses in `analysis/decision_log.csv`.
2. Update `lit/semantic_scholar_waiver_loop013.md` with the ticket reference and add a short summary to `notebooks/research_notebook.md`.
3. If Support provides a remediation checklist, mirror it in `artifacts/state.json` under `next_actions` so the PAP gate reflects the new requirements.
