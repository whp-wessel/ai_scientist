# Science Agent — Survey Research Protocol

> **Reproducibility Principle (applies to EVERYTHING):**  
> All artifacts, including exploratory analyses and **experiments**, must be fully reproducible and deterministic given the recorded seed and environment. Every figure, table, and result must be regenerable from committed code and documented commands. Any randomness must be seeded and logged. The runner snapshots environment info and dataset checksums; the agent must maintain MANIFEST-style regeneration notes for each paper.

## Objective
Within the provided survey dataset, conduct rigorous, reproducible social‑science style research:
1) perform background scoping, 2) generate hypotheses grounded in data and literature,
3) pre‑register a Pre‑Analysis Plan (PAP), 4) test hypotheses with survey‑aware methods,
5) report findings with effect sizes, uncertainty, limitations, and open questions.

## Inputs
- Dataset path(s): `data/raw/`, `data/clean/` (parquet/csv)
- Codebook: `docs/codebook.json` (names, labels, types, value maps)
- Survey design: `docs/survey_design.yaml` (weight var, strata, cluster, replicate weights if any)
- Project config: `config/agent_config.yaml`
- Allowed tools: local Python/R, web search for literature only

## Deliverables (create/update on each loop)
- `notebooks/research_notebook.md` — running narrative with links to artifacts
- `analysis/pre_analysis_plan.md` — frozen before confirmatory tests
- `analysis/decision_log.csv` — timestamped actions, inputs, rationale, outputs
- `analysis/hypotheses.csv` — registry (see template below)
- `analysis/results.csv` — per hypothesis: estimates, SEs, CIs, p/q, n, notes
- `figures/*` — publication‑grade plots (PNG + .json specs if programmatic)
- `tables/*` — machine‑readable tables (CSV) + human‑readable (MD)
- `lit/bibliography.bib` and `lit/bibliography.json` — references with DOIs/URLs + access dates
- `lit/evidence_map.csv` — concept → sources → quality rating → notes
- `artifacts/state.json` — persistence: backlog, checkpoints, and next actions
- `reports/findings_v{X}.{Y}.md` — versioned report with changelog
- **Reproducibility artifacts (runner also maintains)**
  - `artifacts/session_info.txt` — Python/platform, packages (`pip freeze`), git HEAD
  - `artifacts/checksums.json` — SHA‑256 hashes of data files
  - `artifacts/repro_report.md` — human‑readable summary and commitments
  - `artifacts/seed.txt` — run seed; all code must use this seed for randomness

### Submission‑ready Deliverables (per paper)
Maintain for each paper under `papers/<slug>/`:

- `manuscript.md` — journal‑style manuscript with YAML metadata (STROBE‑aligned)
- `pap.yaml` — **executable PAP** referencing variables, models, subsets, and seeds
- `strobe_checklist.md` — reporting checklist (auto‑filled, human‑reviewed)
- `cover_letter.md` — tailored to target journal
- `response_to_reviewers.md` — created post‑review
- `figures/*` — final PNG (300 dpi) + programmatic specs
- `tables/*` — CSV + Markdown (suppressed for small cells)
- `supplement/*` — robustness, alternative codings, diagnostics
- `submission/*` — rendered `manuscript.docx`/`pdf` and required forms
- `MANIFEST.md` — **regeneration commands** (paths, seeds, commit SHA) for all artifacts

Maintain a cross‑paper index:
- `artifacts/papers_index.csv` — `slug,title,status,target_journal,pap_version,report_version,lead_variables,notes`

## Autonomy Boundaries
- **Do**: inspect data, engineer variables, run survey‑aware analyses, search literature, draft reports.
- **Do not**: upload data externally, expose PII, or claim causal effects without design support.
- **Escalate** to human when: survey weights missing but codebook mentions them; contradictory results persist across methods; small cells (<k) appear; power < 0.6 for primary hypotheses.

## Statistical Standards
- Use design-based estimators with weights/strata/clusters (or state that SRS is assumed).
- Report effect sizes + 95% CIs; avoid binary “significant/non‑significant” language.
- Multiplicity: control **FDR (Benjamini–Hochberg at q=0.05)** for each hypothesis family.
- Missing data: describe mechanism (MCAR/MAR/MNAR), report missingness patterns; if using imputation, prefer **multiple imputation** and pool estimates.
- Robustness: prespecify at least two robustness checks per key finding (e.g., alternate codings, alternative link functions, exclusion/inclusion criteria).

## Literature & Bibliography
- For each claim, add ≥1 peer‑reviewed or authoritative source. Save DOI/URL + date accessed.
- Maintain `lit/evidence_map.csv`: concept → sources → quality rating → notes.
- Summarize gaps and open questions at the end of each loop.

## Reproducibility
- **Hard rule:** Everything—including **experiments**—must be reproducible. Any randomized procedure (e.g., CV splits, imputations, bootstrap) must set and log the global `seed` from `config/agent_config.yaml`, and record it in outputs and `MANIFEST.md`.
- Pin environment (record `session_info.txt`), set random seeds, and save dataset checksums (`artifacts/checksums.json`).
- Every figure/table must be regenerable from code saved in `analysis/code/` or `papers/<slug>/` with exact command lines.
- Log all transformations; never overwrite raw data.
- Manuscripts must cite the git commit SHA and PAP commit/tag used to generate results.
- When PAPs are frozen, record a commit/tag and include it in `MANIFEST.md`.

## Multi‑paper Planning
- Split into multiple papers when ≥2 non‑overlapping hypothesis families have distinct primary outcomes/audiences. Move relevant hypotheses to the new `<slug>`.
- Guardrail: a hypothesis can appear in **one** confirmatory PAP at a time.

## Journal Targeting & Compliance
- Maintain `config/publishing.yaml` with: target journals, style (AMA/APA/Harvard), word/figure limits, open‑data policy, ethics/COI requirements.
- Render manuscripts to DOCX and PDF if tools available.
- Block submission until STROBE items are complete and small‑cell suppression has been verified.

## Workflow (each loop)
1. **Sync state**: load `artifacts/state.json`; append a new row to `analysis/decision_log.csv`.
2. **Reproducibility checkpoint**: confirm `session_info.txt` and `checksums.json` exist and are up to date; write/update `papers/<slug>/MANIFEST.md` if working on a paper.
3. **Data hygiene**: validate schema, types, missingness, weights; emit `qc/data_checks.md`.
4. **EDA (exploratory only)**: describe distributions, weighted summaries, and potential associations. Label outputs “Exploratory”.
5. **Hypothesis generation**: propose hypotheses consistent with available variables and theory. Add to `hypotheses.csv` with a family label (for FDR).
6. **Pre‑Analysis Plan (PAP)**: for selected hypotheses, specify outcomes, predictors, subsets, model, estimand, and robustness checks. Freeze PAP (`status=frozen`) before confirmatory tests and tag commit.
7. **Confirmatory analysis**: execute PAP exactly; produce `results.csv`. Adjust for survey design; compute effect sizes, CIs, p, q (FDR). Record seeds used.
8. **Robustness & sensitivity**: run pre‑specified checks; document deviations (if any) and rationale.
9. **Literature integration**: map findings to evidence; update `bibliography.*` and `evidence_map.csv`.
10. **Reporting**: update `research_notebook.md` and `reports/findings_vX.Y.md` with:
    - abstract, methods, results, limitations, generalizability, ethics/privacy notes, and open questions.
11. **Backlog & next actions**: update `artifacts/state.json` with prioritized tasks and stop/ask‑for‑help flags.
12. **Git checkpoints**: after PAP freeze, results updates, figures/tables, bibliography changes, report bumps, and backlog updates (see “Version Control & Checkpointing”).

## Logging (replace “thinking” with Decision Log)
Every action must write a row to `analysis/decision_log.csv` with:
- timestamp, actor (“agent”), action, inputs (files/vars), brief rationale (≤40 words),
- code path executed, key outputs (files/IDs), and outcome (success/fail).

## Internet Use
- Allowed for literature/background only. For each source, store: title, authors, venue, year, DOI/URL, access date, and a one‑sentence relevance note. No scraping of data tables into the analysis unless explicitly approved.

## Privacy & Disclosure
- Suppress any cell n < k (default k=10) in public tables/plots; round or bin as needed.
- No attempts at re-identification. Respect data license restrictions recorded in `config/agent_config.yaml`.

## Output Style
- All narrative in Markdown, tables in CSV + Markdown, plots as PNG (300dpi) + source code.
- Each hypothesis and result carries a **Confidence Rating** (Low/Medium/High) based on robustness and power.

## Termination & Scheduling
- Stop when: task is fully completed (including deliverables), no new validated hypotheses remain, quality checks fail repeatedly, or a human review is requested.

---

### Templates

**Hypothesis registry (`analysis/hypotheses.csv`)**
- `id`, `family`, `description`, `outcome_var`, `predictors`, `controls`, `population/subset`, `estimand`, `status` (proposed|selected|in_PAP|tested), `notes`

**Results (`analysis/results.csv`)**
- `hypothesis_id`, `model`, `n_unweighted`, `n_weighted`, `estimate`, `se`, `ci_low`, `ci_high`, `p_value`, `q_value`, `effect_size_metric`, `robustness_passed` (Y/N), `limitations`, `confidence_rating`

**Decision Log (`analysis/decision_log.csv`)**
- `ts`, `action`, `inputs`, `rationale_short`, `code_path`, `outputs`, `status`

---

### Config stub (`config/agent_config.yaml`)
```yaml
time_budget_minutes_per_loop: 15
fdr_q: 0.05
small_cell_threshold_k: 10
report_variables_of_interest: ["outcome1","outcome2"]
allowed_languages: ["python","r"]
python_packages: ["pandas","numpy","statsmodels","linearmodels","matplotlib","scipy"]
r_packages: ["survey","srvyr","mice","ggplot2","sandwich","clubSandwich"]
seed: 20251016

Version Control & Checkpointing (NEW)
Use Git for every important milestone and right after finishing any task.
Never commit secrets (.env, API keys). Keep a config/.env.example and use .gitignore.
Store large binaries (≥10 MB) via Git LFS. Never commit raw PII.
Milestones that must trigger a commit + push
PAP created or frozen (tag commit)
hypotheses.csv updated (add/remove/edit)
New/updated results.csv or robustness checks completed
New figure/table added to figures/ or tables/
New/updated reports/findings_vX.Y.md
artifacts/state.json / backlog updated or task finished
Any schema/qc change in qc/* or docs/*
Commit message convention
<type>(scope): <what changed> [refs]
Types: feat | fix | refactor | docs | chore | data | analysis | report | qc
Scope: pap | hypotheses | results | figures | tables | report | qc | state | infra
Example: analysis(results): add HYP-12 confirmatory estimates + BH FDR q=0.05
Standard commands
git add -A
git commit -m "<message>"
git pull --rebase origin main || true
git push origin main
Tagging milestones
When you bump reports/findings_vX.Y.md, also tag:
git tag -a vX.Y -m "Milestone: findings vX.Y (PAP vX)"
git push origin vX.Y
Branching (optional)
Use feat/<short-topic> for larger work; PR into main with a short checklist (QC passed, PAP frozen, small-cell suppression checked).
Workflow — add Git checkpoints (EDIT)
After PAP freeze: git commit + tag
After confirmatory results.csv: git commit
After robustness: git commit
After bibliography/evidence_map updates: git commit
After reporting (research_notebook.md, findings_vX.Y.md): git commit + tag
After backlog update: git commit
Safety rails for Git (NEW)
.gitignore must include: .env, data/raw/*, temporary caches, any export with PII.
If small-cell suppression modifies tables, commit only the suppressed versions.
If a push fails (network/conflict), write an entry to analysis/decision_log.csv with status=fail and the git error; retry next loop after git pull --rebase.
Submission‑ready guidance (agent)
Ensure papers/<slug>/MANIFEST.md lists exact commands (with seeds) to regenerate every output.
Cite git commit SHA in manuscript.md and PAP tag for confirmatory results.
Block submission until strobe_checklist.md is complete and small-cell suppression checks pass.