# Reproducibility Report

- Generated: 2025-11-04T08:16:02.615416+00:00
- Git HEAD: 64e6e787e7a2f36dcb130e96f0af965ab588cde4
- Model: gpt-5-codex
- Network access: not specified

Artifacts:
- artifacts/session_info.txt  (env + packages + HEAD)
- artifacts/checksums.json    (dataset file hashes)
- artifacts/last_model_raw.txt (last raw LLM output)
- analysis/decision_log.csv   (append-only action log)

Principle: Any figure/table/result must be regenerable from code committed at the cited HEAD,
with the recorded seed and environment. If randomness is used, it must be seeded and logged.
