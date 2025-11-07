# Reproducibility Report

- Generated: 2025-11-04T20:32:02.823751+00:00
- Git HEAD: d53bce85f61abf2bcf88ac7a28661f78171b2e1c
- Model: gpt-5-codex
- Network access: not specified

Artifacts:
- artifacts/session_info.txt  (env + packages + HEAD)
- artifacts/checksums.json    (dataset file hashes)
- artifacts/last_model_raw.txt (last raw LLM output)
- analysis/decision_log.csv   (append-only action log)

Principle: Any figure/table/result must be regenerable from code committed at the cited HEAD,
with the recorded seed and environment. If randomness is used, it must be seeded and logged.
