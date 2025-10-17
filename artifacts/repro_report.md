# Reproducibility Report

- Generated: 2025-10-17T16:02:12.466227+00:00
- Git HEAD: b64b541d2c8214a2d1155f05ee777bab848596da
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

## 2025-10-17T16:18:33+00:00 — Loop 13 Notes
- Extended `analysis/code/run_pap_models.py` to support MI-pooled HC1 linear (HYP-001) and ordered-logit (HYP-002) analyses seeded at 20251016.
- Ran `python analysis/code/run_pap_models.py --hypotheses HYP-001 HYP-002 --mode exploratory --dataset childhoodbalancedpublic_original.csv --mi-dataset data/derived/childhoodbalancedpublic_mi_prototype.csv.gz --config config/agent_config.yaml`.
- Generated reproducible bundles: `tables/exploratory_hyp001_mi_linear_*` and `tables/exploratory_hyp002_mi_ordered_logit_*` plus manifest metadata JSON.
