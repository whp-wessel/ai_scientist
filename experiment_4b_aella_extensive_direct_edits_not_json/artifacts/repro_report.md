# Reproducibility Report

- Generated: 2025-11-08T13:59:16.058312+00:00
- Git HEAD: a551cb030b9a55a257995c202758cc2ba2941e5a
- Model: gpt-5-codex
- Network access: not specified

Artifacts:
- artifacts/session_info.txt  (env + packages + HEAD)
- artifacts/checksums.json    (dataset file hashes)
- artifacts/llm_raw/loop_XXX.txt (per-loop raw LLM output snapshots)
- analysis/decision_log.csv   (append-only action log)

Principle: Any figure/table/result must be regenerable from code committed at the cited HEAD,
with the recorded seed and environment. If randomness is used, it must be seeded and logged.
