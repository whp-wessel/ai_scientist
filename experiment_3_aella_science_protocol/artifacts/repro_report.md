# Reproducibility Report

- Generated: 2025-11-04T10:06:22.652440+00:00
- Git HEAD: ffe91f833c9a26d866c37e605dc408249457fe1d
- Model: gpt-5-codex
- Network access: enabled (per environment context)

Artifacts:
- artifacts/session_info.txt  (env + packages + HEAD; regenerate via `python analysis/code/update_repro_checkpoints.py --config config/agent_config.yaml`)
- artifacts/checksums.json    (dataset file hashes; same command as above)
- artifacts/last_model_raw.txt (last raw LLM output)
- analysis/decision_log.csv   (append-only action log)

Principle: Any figure/table/result must be regenerable from code committed at the cited HEAD,
with the recorded seed and environment. If randomness is used, it must be seeded and logged.
