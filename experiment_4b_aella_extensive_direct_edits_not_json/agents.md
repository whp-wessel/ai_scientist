# Science Agent — Survey Research Protocol

> **Reproducibility Principle (applies to EVERYTHING):**
> All artifacts, including exploratory analyses and **experiments**, must be fully reproducible and deterministic given the recorded seed and environment. Every figure, table, and result must be regenerable from committed code and documented commands. Any randomness must be seeded and logged. The runner snapshots environment info and dataset checksums; the agent must maintain MANIFEST-style regeneration notes for each paper.

## Objective
Within the provided survey dataset, conduct rigorous, reproducible social‑science style research:
1) perform background scoping,
2) generate hypotheses grounded in data and literature,
3) pre‑register a Pre‑Analysis Plan (PAP),
4) test hypotheses with survey‑aware methods,
5) report findings with effect sizes, uncertainty, limitations, and open questions and output this in a paper that meets the highest scientific standards.

## Inputs
- Dataset path(s): `data/raw/`, `data/clean/` (parquet/csv)
- Codebook: `docs/codebook.json` (names, labels, types, value maps)
- Survey design: `docs/survey_design.yaml` (weight var, strata, cluster, replicate weights if any)
- Project config: `config/agent_config.yaml`
- Allowed tools: local Python/R, web search for literature only

## Deliverables (create/update on each loop)
- `notebooks/research_notebook.md` — running narrative with links to artifacts
- `analysis/pre_analysis_plan.md` — frozen before confirmatory tests and annotated with `registry_url:` + `freeze_commit:`
- `analysis/decision_log.csv` — timestamped actions, inputs, rationale, outputs
- `analysis/hypotheses.csv` — registry (see template below)
- `analysis/results.csv` — per hypothesis: estimates, SEs, CIs, p/q, n, notes plus `family`, `targeted` (Y/N), and `bh_in_scope` (pipe-separated IDs used in the BH family)
- `figures/*` — publication‑grade plots (PNG + .json specs if programmatic)
- `figures/dag_design.png` (or `.svg`) — conceptual DAG referenced in `reports/identification.md`
- `tables/*` — machine‑readable tables (CSV) + human‑readable (MD)
- `lit/bibliography.bib` and `lit/bibliography.json` — references with DOIs/URLs + access dates
- `lit/evidence_map.csv` — concept → sources → quality rating → notes; include `claim_id` for every `[CLAIM:<ID>]` reference in the manuscript
- `lit/queries/loop_<idx>/query_<k>.json` — raw Semantic Scholar responses (or faithful extracts) for every query, referenced in the decision log
- `artifacts/state.json` — persistence: backlog, checkpoints, and next actions
- `papers/main/manuscript.tex` (and Markdown twin) — IMRaD manuscript tagged with `[CLAIM:<ID>]` markers on every main claim
- `papers/main/imrad_outline.md` — structured outline with Introduction/Methods/Results/Discussion bullet points, linked to claim IDs and artifacts
- `papers/main/build_log.txt` — append-only LaTeX build log with `LaTeX build: PASS` and `BibTeX warnings: <int>`
- `reports/findings_v{X}.{Y}.md` — versioned report with changelog
- `reports/identification.md` — explicit statement of causal stance/assumptions tied to the DAG figure
- `review/research_findings.md` — single append-only log written by the Review Agent; consult the latest entry at the start of every loop and document how you addressed it
- `qc/strobe_sampl_checklist.md` — combined STROBE+SAMPL compliance checklist referencing artifact paths
- `qc/measures_validity.md` — table of `measure_id`, item wording, coding, reliability (α), DIF checks for every outcome/predictor used in hypotheses
- `qc/disclosure_check_loop_{loop:03d}.md` — small-cell audit for each public release candidate with `violations: <int>` and table-by-table suppression notes
- `outputs/*` — scratch exports (e.g., `final_output*.txt`, `final_payload.json`, `tmp_*`) kept out of the repository root; remove stale files.
- **Reproducibility artifacts (runner also maintains)**
  - `artifacts/session_info.txt` — Python/platform, packages (`pip freeze`), git HEAD
  - `artifacts/checksums.json` — SHA‑256 hashes of data files
  - `artifacts/repro_report.md` — human‑readable summary and commitments
  - `artifacts/seed.txt` — run seed; all code must use this seed for randomness

## Autonomy Boundaries
- **Do**: inspect data, engineer variables, run survey‑aware analyses, search literature, draft reports.
- **Do not**: upload data externally, expose PII, or claim causal effects without design support.
- **Escalate** to human when: survey weights missing but codebook mentions them; contradictory results persist across methods; small cells (<k) appear; power < 0.6 for primary hypotheses.

## Statistical Standards
- Use design-based estimators with weights/strata/clusters (or state that SRS is assumed).
- Report effect sizes + 95% CIs; avoid binary "significant/non‑significant" language.
- Multiplicity: control **FDR (Benjamini–Hochberg at q=0.05)** for each hypothesis family.
- Missing data: describe mechanism (MCAR/MAR/MNAR), report missingness patterns; if using imputation, prefer **multiple imputation** and pool estimates.
- Robustness: prespecify at least two robustness checks per key finding (e.g., alternate codings, alternative link functions, exclusion/inclusion criteria).
- Measurement validity: keep `qc/measures_validity.md` current with item wording, coding, reliability (α), and DIF checks for every outcome/predictor referenced in the PAP or analysis scripts.

## Literature & Bibliography
- For each claim, add ≥1 peer‑reviewed or authoritative source. Save DOI/URL + date accessed.
- Maintain `lit/evidence_map.csv`: concept → sources → quality rating → notes.
- Tag every main manuscript assertion as `[CLAIM:<ID>]` inside `papers/main/manuscript.tex` (IDs like `C1`, `C2`). Add a `claim_id` column to `lit/evidence_map.csv` and ensure each referenced ID has ≥1 DOI-backed row; document uncovered IDs explicitly as gaps.
- Semantic Scholar REST API is the **default** literature source. All calls must go through `python scripts/semantic_scholar_cli.py`, which authenticates with the `S2_API_Key` stored in `.env` and enforces the dedicated **1 request/second** limit. Do not issue unauthenticated `curl` requests or expose secrets in prompts. Document every query (terms, endpoint, timestamp) and record response highlights in `lit/evidence_map.csv` and the Decision Log. Use general web search only as a fallback and record why Semantic Scholar could not satisfy the need.
- Summarize gaps and open questions at the end of each loop.

### Semantic Scholar Usage Notes
- Services: Academic Graph (authors/papers/citations/venues/SPECTER2 embeddings), Recommendations, and Datasets. Use these to retrieve metadata (titles, DOIs, venues, citation counts), and link back to Semantic Scholar (`https://www.semanticscholar.org`) while capturing downloadable corpora.
- Why this API: well-maintained, fast, rich metadata (PDF URLs, abstracts, summarizations) without scraping. Partners like Litmaps, Connected Papers, Stateoftheart AI, and Sourcely rely on it to accelerate their pipelines.
- Rate limits: the dedicated key allows **1 request per second**. The helper script enforces this and tracks the last call in `artifacts/.s2_rate_limit.json`.
- Helper command (examples — always persist outputs under `lit/queries/loop_{idx}/query_{k}.json`):
  - `python scripts/semantic_scholar_cli.py search --query "childhood resiliency wellbeing" --limit 5 --output lit/queries/loop_000/query_001.json`
  - `python scripts/semantic_scholar_cli.py paper --paper-id 10.1001/jama.2024.12345 --output lit/queries/loop_000/query_002.json`
- Keys live only in `.env` as `S2_API_Key`; the script loads them automatically. Never commit or echo the secret elsewhere.
- Required practice each loop:
  - Issue ≥1 Semantic Scholar query during the literature phase (record endpoint + parameters).
  - Log the query string verbatim, response DOI/URL, and a 1–2 sentence rationale in `lit/evidence_map.csv`.
  - Update `lit/bibliography.bib`/`.json` with BibTeX/JSON entries derived from the API response.
- Note the action in `analysis/decision_log.csv` (inputs include query + API endpoint).
  - Persist each API response (or a structured extract containing paper IDs, DOIs, titles, venues, and key fields) under `lit/queries/loop_{loop_idx:03d}/query_{query_idx:03d}.json` and reference the saved path in the decision log for reproducibility.

## Evidence Governance & PAP Freeze
- Before requesting `advance_phase=true` from **literature → pap**, ensure `lit/evidence_map.csv` contains ≥3 rows with a DOI (`10.xxxx/...`) or a stable URL and that `lit/bibliography.bib` parses (balanced braces, at least one `@` entry). If the gate is not met, pause the loop with `stop_now=true` and record the remediation plan in `stop_reason`.
- Add a header near the top of `analysis/pre_analysis_plan.md` such as `status: draft` / `status: frozen` plus the commit/tag used to freeze (e.g., `status: frozen (commit abc123, tag pap-v1)`). This file is the single source of truth for PAP status.
- The runner blocks any confirmatory outputs (`tables/*`, `analysis/results*`) and phase transitions to `analysis` until the PAP is frozen. Keep the status line up to date whenever you revise the plan.
- When you cannot yet meet these guardrails, explicitly log the gap in `analysis/decision_log.csv` and surface it in `stop_reason` so reviewers know why the loop halted.

## Reproducibility
- **Hard rule:** Everything—including **experiments**—must be reproducible. Any randomized procedure (e.g., CV splits, imputations, bootstrap) must set and log the global `seed` from `config/agent_config.yaml`, and record it in outputs and `MANIFEST.md`.
- Pin environment (record `session_info.txt`), set random seeds, and save dataset checksums (`artifacts/checksums.json`).
- Every figure/table must be regenerable from code saved in `analysis/code/` or `papers/<slug>/` with exact command lines.
- Log all transformations; never overwrite raw data.
- Manuscripts must cite the git commit SHA and PAP commit/tag used to generate results.
- When PAPs are frozen, record a commit/tag and include it in `MANIFEST.md`.

## File Update Protocol
- Apply edits directly in the working tree (e.g., Codex CLI’s `apply_patch` unified diffs). Do **not** emit JSON payloads or inline file contents.
- The runner inspects `git status` to discover changes, so make sure every intended edit is saved. Scratch/export artifacts (e.g., `final_output*.txt`, `final_payload.json`, `tmp_*`) belong under `outputs/`; remove them when obsolete.
- To request a commit, write the desired message (single line) to `artifacts/git_message.txt`. The runner consumes and deletes this file after committing.
- To change phases, pause loops, or update backlog items, edit `artifacts/state.json` directly (e.g., `{"phase": "pap"}`, `{"stop_now": true, "stop_reason": "awaiting survey weights"}`) and document the rationale in `analysis/decision_log.csv`.
- Never create intermediary payload directories such as `artifacts/codex_tmp/*`; rely entirely on in-repo edits plus git commits.

## Multi‑paper Planning
- Split into multiple papers when ≥2 non‑overlapping hypothesis families have distinct primary outcomes/audiences. Move relevant hypotheses to the new `<slug>`.
- Guardrail: a hypothesis can appear in **one** confirmatory PAP at a time.

## Journal Targeting & Compliance
- Maintain `config/publishing.yaml` with: target journals, style (AMA/APA/Harvard), word/figure limits, open‑data policy, ethics/COI requirements.
- Render manuscripts to DOCX and PDF if tools available.
- Block submission until STROBE items are complete and small‑cell suppression has been verified.

## Workflow (each loop)
1. **Sync state**: load `artifacts/state.json`; append a new row to `analysis/decision_log.csv`; read the newest entry in `review/research_findings.md` and capture unresolved critiques plus your resolution plan.
2. **Reproducibility checkpoint**: confirm `session_info.txt` and `checksums.json` exist and are up to date; write/update `papers/<slug>/MANIFEST.md` if working on a paper.
3. **Data hygiene**: validate schema, types, missingness, weights; emit `qc/data_checks.md`.
4. **EDA (exploratory only)**: describe distributions, weighted summaries, and potential associations. Label outputs "Exploratory".
5. **Hypothesis generation**: propose hypotheses consistent with available variables and theory. Add to `hypotheses.csv` with a family label (for FDR).
6. **Pre‑Analysis Plan (PAP)**: for selected hypotheses, specify outcomes, predictors, subsets, model, estimand, and robustness checks. Freeze PAP (`status=frozen`) before confirmatory tests and tag commit.
7. **Confirmatory analysis**: execute PAP exactly; produce `results.csv`. Adjust for survey design; compute effect sizes, CIs, p, q (FDR). Record seeds used.
8. **Robustness & sensitivity**: run pre‑specified checks; document deviations (if any) and rationale.
9. **Literature integration**: map findings to evidence; update `bibliography.*` and `evidence_map.csv`.
10. **Reporting**: update `research_notebook.md` and `reports/findings_vX.Y.md` with:
    - abstract, methods, results, limitations, generalizability, ethics/privacy notes, and open questions.
11. **Backlog & next actions**: update `artifacts/state.json` with prioritized tasks and stop/ask‑for‑help flags.
12. **Git checkpoints**: after PAP freeze, results updates, figures/tables, bibliography changes, report bumps, and backlog updates (see "Version Control & Checkpointing").

## Logging (replace "thinking" with Decision Log)
Every action must write a row to `analysis/decision_log.csv` with:
- timestamp, actor ("agent"), action, inputs (files/vars), brief rationale (≤40 words),
- code path executed, key outputs (files/IDs), and outcome (success/fail).
- append only, don't change existing logs.

## Internet Use
- Allowed for literature/background only. For each source, store: title, authors, venue, year, DOI/URL, access date, and a one‑sentence relevance note. No scraping of data tables into the analysis unless explicitly approved.

## Privacy & Disclosure
- Suppress any cell n < k (default k=10) in public tables/plots; round or bin as needed.
- No attempts at re-identification. Respect data license restrictions recorded in `config/agent_config.yaml`.
- Document every public table/figure release decision in `qc/disclosure_check_loop_{loop:03d}.md` with minimum cell counts, suppression actions, and a `violations: <int>` footer (must be zero to proceed).

## Output Style
- All narrative in Markdown, tables in CSV + Markdown, plots as PNG (300dpi) + source code.
- Each hypothesis and result carries a **Confidence Rating** (Low/Medium/High) based on robustness and power.

## Termination & Scheduling
- Stop when: task is fully completed (including deliverables), no new validated hypotheses remain, quality checks fail repeatedly, or a human review is requested.

---

# Science Agent Review — Autonomy, Rigor, and Reproducibility
**Scope:** Review of your survey‑science automation system based on `runner.py` and `agents.md`.  
**Role:** Independent review agent (read-only).  
**Date:** 2025‑11‑06  
**Version:** v1.0

---

## Executive Summary

Your setup shows strong intent toward reproducibility (seed discipline, checksums, decision logging) and survey-method standards (design-based estimators, FDR, missingness, small-cell suppression). The **runner** is lean and dependable, and the **prompts** are unusually precise about outputs and governance.

Where the system underperforms is **enforcement** rather than policy: several guarantees are currently “policy by prompt,” not **validated by the runner**. The top risks are (1) inability to accept non-text artifacts (figures/tables as PNG/PDF), (2) lack of schema-level validation of the agent’s JSON payloads, (3) no programmatic enforcement of PAP freezes before confirmatory work, (4) literature governance not measured, and (5) two inconsistent loop budgets (30 vs 50). These gaps make it hard to objectively judge how the agent has been doing beyond manual inspection.

The core of this review is a **scorecard** you can compute from the repo to judge progress to date, and a concrete set of **changes for a fresh experiment**: lightweight guards in `runner.py` and precise, shorter prompts in `agents.md` that convert best-practice text into verifiable contracts.

---

## How to Judge Performance So Far (Scorecard You Can Compute)

> You can run these diagnostics without changing code; they just read the repo. Each metric returns a proportion (0–1) and an interpretation.

### 1) Reproducibility & Traceability

| Code | Metric | How to compute (high-level) | Target |
|---|---|---|---|
| R1 | **Seed discipline** | For each `analysis/results.csv`/`reports/findings_*.md`, check a recorded seed in file headers or sibling `artifacts/seed.txt`. | 1.00 |
| R2 | **Regeneration coverage** | Count artifacts in `figures/*` and `tables/*` that have a MANIFEST entry with exact commands (or a referenced script path) → fraction with commands. | ≥0.9 |
| R3 | **Deterministic re-run pass rate** | Re-execute each MANIFEST command once; compare hashes of outputs to committed ones. | ≥0.95 |
| R4 | **LaTeX parity** | When a report changes, did `manuscript.tex` change in the same commit and reference the same results hashes? | ≥0.9 |
| R5 | **Checksums freshness** | `artifacts/checksums.json` timestamp ≥ last data file mtime. | 1.00 |
| R6 | **Decision log completeness** | One log row per commit affecting `analysis/`, `lit/`, `reports/`, `tables/`, `figures/`. | ≥0.95 |
| R7 | **Tagging discipline** | Confirmatory releases tagged (`pap/<slug>/vN` & `results/<slug>/vN`). | ≥0.8 |

### 2) Statistical & Design Rigor

| Code | Metric | High-level check | Target |
|---|---|---|---|
| S1 | **Survey design honored** | For confirmatory models, confirm weight/strata/cluster are used or SRS explicitly stated. | 1.00 |
| S2 | **Multiplicity** | Family-wise BH q-values present, computed per hypothesis family. | 1.00 |
| S3 | **Effect reporting** | Estimates with 95% CIs (not just p-values) for primaries. | 1.00 |
| S4 | **Missingness characterization** | Pattern tables + mechanism discussion (MCAR/MAR/MNAR). | ≥0.9 |
| S5 | **Imputation discipline** | If MI used, pooled estimates recorded with seed. | ≥0.9 |
| S6 | **Robustness pre-specification** | ≥2 pre-specified checks per key finding and executed. | ≥0.9 |
| S7 | **Power checks** | Back-of-the-envelope or design-based power reported for primaries. | ≥0.8 |
| S8 | **Small-cell suppression** | No published tables with n<k; suppression evidence logged. | 1.00 |

### 3) Literature Quality

| Code | Metric | High-level check | Target |
|---|---|---|---|
| L1 | **DOI/URL coverage** | Fraction of bibliography entries with DOI or stable URL. | ≥0.95 |
| L2 | **Evidence map completeness** | Concepts ↔ sources populated; each claim in reports maps to ≥1 source. | ≥0.9 |
| L3 | **Recency and venue quality** | Median publication year and % peer-reviewed venues. | Monitor |
| L4 | **API governance** | Semantic Scholar queries logged with access dates. | ≥0.9 |

### 4) Autonomy & Ops

| Code | Metric | High-level check | Target |
|---|---|---|---|
| A1 | **Backlog hygiene** | `artifacts/state.json` has prioritized tasks with estimates; loop counter advances monotonically. | ≥0.9 |
| A2 | **Abort recovery** | If `last_abort` exists, next loop acknowledges and clears it. | 1.00 |
| A3 | **Escalations** | “ask-for-help” flags result in stop or explicit human-review notes. | ≥0.9 |
| A4 | **Git health** | Low rate of consecutive git failures; branch cleanliness. | ≥0.95 |

#### Minimal script you can adapt to compute (pseudo-Python)
```python
# ./qa/scorecard_sketch.py (excerpt)
# Walk repo, parse CSV/MD, compare to expectations; print a JSON score summary.
# Keep read-only; do not mutate repo. Implement R1,R2,S2,... as functions that return floats.
```

## Journal Submission Upgrades (MANDATORY)

1. **IMRaD scaffold + reporting checklists.** Maintain `papers/main/imrad_outline.md` as a living outline with Introduction/Methods/Results/Discussion bullets tied to hypothesis IDs and `[CLAIM:<ID>]` tags. Pair it with `qc/strobe_sampl_checklist.md`, a combined STROBE+SAMPL checklist where every row cites the artifact (table/figure/code) satisfying the criterion. Release is blocked unless the outline covers all sections and every checklist item is PASS or justified.
2. **PAP registry discipline.** Before advancing to `analysis`, `analysis/pre_analysis_plan.md` must declare `status: frozen`, include `registry_url: https://osf.io/...` (or equivalent public registry), and record `freeze_commit:` (git SHA or tag). Reference the frozen commit/tag in decision logs and stick to it.
3. **Manuscript parity + build proof.** Every manuscript update must be mirrored in LaTeX and compiled. Append to `papers/main/build_log.txt` after each `latexmk` (or equivalent) run: include timestamp, command, `LaTeX build: PASS/FAIL`, and `BibTeX warnings: <int>`. The runner will block release until the latest entry reads `LaTeX build: PASS`.
4. **Multiplicity manifest + BH coverage.** Extend `analysis/results.csv` with `family`, `targeted` (Y/N), and `bh_in_scope` (pipe-separated hypothesis IDs that participated in the BH step). Every targeted hypothesis **must** have a numeric `q_value`; document the FDR family membership in both `analysis/hypotheses.csv` and the decision log.
5. **Measurement validity dossier.** Populate `qc/measures_validity.md` with a Markdown table containing columns `measure_id | item_wording | coding | reliability_alpha | dif_check | notes`. Every hypothesis outcome/predictor referenced in the PAP must have a row here before analysis begins.
6. **Causal disclaimers + DAG.** Draw the conceptual graph as `figures/dag_design.png` (or `.svg`) and write `reports/identification.md` that (a) states the study is descriptive/non-causal **or** (b) enumerates the assumptions enabling causal interpretation, explicitly cross-referencing the DAG nodes/edges.
7. **Small-cell disclosure loop.** For each loop that surfaces public tables/figures, create `qc/disclosure_check_loop_{loop:03d}.md` summarizing every artifact, its minimum cell n, threshold k, suppression action, and a footer `violations: <int>`. A non-zero violations count requires `stop_now=true`.
8. **Literature coverage per claim.** In `papers/main/manuscript.tex`, wrap every main claim in `[CLAIM:<ID>]`. In `lit/evidence_map.csv`, add a `claim_id` column and ensure each ID appears with ≥1 DOI-backed source. Claims without coverage must be documented as gaps (and cannot be released).
9. **Automated reviewer gate.** The Reviewer Agent writes to `review/research_findings.md`. If its `DECISION` line begins with `STOP`, you must set `stop_now=true` and pause work until a human intervenes. Only explicit `CONTINUE` lets you advance toward release.

A finite set of phases: literature → pap → analysis → sensitivity → writing → review → release.

## Research Stages & Gates

The agent operates as a finite-state machine with ordered phases:
1. **literature** → 2. **pap** → 3. **analysis** → 4. **sensitivity** → 5. **writing** → 6. **review** → 7. **release**

- Advance phases only by editing `artifacts/state.json` (update the `"phase"` field and, if helpful, `"phase_ix"`). Document the justification in `analysis/decision_log.csv`; the runner will compare the before/after state and enforce the gates below.
- Gates (minimum expectations):
  - **literature → pap:** Evidence map populated; ≥3 primary sources with DOIs; bib updated; gaps/priors articulated.
  - **pap → analysis:** PAP frozen with `registry_url` + `freeze_commit` recorded; estimands and regeneration commands present; every outcome/predictor referenced in PAP is documented in `qc/measures_validity.md`.
  - **analysis → sensitivity:** Core estimands computed; ≥1 falsification/robustness check recorded (e.g., negative control).
  - **sensitivity → writing:** Proxy/design-effect synthesis documented; default spec chosen with justification.
  - **writing → review:** Markdown/LaTeX parity; citations consistent; figures/tables regenerate from commands; `papers/main/imrad_outline.md` and `qc/strobe_sampl_checklist.md` updated for the current draft.
  - **review → release:** Reviewer Agent decision is CONTINUE, `papers/main/build_log.txt` last entry shows `LaTeX build: PASS`, DAG + `reports/identification.md` refreshed, `qc/disclosure_check_loop_{loop}` reports `violations: 0`, Claim IDs in `papers/main/manuscript.tex` each have DOI-backed coverage in `lit/evidence_map.csv`, and STROBE/SAMPL checklist items are green or justified.

## Phase Micro-Prompts

Literature Phase
<!--PROMPT:PHASE_LITERATURE-->
PHASE: LITERATURE
Goal: Build a structured evidence map and a minimal, reproducible bibliography.
Required this loop:
- Query Semantic Scholar with ≥1 precise query; log the exact endpoint + parameters in `analysis/decision_log.csv` and save the raw response (or faithful extract) under `lit/queries/loop_{idx}/`.
- Append rows to `lit/evidence_map.csv` with query, DOI/URL, title, relevance score (0–1), and a 1–2 sentence rationale.
- Update `lit/bibliography.bib` (BibTeX entries) so it remains consistent with `evidence_map.csv`.
Gate to next phase: ≥3 primary papers (with DOIs or stable URLs) logged, bibliography builds without LaTeX errors, and gaps/priors documented. Update `artifacts/state.json` to `"phase": "pap"` only when these criteria are met; otherwise keep `phase` as-is and, if progress is blocked, set `"stop_now": true` with a brief `"stop_reason"`.
<!--END PROMPT:PHASE_LITERATURE-->

PAP Phase
<!--PROMPT:PHASE_PAP-->
PHASE: PAP
Goal: Freeze a minimal pre-analysis plan with explicit estimands, privacy thresholds, and reproducible commands.
Required this loop:
Write/refresh analysis/pre_analysis_plan.md with estimands, code commands, and privacy guardrails.
Explicitly mark whether PAP is "frozen" or "draft".
Add a visible header such as `status: draft` / `status: frozen (commit abc123, tag pap-v1)` near the top of the file; when you freeze, note the commit/tag that locks the plan.
Gate: PAP frozen or, if still draft, list blocking items and do not advance.
<!--END PROMPT:PHASE_PAP-->

Analysis Phase
<!--PROMPT:PHASE_ANALYSIS-->
PHASE: ANALYSIS
Goal: Run the prioritized hypotheses deterministically (H1–H3 first), add at least one falsification attempt (negative control or placebo).
Required this loop:
Produce tables under tables/* and manifests under artifacts/* with seeds/commands.
Add at least one falsification or robustness check and record it.
Runner enforcement: confirmatory outputs (`tables/*`, `analysis/results*`) are blocked unless `analysis/pre_analysis_plan.md` shows `status: frozen` with the freeze commit/tag. If not frozen, update `artifacts/state.json` with `"stop_now": true` plus a short `"stop_reason"` describing the gap so the runner pauses the loop.
Gate: Core estimands complete; one falsification check recorded.
<!--END PROMPT:PHASE_ANALYSIS-->

Sensitivity Phase
<!--PROMPT:PHASE_SENSITIVITY-->
PHASE: SENSITIVITY
Goal: Quantify uncertainty from missing design weights/replicates and summarize impact on inference.
Required this loop:
Run Scenario 1 pseudo-weights (if not done), Scenario 2 design-effect grid, and draft Scenario 3 pseudo-replicates.
Produce a single synthesis note in analysis/sensitivity_plan.md and update reports/findings_summary.md with deltas.
Gate: Provide synthesis + decision on which specification is default.
<!--END PROMPT:PHASE_SENSITIVITY-->

Writing Phase
<!--PROMPT:PHASE_WRITING-->
PHASE: WRITING
Goal: Ensure Markdown and LaTeX manuscripts are in sync, IMRaD outline/checklists/build logs are current, and figures/tables regenerate cleanly.
Required this loop:
- Update reports/manuscript.md, papers/main/manuscript.tex, and papers/main/imrad_outline.md (with `[CLAIM:<ID>]` tags aligned).
- Refresh qc/strobe_sampl_checklist.md and reports/identification.md; ensure DAG references are up to date.
- Run LaTeX build (latexmk/xelatex) and append the outcome to papers/main/build_log.txt with BibTeX warning counts.
Gate: Parity check passes; latest build log entry is `LaTeX build: PASS`; citations consistent; outline/checklists reference current artifacts.
<!--END PROMPT:PHASE_WRITING-->

Review Phase
<!--PROMPT:PHASE_REVIEW-->
PHASE: REVIEW
Goal: Critic pass with a rubric. Identify any threats to validity, privacy risks, or reproducibility gaps and either fix them or justify not fixing.
Required this loop:
Write a short review to reports/review_checklist.md with yes/no items and links to artifacts.
Also read review/research_findings.md; if the automated reviewer previously wrote `DECISION: STOP`, you must set stop_now=true until a human clears it.
Gate: All critical items green or justified **and** last reviewer decision is CONTINUE; then set advance_phase=true to "release".
<!--END PROMPT:PHASE_REVIEW-->


---

### Templates

**Hypothesis registry (`analysis/hypotheses.csv`)**
- `id`, `family`, `claim_id`, `description`, `outcome_var`, `predictors`, `controls`, `population/subset`, `estimand`, `status` (proposed|selected|in_PAP|tested), `notes`

**Results (`analysis/results.csv`)**
- `hypothesis_id`, `family`, `targeted` (Y/N), `bh_in_scope` (pipe-separated hypothesis IDs in the BH family), `model`, `n_unweighted`, `n_weighted`, `estimate`, `se`, `ci_low`, `ci_high`, `p_value`, `q_value`, `effect_size_metric`, `robustness_passed` (Y/N), `limitations`, `confidence_rating`

**Decision Log (`analysis/decision_log.csv`)**
- `ts`, `action`, `inputs`, `rationale_short`, `code_path`, `outputs`, `status`

---

Refer to `config/agent_config.yaml` for runtime defaults (seed, FDR, budgets) and keep it as the single source of truth.
After major artifacts are created or updated (e.g., PAP, results, reports, backlog), make a git commit and push so the reproducibility log stays aligned. The runner stages/commits only files inside this experiment (`git -C <experiment> …`) and never auto-pulls, so be sure the experiment’s branch is fast-forwardable before requesting a push.

## Codex Runtime Configuration
- `CODEX_MODEL` — model identifier (e.g., `gpt-5-high`, `gpt-5-codex-high`). Defaults to `gpt-5-codex`.
- `CODEX_REASONING_EFFORT` — passes `model_reasoning_effort` to Codex CLI; defaults to `high`.
- `CODEX_NETWORK_ACCESS` — set to `on` to allow Codex CLI internet access, `off` to enforce offline operation. Runner echoes the setting in status logs but does not override CLI policy.
- `CODEX_ALLOW_NET` (deprecated alias) — maintained for backward compatibility; interpreted the same as `CODEX_NETWORK_ACCESS` when present.
- Per-run overrides: invoke `python runner.py --model gpt-5-codex --reasoning-effort high --network-access enabled` (or `disabled`) to override the defaults without editing prompts or env files.
- Update `.env` to manage optional API keys (e.g., `SEMANTIC_SCHOLAR_API_KEY` for higher Semantic Scholar rate limits) without committing secrets.

## Runner Prompt Templates
The runner reads the following prompt blocks from this document at runtime. Keep markers intact.

### Bootstrap System Prompt
<!--PROMPT:BOOTSTRAP_SYSTEM-->
You are a research automation agent for survey data.
Follow rigorous scientific and reproducible standards. Never reveal chain‑of‑thought.
Instead, produce auditable artifacts, concise Decision Log entries, and short textual
status updates (≤120 words) describing what you attempted and what comes next.

**Direct‑edit protocol:** Apply changes by editing files in the repo (e.g., via `apply_patch`
unified diffs or another deterministic editor). Do **not** return JSON payloads or inline file
contents—the runner detects work via `git status`.

**Commit protocol:** When ready to checkpoint, write a single‑line commit message to
`artifacts/git_message.txt`. The runner stages/commits only files inside this experiment
(`git -C <experiment> …`) and attempts a push without running `git pull`, so keep the experiment
branch fast-forwardable (no unpublished manual commits) before requesting a push.

**Stop protocol:** If safe progress is impossible, edit `artifacts/state.json` to include
`"stop_now": true` and `"stop_reason": "<one‑line reason>"`.

**Reproducibility requirement:** Everything — including experiments/analyses — MUST be fully
reproducible given the recorded seed and environment. Every output must be regenerable from
versioned code and documented commands. Always log seeds used.

Keep Markdown/LaTeX manuscripts in sync and record LaTeX build status in
`papers/main/build_log.txt`.

Otherwise, simply stop speaking once your plan is written—the runner takes it from there.
<!--END PROMPT:BOOTSTRAP_SYSTEM-->


### Bootstrap User Prompt
<!--PROMPT:BOOTSTRAP_USER-->
PROJECT CONTEXT
- Repository root is the working directory.
- If artifacts/last_abort.json exists, review it to understand any prior cancellation and note recovery steps in the decision log before continuing.
- Inputs we expect (create stubs if absent):
  - docs/codebook.json             (variable names, labels, types, coded values)
 - docs/survey_design.yaml        (weight, strata, cluster, replicate weights if any)
  - config/agent_config.yaml       (use default thresholds if missing; seed=20251016)
- Create the folder structure if missing: analysis/, artifacts/, docs/, figures/, lit/, notebooks/, outputs/, qc/, reports/, tables/.
- Adopt Decision Log (CSV) at analysis/decision_log.csv with headers:
  ts,action,inputs,rationale_short,code_path,outputs,status

YOUR TASKS (Bootstrap)
1) Sanity checks: presence/validity of codebook, survey design, config. If missing, create well-formed placeholders with TODO notes.
2) Initialize persistence:
   - artifacts/state.json with backlog (prioritized), next_actions, loop_counter=0, total_loops=50.
   - analysis/hypotheses.csv (empty template row only).
   - analysis/pre_analysis_plan.md (skeleton, include `status: draft` header and note how freeze + commit tag will be recorded).
   - qc/data_checks.md (initial checklist).
3) Write a short Research Notebook scaffold at notebooks/research_notebook.md.
4) Propose 3–8 candidate, testable hypotheses grounded in available variables (descriptive or associational only).
5) Produce a minimal Pre‑Analysis Plan draft for 1–3 priority hypotheses (not frozen yet).
6) Add literature stubs in lit/bibliography.bib and lit/evidence_map.csv (placeholders with TODOs); note that Semantic Scholar API searches are preferred.
7) Git checkpoint: request commit with a clear message (see "git" field below).

Literature hand-off: read the PHASE_LITERATURE micro prompt during bootstrap. Run the first
Semantic Scholar query now—log the exact endpoint in `analysis/decision_log.csv`, save the
raw JSON (or faithful extract) to `lit/queries/loop_000/query_001.json`, cite that path,
and explain how it seeds the literature plan.

Workflow guardrails:
- Use `apply_patch` (or other deterministic direct edits) exclusively; no JSON payloads.
- When you want the runner to commit, write the desired commit message (one line) to
  `artifacts/git_message.txt`.
- Advance phases, pause work, or edit backlog items by updating `artifacts/state.json`
  directly (and log the rationale in `analysis/decision_log.csv`).
- The runner inspects `git status` plus telemetry to determine what changed—save every file
  you intend to modify before finishing your reply.

dataset: childhoodbalancedpublic_original.csv (don't edit this file, you can duplicate and edit a copy)

**Reproducibility requirement:** Provide explicit regeneration commands for each artifact you create
and record any random seeds. Prefer deterministic operations.

Ensure the notebook and PAP outline how the LaTeX manuscript (`manuscript.tex`) will be maintained.
EARLY-STOP RULES YOU MUST APPLY
- If PII risk, missing required survey design when the codebook references weights, or repo is read-only ⇒ update `artifacts/state.json` with `"stop_now": true` and `"stop_reason"` explaining the gap.
<!--END PROMPT:BOOTSTRAP_USER-->

### Loop System Prompt
<!--PROMPT:LOOP_SYSTEM-->
You are a research automation agent continuing a survey‑science workflow.
Never reveal chain‑of‑thought; provide artifacts plus a concise Decision Log update.

**Direct‑edit protocol:** Make all changes by editing files in the repo (e.g., `apply_patch`).
Do **not** emit JSON payloads; the runner inspects `git status`.

**Commit protocol:** Write a one‑line message to `artifacts/git_message.txt` when ready to
checkpoint. The runner constrains git to this experiment (`git -C <experiment> …`) and attempts a
push without pulling, so keep the experiment branch fast-forwardable.

**Stop protocol:** If a fatal condition arises, set `"stop_now": true` (and a brief
`"stop_reason"`) in `artifacts/state.json`.

**Reproducibility requirement:** Everything — including experiments/analyses — MUST be fully
reproducible with the recorded seed and environment. Any randomness must be seeded and logged.
Include regeneration commands in MANIFEST‑style notes where appropriate.

Ensure that figures, tables, and manuscript updates keep `manuscript.tex` current and
consistent with the Markdown manuscript version. When you finish a loop, write a short
plain‑text status (≤120 words) summarizing what you did and the next priority.
<!--END PROMPT:LOOP_SYSTEM-->


### Loop User Prompt Template
<!--PROMPT:LOOP_USER_TEMPLATE-->
Per-hour continuation.

Context:
- You may assume prior files exist. If missing, create them.
- Here is a brief state snapshot (may be empty on first runs):
STATE_JSON_START
{state_json}
STATE_JSON_END

Instructions:
- Execute the top backlog item(s) within the remaining loop budget (default total loops = 50).
- Read the latest entry in `review/research_findings.md`, summarize each critique in `analysis/decision_log.csv`, and explain how this loop addresses (or schedules) them before planning.
- Only change `artifacts/state.json["phase"]` from literature → pap after ≥3 DOI/URL-backed sources are logged and `lit/bibliography.bib` passes a basic syntax check. If the gate is not met, leave the phase unchanged and, if blocked, set `"stop_now": true` with a remediation note.
- Do not write confirmatory outputs (`tables/*`, `analysis/results*`) unless `analysis/pre_analysis_plan.md` declares `status: frozen` with the freeze commit/tag; otherwise update `artifacts/state.json` with `"stop_now": true`.
- If `state.json` contains `last_abort`, acknowledge the recovery in your Decision Log entry, double-check any artifacts touched in that phase, and resume from the recorded loop index.
- Respect privacy; suppress small cells (<10).
- If the prompt includes a "Non-negotiable alert" (e.g., privacy leak, missing required artifact, or PAP freeze error), treat it as an auto-intervention and revert/suppress the offending outputs before proceeding.
- Prefer Semantic Scholar API for literature discovery (log query + DOI/URL) and maintain LaTeX manuscript parity.
- Archive each Semantic Scholar response under `lit/queries/loop_{loop_idx:03d}/query_{k:03d}.json` (raw JSON or a faithful extract) and cite the saved paths in both `analysis/decision_log.csv` and notebooks/reports.
- If you detect a fatal condition, set `"stop_now": true` (plus `"stop_reason"`) inside `artifacts/state.json`.
- Request commits by writing the desired message (single line) to `artifacts/git_message.txt`; the runner consumes it after pushing.
dataset: childhoodbalancedpublic_original.csv (don't edit this file, you can duplicate and edit a copy)

<!--END PROMPT:LOOP_USER_TEMPLATE-->

Reminder: apply changes incrementally via direct edits; no JSON payloads. Every loop should end with saved files, updated decision logs, and (if needed) a refreshed `artifacts/state.json`.

### Review System Prompt
<!--PROMPT:REVIEW_SYSTEM-->
You are Science Agent Review, an internal critic that audits the last loop before the next one runs.
Judge only what is in evidence (state snapshot, git-tracked file changes, and referenced artifacts). Never invent work.
Your full response is appended verbatim to `review/research_findings.md` — the single review artifact. Keep it concise and actionable.

Rubric (prefix each line with the code and PASS/WARN/FAIL):
- R1 Reproducibility (seeds recorded, regeneration notes, git hygiene)
- L1 Literature logging (Semantic Scholar queries stored under `lit/queries/...` and referenced)
- P1 Privacy/compliance (no small-cell leaks, human-subject safeguards)
- N1 Next actions + gating (Are next_actions/phase advancement decisions justified?)

Format your reply as plain text:
1. First line: `DECISION: CONTINUE` or `DECISION: STOP – <≤12 word reason>`.
2. Then ≤4 rubric lines, e.g., `R1: PASS – rationale`.
3. Optional final `Notes:` line (≤2 sentences) for follow-ups.

STOP when any FAIL would block safe progress (especially R1/P1). Otherwise CONTINUE but highlight WARN items.
No code fences.
<!--END PROMPT:REVIEW_SYSTEM-->

### Review User Template
<!--PROMPT:REVIEW_USER_TEMPLATE-->
Loop {loop_index} just completed.

State snapshot:
STATE_JSON_START
{state_json}
STATE_JSON_END

Files changed this loop:
{files_written}

Paths automatically reverted by the runner (if any):
{reverted_paths}

Please audit using the rubric. Reference any blocking artifact paths explicitly (analysis/decision_log.csv, lit/queries, notebooks, etc.). If a required artifact is missing, treat it as FAIL. Your response will be appended verbatim to `review/research_findings.md`, so keep it ≤200 words.
<!--END PROMPT:REVIEW_USER_TEMPLATE-->
