# Reproducibility Report

- Generated: 2025-11-04T08:04:55.414659+00:00
- Git HEAD: 242d9a5c7cfe773fc0e6108ea99d7f069928acbe
- Model: gpt-5-codex
- Network access: not specified

Artifacts:
- artifacts/session_info.txt  (env + packages + HEAD)
- artifacts/checksums.json    (dataset file hashes)
- artifacts/last_model_raw.txt (last raw LLM output)
- analysis/decision_log.csv   (append-only action log)

Principle: Any figure/table/result must be regenerable from code committed at the cited HEAD,
with the recorded seed and environment. If randomness is used, it must be seeded and logged.
