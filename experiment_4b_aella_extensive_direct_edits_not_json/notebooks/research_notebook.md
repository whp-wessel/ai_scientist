# Research Notebook

## Loop 000 — Literature Phase (Bootstrap)

**Context.** Initialized the repository structure, verified availability of the raw CSV (14,443 × 718), and drafted placeholder governance documents (`docs/codebook.json`, `docs/survey_design.yaml`, `config/agent_config.yaml`). Logged all actions in `analysis/decision_log.csv`.

**Exploratory actions (reproducible).**
1. Inspect variable headers and shape  
   ```bash
   python - <<'PY'
   import csv
   from pathlib import Path
   path = Path("childhoodbalancedpublic_original.csv")
   with path.open() as f:
       reader = csv.reader(f)
       header = next(reader)
       rows = sum(1 for _ in reader)
   print("rows", rows)
   print("cols", len(header))
   print("first_40", header[:40])
   PY
   ```
2. Draft governance files (direct edits recorded via git) to ensure every downstream script has deterministic paths and seeds.

**LaTeX coordination.** The PAP and notebook reference `papers/main/manuscript.tex`; once draft prose begins, every notebook update will be mirrored in LaTeX and `papers/main/build_log.txt` will record each `latexmk -pdf papers/main/manuscript.tex` invocation.

**Next actions.**
- Flesh out measurement validity (`qc/measures_validity.md`) for PAP variables.
- Resolve Semantic Scholar authentication so literature scaffolding can advance beyond placeholders.
- Build minimal data-processing scripts under `analysis/code/` to lock down deterministic cleaning.
