# Reproducibility Report

- Generated: 2025-11-04T09:31:47.439103+00:00
- Git HEAD: 8a63d3c3a86cf796952fa51c0bc30845d6b530eb
- Model: gpt-5-codex
- Network access: not specified

Artifacts:
- artifacts/session_info.txt  (env + packages + HEAD)
- artifacts/checksums.json    (dataset file hashes)
- artifacts/last_model_raw.txt (last raw LLM output)
- analysis/decision_log.csv   (append-only action log)

Principle: Any figure/table/result must be regenerable from code committed at the cited HEAD,
with the recorded seed and environment. If randomness is used, it must be seeded and logged.
