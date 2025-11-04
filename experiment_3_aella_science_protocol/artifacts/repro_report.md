# Reproducibility Report

- Generated: 2025-11-04T07:58:50.000000+00:00
- Git HEAD: 69d17b44c48c47be238e9bd33b3bc2a437608da3
- Model: gpt-5-codex
- Network access: enabled

Artifacts:
- artifacts/session_info.txt  (env + packages + HEAD)
- artifacts/checksums.json    (dataset file hashes)
- artifacts/last_model_raw.txt (last raw LLM output)
- analysis/decision_log.csv   (append-only action log)
- papers/main/MANIFEST.md     (PAP freeze manifest; tag `pap-freeze-20251104` to be created)
- reports/findings_v0.1.md    (Markdown manuscript scaffold; parity with LaTeX required)

Principle: Any figure/table/result must be regenerable from code committed at the cited HEAD,
with the recorded seed and environment. If randomness is used, it must be seeded and logged.
