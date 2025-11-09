# Reproducibility Report

- Generated: 2025-11-09T16:35:05.839754+00:00
- Git HEAD: f2133a38440022a395507c9ffd47d9e471b64dd5
- Model: gpt-5-codex-mini
- Network access: not specified

Artifacts:
- artifacts/session_info.txt  (env + packages + HEAD)
- artifacts/checksums.json    (dataset file hashes)
- artifacts/llm_raw/loop_XXX.txt (per-loop raw LLM output snapshots)
- analysis/decision_log.csv   (append-only action log)

Principle: Any figure/table/result must be regenerable from code committed at the cited HEAD,
with the recorded seed and environment. If randomness is used, it must be seeded and logged.
