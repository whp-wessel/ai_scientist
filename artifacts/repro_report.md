# Reproducibility Report

- Generated: 2025-10-16T14:49:02.552214+00:00
- Git HEAD: b2842e207e408d50f534df67cdff01a4a7022ca6
- Model: gpt-5-codex

Artifacts:
- artifacts/session_info.txt  (env + packages + HEAD)
- artifacts/checksums.json    (dataset file hashes)
- artifacts/last_model_raw.txt (last raw LLM output)
- analysis/decision_log.csv   (append-only action log)

Principle: Any figure/table/result must be regenerable from code committed at the cited HEAD,
with the recorded seed and environment. If randomness is used, it must be seeded and logged.
