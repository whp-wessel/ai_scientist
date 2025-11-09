# Manuscript MANIFEST

## Artifacts and Regeneration Commands
- `papers/main/manuscript.tex`: edit via deterministic text editor; compile using `latexmk -pdf papers/main/manuscript.tex` (once figures/tables exist).
- `papers/main/manuscript.md`: keep in sync with TeX file; manual edit only.
- `papers/main/imrad_outline.md`: update manually after each major analysis milestone.
- `figures/dag_design.png` / `figures/dag_design.json`: regenerate via `python analysis/code/plot_dag.py --output-png figures/dag_design.png --output-json figures/dag_design.json`.
- `reports/identification.md`: manual edit; reference DAG command above and cite disclosure guardrails + descriptive stance.
- `analysis/results.csv`, `analysis/results_pre_bh.csv`, `artifacts/bh_summary.json`, `tables/results_summary.csv`, and `tables/results_summary.md`: rerun the PAP pipeline with the deterministic seed via the `analysis/code/run_models.py`, `analysis/code/negative_control.py`, `analysis/code/summarize_results.py`, `analysis/code/calc_bh.py`, and `analysis/code/build_results_summary.py` chain.
- `outputs/sensitivity_pseudo_weights/pseudo_weights_deff_*.json`, `outputs/sensitivity_design_effect_grid.csv/.md`, and `outputs/sensitivity_replicates/sensitivity_replicates_summary.json`: regenerate via the three sensitivity scripts enumerated in `analysis/sensitivity_manifest.md` (pseudo weights, design effect grid, pseudo replicates), each commanded with `--seed 20251016`.
- `qc/disclosure_check_loop_059.md`: rerun `python analysis/code/disclosure_check.py --tables-dir tables --figures-dir figures --min-n 10 --seed 20251016 --output-md qc/disclosure_check_loop_059.md`.
- `qc/measures_validity.md` and `artifacts/measurement_validity_loop059.json`: rerun `python analysis/code/measure_validity_checks.py --config config/agent_config.yaml --output-md qc/measures_validity.md --output-json artifacts/measurement_validity_loop059.json`.
- `qc/strobe_sampl_checklist.md`: update the combined STROBE+SAMPL checklist whenever Table/Figure assets change, citing `analysis/results.csv`, `tables/results_summary.*`, and the relevant QC artifacts.
- `lit/evidence_map.csv`, `lit/bibliography.bib`, and `lit/bibliography.json`: append DOI-backed rows (e.g., from the crossref fallback for loop 059) every time new literature queries or claims are introduced; record each query path under `lit/queries/loop_059/`.
- Build outputs (PDF/DOCX) will be stored under `papers/main/output/` (dir TBD) with commands logged here.

## Seeds and Versions
- Global seed: 20251016 (`config/agent_config.yaml`).
- PAP freeze tag: TBD (record here once created).

## Notes
- Add each confirmatory figure/table with: relative path, generating script + command, git commit hash.
