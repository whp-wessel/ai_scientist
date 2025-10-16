# Reproducibility Report

- Generated: 2025-10-16T14:01:05.361891+00:00
- Git HEAD: 91532b68b623fb8ea919cb57a659947aa7dacfb0
- Model: gpt-5-codex

Artifacts:
- artifacts/session_info.txt  (env + packages + HEAD)
- artifacts/checksums.json    (dataset file hashes)
- artifacts/last_model_raw.txt (last raw LLM output)
- analysis/decision_log.csv   (append-only action log)

Principle: Any figure/table/result must be regenerable from code committed at the cited HEAD,
with the recorded seed and environment. If randomness is used, it must be seeded and logged.
