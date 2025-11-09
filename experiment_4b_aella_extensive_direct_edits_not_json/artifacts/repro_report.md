# Reproducibility Report

- Generated: 2025-11-09T14:09:33.605041+00:00
- Git HEAD: 385ac7cd48c6e1bbc8a452c408ec5c6dbe6b8ade
- Model: gpt-5-codex-mini
- Network access: not specified

Artifacts:
- artifacts/session_info.txt  (env + packages + HEAD)
- artifacts/checksums.json    (dataset file hashes)
- artifacts/llm_raw/loop_XXX.txt (per-loop raw LLM output snapshots)
- analysis/decision_log.csv   (append-only action log)

Principle: Any figure/table/result must be regenerable from code committed at the cited HEAD,
with the recorded seed and environment. If randomness is used, it must be seeded and logged.
