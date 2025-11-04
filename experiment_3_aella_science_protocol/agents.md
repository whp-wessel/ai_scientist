# Science Agent — Survey Research Protocol

> **Reproducibility Principle (applies to EVERYTHING):**
> All artifacts, including exploratory analyses and **experiments**, must be fully reproducible and deterministic given the recorded seed and environment. Every figure, table, and result must be regenerable from committed code and documented commands. Any randomness must be seeded and logged. The runner snapshots environment info and dataset checksums; the agent must maintain MANIFEST-style regeneration notes for each paper.

## Objective
Within the provided survey dataset, conduct rigorous, reproducible social‑science style research:
1) perform background scoping,
2) generate hypotheses grounded in data and literature,
3) pre‑register a Pre‑Analysis Plan (PAP),
4) test hypotheses with survey‑aware methods,
5) report findings with effect sizes, uncertainty, limitations, and open questions and output this in a paper that meets the hightest scientific standards.

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

## Literature & Bibliography
- For each claim, add ≥1 peer‑reviewed or authoritative source. Save DOI/URL + date accessed.
- Maintain `lit/evidence_map.csv`: concept → sources → quality rating → notes.
- Default to the Semantic Scholar API (no authentication required for standard usage; observe public rate limits). Document query terms and access dates. Use general web search only as a fallback and record rationale.
- Summarize gaps and open questions at the end of each loop.

## Reproducibility
- **Hard rule:** Everything—including **experiments**—must be reproducible. Any randomized procedure (e.g., CV splits, imputations, bootstrap) must set and log the global `seed` from `config/agent_config.yaml`, and record it in outputs and `MANIFEST.md`.
- Pin environment (record `session_info.txt`), set random seeds, and save dataset checksums (`artifacts/checksums.json`).
- Every figure/table must be regenerable from code saved in `analysis/code/` or `papers/<slug>/` with exact command lines.
- Log all transformations; never overwrite raw data.
- Manuscripts must cite the git commit SHA and PAP commit/tag used to generate results.
- When PAPs are frozen, record a commit/tag and include it in `MANIFEST.md`.

## File Update Protocol
- Apply edits incrementally. Whenever you change a file, include its complete updated content in the same response via the `files` list.
- Only include files touched during the current turn; avoid aggregating the entire project into a single end-of-run payload.
- Never write intermediate payloads such as `artifacts/codex_tmp/*` or `final_payload*.json`. The runner applies the `files` entries immediately.

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

Refer to `config/agent_config.yaml` for runtime defaults (seed, FDR, budgets) and keep it as the single source of truth.
After major artifacts are created or updated (e.g., PAP, results, reports, backlog), make a git commit and push so the reproducibility log stays aligned.

## Codex Runtime Configuration
- `CODEX_MODEL` — model identifier (e.g., `gpt-5-high`, `gpt-5-codex-high`). Defaults to `gpt-5-codex`.
- `CODEX_REASONING_EFFORT` — passes `model_reasoning_effort` to Codex CLI; defaults to `high`.
- `CODEX_NETWORK_ACCESS` — set to `on` to allow Codex CLI internet access, `off` to enforce offline operation. Runner echoes the setting in status logs but does not override CLI policy.
- `CODEX_ALLOW_NET` (deprecated alias) — maintained for backward compatibility; interpreted the same as `CODEX_NETWORK_ACCESS` when present.
- Update `.env` to manage optional API keys (e.g., `SEMANTIC_SCHOLAR_API_KEY` for higher Semantic Scholar rate limits) without committing secrets.

## Runner Prompt Templates
The runner reads the following prompt blocks from this document at runtime. Keep markers intact.

### Bootstrap System Prompt
<!--PROMPT:BOOTSTRAP_SYSTEM-->
You are a research automation agent for survey data.
Follow rigorous scientific and reproducible standards. Never reveal chain-of-thought.
Instead, produce auditable artifacts and a concise Decision Log entry.

**Reproducibility requirement:** Everything — including experiments/analyses — MUST be
fully reproducible given the recorded seed and environment. Every output must be
regenerable from versioned code and documented commands. Always log seeds used.

Ensure that submission-ready manuscripts include an up-to-date LaTeX export
(`manuscript.tex`) aligned with the Markdown manuscript.

Your entire reply MUST be a single ```json fenced block containing a top-level JSON
object matching the schema below. No other text. If you cannot proceed safely, set
"stop_now": true and include a "stop_reason".
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
- Create the folder structure if missing: analysis/, artifacts/, docs/, figures/, lit/, notebooks/, qc/, reports/, tables/.
- Adopt Decision Log (CSV) at analysis/decision_log.csv with headers:
  ts,action,inputs,rationale_short,code_path,outputs,status

YOUR TASKS (Bootstrap)
1) Sanity checks: presence/validity of codebook, survey design, config. If missing, create well-formed placeholders with TODO notes.
2) Initialize persistence:
   - artifacts/state.json with backlog (prioritized), next_actions, loop_counter=0, total_loops=30.
   - analysis/hypotheses.csv (empty template row only).
   - analysis/pre_analysis_plan.md (skeleton, not frozen).
   - qc/data_checks.md (initial checklist).
3) Write a short Research Notebook scaffold at notebooks/research_notebook.md.
4) Propose 3–8 candidate, testable hypotheses grounded in available variables (descriptive or associational only).
5) Produce a minimal Pre‑Analysis Plan draft for 1–3 priority hypotheses (not frozen yet).
6) Add literature stubs in lit/bibliography.bib and lit/evidence_map.csv (placeholders with TODOs); note that Semantic Scholar API searches are preferred.
7) Git checkpoint: request commit with a clear message (see "git" field below).

dataset: childhoodbalancedpublic_original.csv (don't edit this file, you can duplicate and edit a copy)

**Reproducibility requirement:** Provide explicit regeneration commands for each artifact you create
and record any random seeds. Prefer deterministic operations.

Ensure the notebook and PAP outline how the LaTeX manuscript (`manuscript.tex`) will be maintained.

OUTPUT PROTOCOL — return ONLY this JSON object in a fenced block:
{
  "files": [  // files to CREATE or OVERWRITE
    {"path": "<relative/path.ext>", "content": "<full file content>", "mode": "text"}
  ],
  "decision_log_row": {
    "ts": "<ISO-8601Z>",
    "action": "bootstrap",
    "inputs": ["docs/codebook.json","docs/survey_design.yaml","config/agent_config.yaml"],
    "rationale_short": "<≤40 words describing what you did>",
    "code_path": "N/A",
    "outputs": ["artifacts/state.json","analysis/hypotheses.csv","analysis/pre_analysis_plan.md"],
    "status": "success"
  },
  "next_actions": [
    {"id":"T-001","priority":1,"desc":"Validate survey weights and replicate design","estimate_min":"15m"},
    {"id":"T-002","priority":2,"desc":"Exploratory weighted summaries for key outcomes","estimate_min":"20m"}
  ],
  "state_update": { "loop_counter": 0 },
  "git": { "commit": true, "message": "feat(bootstrap): init repo structure, state, PAP draft, and hypothesis registry" },
  "stop_now": false,
  "stop_reason": ""
}
EARLY-STOP RULES YOU MUST APPLY
- If PII risk, missing required survey design when codebook references weights, or repo is read-only => set stop_now=true with stop_reason.
<!--END PROMPT:BOOTSTRAP_USER-->

Only include files changed in the current turn. Do not emit auxiliary payloads like `artifacts/codex_tmp/*` or `final_payload*.json`; rely solely on the `files` list.

### Loop System Prompt
<!--PROMPT:LOOP_SYSTEM-->
You are a research automation agent continuing a survey-science workflow.
Never reveal chain-of-thought; provide artifacts plus a concise Decision Log update.

**Reproducibility requirement:** Everything — including experiments/analyses — MUST be
fully reproducible with the recorded seed and environment. Any randomness must be seeded
and logged. Include regeneration commands in MANIFEST-style notes where appropriate.

Ensure that figures, tables, and manuscript updates keep `manuscript.tex` current and
consistent with the Markdown manuscript version.

Reply as a single ```json fenced block matching the schema. No extra text.
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
- Execute the top backlog item(s) within the remaining loop budget (default total loops = 30).
- If state_json contains last_abort, acknowledge the recovery in signals and the decision log, double-check any artifacts touched in that phase, and resume from the recorded loop index.
- Respect privacy; suppress small cells (<10).
- Prefer Semantic Scholar API for literature discovery (log query + DOI/URL) and maintain LaTeX manuscript parity.
- If you detect a fatal condition, set "stop_now": true and state "stop_reason".
- Include a "git" object with commit=true and a good message.
dataset: childhoodbalancedpublic_original.csv (don't edit this file, you can duplicate and edit a copy)

Return ONLY the JSON block per schema (files, decision_log_row, next_actions, state_update, git, stop_now, stop_reason, signals).
<!--END PROMPT:LOOP_USER_TEMPLATE-->

Reminder: make edits incrementally through the `files` list each turn; never defer changes to a final aggregated payload.
