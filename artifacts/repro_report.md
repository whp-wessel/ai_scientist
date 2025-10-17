# Reproducibility Report

- Generated: 2025-10-17T15:47:07.263255+00:00
- Git HEAD: d5197f80a3b37e4e1d98469706e7bc84f3c40fde
- Model: gpt-5-codex

Artifacts:
- artifacts/session_info.txt  (env + packages + HEAD)
- artifacts/checksums.json    (dataset file hashes)
- artifacts/last_model_raw.txt (last raw LLM output)
- analysis/decision_log.csv   (append-only action log)

Principle: Any figure/table/result must be regenerable from code committed at the cited HEAD,
with the recorded seed and environment. If randomness is used, it must be seeded and logged.

## 2025-10-17T15:59:28+00:00 — Loop 12 Notes
- Refreshed `artifacts/checksums.json` for `childhoodbalancedpublic_original.csv` and imputed derivatives (SHA-256).
- Authored & executed `python analysis/code/run_pap_models.py --hypotheses HYP-003 --mode exploratory --dataset childhoodbalancedpublic_original.csv --config config/agent_config.yaml --seed 20251016`.
- Outputs stored under `tables/exploratory_hyp003_ordered_logit_*` with disclosure checks (k>=10).
