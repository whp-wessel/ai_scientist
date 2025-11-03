# Reproducibility Report

- Generated: 2025-11-03T21:01:32.061663+00:00
- Git HEAD: 8c0ef89540eeca55f33029583aa3e1b8c3f9ff73
- Model: gpt-5-codex
- Network access: not specified

Artifacts:
- artifacts/session_info.txt  (env + packages + HEAD)
- artifacts/checksums.json    (dataset file hashes)
- artifacts/last_model_raw.txt (last raw LLM output)
- analysis/decision_log.csv   (append-only action log)

Principle: Any figure/table/result must be regenerable from code committed at the cited HEAD,
with the recorded seed and environment. If randomness is used, it must be seeded and logged.
