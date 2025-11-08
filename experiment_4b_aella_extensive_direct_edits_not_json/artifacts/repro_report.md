# Reproducibility Report

- Generated: 2025-11-08T17:56:06.753429+00:00
- Git HEAD: 42a0e9ce18a87ff3e6a8a695a117063a8c903c0d
- Model: gpt-5-codex
- Network access: not specified

Artifacts:
- artifacts/session_info.txt  (env + packages + HEAD)
- artifacts/checksums.json    (dataset file hashes)
- artifacts/llm_raw/loop_XXX.txt (per-loop raw LLM output snapshots)
- analysis/decision_log.csv   (append-only action log)

Principle: Any figure/table/result must be regenerable from code committed at the cited HEAD,
with the recorded seed and environment. If randomness is used, it must be seeded and logged.
