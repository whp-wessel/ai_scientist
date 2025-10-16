# Reproducibility Report

- Generated: 2025-10-16T13:44:45.407504+00:00
- Git HEAD: dc9b7f16dcc3a54d9fa541c21c4b69de3c540cac
- Model: gpt-5-codex

Artifacts:
- artifacts/session_info.txt  (env + packages + HEAD)
- artifacts/checksums.json    (dataset file hashes)
- artifacts/last_model_raw.txt (last raw LLM output)
- analysis/decision_log.csv   (append-only action log)

Principle: Any figure/table/result must be regenerable from code committed at the cited HEAD,
with the recorded seed and environment. If randomness is used, it must be seeded and logged.
