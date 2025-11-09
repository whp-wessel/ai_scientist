# Reproducibility Report

- Generated: 2025-11-09T20:50:57.534481+00:00
- Git HEAD: cf2dc879dfaed87147e25c7222a0735ce6ca3dbc
- Model: gpt-5-codex-mini
- Network access: not specified

Artifacts:
- artifacts/session_info.txt  (env + packages + HEAD)
- artifacts/checksums.json    (dataset file hashes)
- artifacts/llm_raw/loop_XXX.txt (per-loop raw LLM output snapshots)
- analysis/decision_log.csv   (append-only action log)

Principle: Any figure/table/result must be regenerable from code committed at the cited HEAD,
with the recorded seed and environment. If randomness is used, it must be seeded and logged.
