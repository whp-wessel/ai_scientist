# Reproducibility Report

- Generated: 2025-10-17T22:58:59Z
- Git HEAD: 339ce7b923eb728ac094bd53738fa8615f944d44
- Model: gpt-5-codex

Artifacts refreshed this loop:
- `artifacts/session_info.txt` — updated Python/platform, git status, and pip freeze.
- `artifacts/checksums.json` — SHA-256 hashes for `childhoodbalancedpublic_original.csv` and derived MI datasets.
- `analysis/code/run_mi_robustness.py` — bug fix to restore complete-case ordered-logit pathway.
- `tables/robustness_hyp001_mi_scenarios_*`, `tables/robustness_hyp002_mi_scenarios_*`, `analysis/imputation/robustness_hyp[001|002]_mi_scenarios.md` — regenerated via seeded command below.

Regeneration command (exploratory robustness):
```bash
python analysis/code/run_mi_robustness.py --seed 20251016
```

Principle: Any figure/table/result must be regenerable from code committed at the cited HEAD,
with the recorded seed and environment. Randomness is seeded with `20251016` per `config/agent_config.yaml`.
