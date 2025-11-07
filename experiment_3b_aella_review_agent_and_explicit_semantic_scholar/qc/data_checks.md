# Data Checks — Loop 000 (Bootstrap)

- **Dataset availability**: `childhoodbalancedpublic_original.csv` located at repo root.
  Verified shape 14,443 × 718 via `python - <<'PY'` snippet logged in notebook.
- **PII scan**: Manual column skim indicates primarily self-reported categorical items; no
  direct identifiers detected. Continue to monitor free-text columns before release.
- **Survey design metadata**: Missing — placeholder `docs/survey_design.yaml` created.
- **Missingness diagnostics**: Deferred; plan to run `analysis/code/01_prepare_data.py`
  once drafted.
- **Random seed discipline**: Seed `20251016` recorded in `config/agent_config.yaml` and
  referenced across artifacts.
- **Regeneration command**: `python analysis/scripts/data_checks.py --seed 20251016`
  (script to be implemented; current file maintained manually for transparency).
- **Next steps**: Address Tasks `T-001` (weights) and `T-002` (exploratory summaries)
  before advancing phases.
