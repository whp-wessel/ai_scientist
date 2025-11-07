# Data Checks — Loop 000 (Bootstrap Refresh)

- **Dataset availability**: `childhoodbalancedpublic_original.csv` present at repo root.
  Verified via:
  ```bash
  python - <<'PY'
  import pandas as pd
  df = pd.read_csv('childhoodbalancedpublic_original.csv')
  print({'rows': len(df), 'cols': df.shape[1]})
  PY
  ```
  Output: `{'rows': 14443, 'cols': 718}`.
- **Dtype warnings**: pandas flagged mixed types in column 68. Action: coerce
  affected columns explicitly inside `analysis/code/01_prepare_data.py` and log
  conversions.
- **PII scan**: Spot check of first 10 columns shows categorical survey content
  with no direct identifiers. Continue monitoring open-text items before release.
- **Survey design metadata**: `docs/survey_design.yaml` still a placeholder. Task
  `T-001` tracks confirmation of any weight/strata/cluster variables.
- **Missingness diagnostics**: Deferred until cleaning script exists; plan to run
  `python analysis/code/01_prepare_data.py --task missingness --seed 20251016` (to
  be implemented) before PAP freeze.
- **Random seed discipline**: Seed `20251016` recorded in `config/agent_config.yaml`
  and reiterated here for every deterministic command.
- **Regeneration command for this checklist**:
  ```bash
  python analysis/scripts/data_checks.py --seed 20251016 \
    --input childhoodbalancedpublic_original.csv \
    --out qc/data_checks.md
  ```
  (Script stub to be added; for now this Markdown is maintained manually with the
  verified command history logged above.)
- **Next steps**: Address Tasks `T-001` (design metadata) and `T-002`
  (exploratory weighted summaries) before advancing beyond the literature phase.
