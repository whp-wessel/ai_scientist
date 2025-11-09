# Sensitivity Manifest (Loop 068)
All commands run from the repo root with seed `20251016` (see `config/agent_config.yaml` + `artifacts/seed.txt`). Re-run each block to regenerate the proxy/design-effect artifacts.

---

### Scenario 1 — Pseudo-weight sweep (DEFF ∈ {1.0, 1.25, 1.5})
```bash
python analysis/code/pseudo_weight_sensitivity.py \
  --config config/agent_config.yaml \
  --seed 20251016 \
  --draws 400 \
  --scenarios 1.0 1.25 1.5 \
  --output-dir outputs/sensitivity_pseudo_weights
```
Outputs:
- `outputs/sensitivity_pseudo_weights/pseudo_weights_deff_100.json`
- `outputs/sensitivity_pseudo_weights/pseudo_weights_deff_125.json`
- `outputs/sensitivity_pseudo_weights/pseudo_weights_deff_150.json`

---

### Scenario 2 — Design-effect grid (DEFF ∈ {1.0, 1.25, 1.5, 2.0})
```bash
python analysis/code/design_effect_grid.py \
  --input analysis/results.csv \
  --deffs 1.0 1.25 1.5 2.0 \
  --output-csv outputs/sensitivity_design_effect_grid.csv \
  --output-md outputs/sensitivity_design_effect_grid.md
```
Outputs:
- `outputs/sensitivity_design_effect_grid.csv`
- `outputs/sensitivity_design_effect_grid.md`

---

### Scenario 3 — Pseudo-replicate jackknife (k = 6 clusters)
```bash
python analysis/code/pseudo_replicates.py \
  --config config/agent_config.yaml \
  --seed 20251016 \
  --k 6 \
  --results analysis/results.csv \
  --output-dir outputs/sensitivity_replicates
```
Output:
- `outputs/sensitivity_replicates/sensitivity_replicates_summary.json`

---

### Confirmatory + negative-control rebuild
```bash
python analysis/code/run_models.py \
  --hypothesis all \
  --config config/agent_config.yaml \
  --seed 20251016 \
  --draws 400 \
  --output-prefix outputs/run_models_loop056

python analysis/code/negative_control.py \
  --config config/agent_config.yaml \
  --seed 20251016 \
  --output outputs/negative_control_loop056.json

python analysis/code/summarize_results.py \
  --json-paths outputs/run_models_loop056_H1.json \
               outputs/run_models_loop056_H2.json \
               outputs/run_models_loop056_H3.json \
               outputs/negative_control_loop056.json \
  --output-csv analysis/results_pre_bh.csv

python analysis/code/calc_bh.py \
  --config config/agent_config.yaml \
  --input-csv analysis/results_pre_bh.csv \
  --output-csv analysis/results.csv \
  --summary-json artifacts/bh_summary.json

python analysis/code/build_results_summary.py \
  --input analysis/results.csv \
  --output-csv tables/results_summary.csv \
  --output-md tables/results_summary.md
```
Outputs:
- `analysis/results_pre_bh.csv`
- `analysis/results.csv`
- `artifacts/bh_summary.json`
- `tables/results_summary.csv`
- `tables/results_summary.md`
