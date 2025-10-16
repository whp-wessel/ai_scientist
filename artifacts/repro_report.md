# Reproducibility Report

- Generated: 2025-10-16T11:40:56.965197+00:00
- Git HEAD: 696fc6314e3d1709b3862b4ac1b90603e49b8406
- Model: codex-high

Artifacts:
- artifacts/session_info.txt  (env + packages + HEAD)
- artifacts/checksums.json    (dataset file hashes)
- artifacts/last_model_raw.txt (last raw LLM output)
- analysis/decision_log.csv   (append-only action log)

Principle: Any figure/table/result must be regenerable from code committed at the cited HEAD,
with the recorded seed and environment. If randomness is used, it must be seeded and logged.
