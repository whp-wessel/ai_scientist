# Reproducibility Report

- Generated: 2025-11-09T20:10:51.209096+00:00
- Git HEAD: 6f87d44f02f6f2d7f5398f9bd71d8abb6ef11ed6
- Model: gpt-5-codex-mini
- Network access: not specified

Artifacts:
- artifacts/session_info.txt  (env + packages + HEAD)
- artifacts/checksums.json    (dataset file hashes)
- artifacts/llm_raw/loop_XXX.txt (per-loop raw LLM output snapshots)
- analysis/decision_log.csv   (append-only action log)

Principle: Any figure/table/result must be regenerable from code committed at the cited HEAD,
with the recorded seed and environment. If randomness is used, it must be seeded and logged.
