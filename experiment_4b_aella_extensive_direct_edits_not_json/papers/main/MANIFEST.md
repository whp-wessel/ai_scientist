# Manuscript MANIFEST

## Artifacts and Regeneration Commands
- `papers/main/manuscript.tex`: edit via deterministic text editor; compile using `latexmk -pdf papers/main/manuscript.tex` (once figures/tables exist).
- `papers/main/manuscript.md`: keep in sync with TeX file; manual edit only.
- `papers/main/imrad_outline.md`: update manually after each major analysis milestone.
- `figures/dag_design.png` / `figures/dag_design.json`: regenerate via `python analysis/code/plot_dag.py --output-png figures/dag_design.png --output-json figures/dag_design.json`.
- `reports/identification.md`: manual edit; reference DAG command above and cite disclosure guardrails + descriptive stance.
- Build outputs (PDF/DOCX) will be stored under `papers/main/output/` (dir TBD) with commands logged here.

## Seeds and Versions
- Global seed: 20251016 (`config/agent_config.yaml`).
- PAP freeze tag: TBD (record here once created).

## Notes
- Add each confirmatory figure/table with: relative path, generating script + command, git commit hash.
