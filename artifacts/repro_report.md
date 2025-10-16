# Reproducibility Report

- Generated: 2025-10-16T13:12:45.972100+00:00
- Git HEAD: e12e2427b093bc8704256e36b56fbcc248236b47
- Model: gpt-5-codex

Artifacts:
- artifacts/session_info.txt  (env + packages + HEAD)
- artifacts/checksums.json    (dataset file hashes)
- artifacts/last_model_raw.txt (last raw LLM output)
- analysis/decision_log.csv   (append-only action log)
- tables/exploratory_selflove_by_abuse.{csv,md}
- tables/exploratory_networth_by_classchild.{csv,md}
- tables/exploratory_missingness_key_vars.{csv,md}
- artifacts/eda_weighted_summaries_metadata.json

Principle: Any figure/table/result must be regenerable from code committed at the cited HEAD,
with the recorded seed and environment. If randomness is used, it must be seeded and logged.
Regenerate exploratory summaries via `python analysis/code/eda_weighted_summaries.py`.
