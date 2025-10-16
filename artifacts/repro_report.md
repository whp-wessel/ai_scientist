# Reproducibility Report

- Generated: 2025-10-16T14:13:49.189213+00:00
- Git HEAD: a499ace4b2d44835f8f20d78fbd75df0c758f9da
- Model: gpt-5-codex

Artifacts:
- artifacts/session_info.txt  (env + packages + HEAD)
- artifacts/checksums.json    (dataset file hashes)
- artifacts/last_model_raw.txt (last raw LLM output)
- analysis/decision_log.csv   (append-only action log)

Principle: Any figure/table/result must be regenerable from code committed at the cited HEAD,
with the recorded seed and environment. If randomness is used, it must be seeded and logged.
