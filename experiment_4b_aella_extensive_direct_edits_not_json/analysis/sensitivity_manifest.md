# Sensitivity Manifest

All scripts below run with seed `20251016` (config/agent_config.yaml) so the pseudo-weight, design-effect grid, and pseudo-replicate outputs remain deterministic. Commands should be rerun from the repository root.

- **Pseudo-weight scenarios (DEFF ∈ {1.0, 1.25, 1.5})**  
  Command:  
  ````bash
  python analysis/code/pseudo_weight_sensitivity.py --config config/agent_config.yaml --seed 20251016 --draws 400 --scenarios 1.0 1.25 1.5
  ````  
  Outputs: `outputs/sensitivity_pseudo_weights/pseudo_weights_deff_100.json`, `..._125.json`, `..._150.json`

- **Design-effect grid**  
  Command:  
  ````bash
  python analysis/code/design_effect_grid.py --input analysis/results.csv --deffs 1.0 1.25 1.5 2.0 --output-csv outputs/sensitivity_design_effect_grid.csv --output-md outputs/sensitivity_design_effect_grid.md
  ````  
  Outputs: `outputs/sensitivity_design_effect_grid.csv`, `outputs/sensitivity_design_effect_grid.md`

- **Pseudo-replicate jackknife (k=6)**  
  Command:  
  ````bash
  python analysis/code/pseudo_replicates.py --config config/agent_config.yaml --seed 20251016 --k 6 --output-dir outputs/sensitivity_replicates --results analysis/results.csv
  ````  
  Output: `outputs/sensitivity_replicates/sensitivity_replicates_summary.json`
