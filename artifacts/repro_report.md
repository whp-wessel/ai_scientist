# Reproducibility Report

- Generated: 2025-10-16T13:00:14.744932+00:00
- Git HEAD: 72e6938223322d4be5120073cf6e8ebaec409a37
- Model: gpt-5-codex

Artifacts:
- artifacts/session_info.txt  (env + packages + HEAD)
- artifacts/checksums.json    (dataset file hashes)
- artifacts/last_model_raw.txt (last raw LLM output)
- analysis/decision_log.csv   (append-only action log)

Principle: Any figure/table/result must be regenerable from code committed at the cited HEAD,
with the recorded seed and environment. If randomness is used, it must be seeded and logged.
