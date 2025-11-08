# Science Agent Review Findings

## Loop 001 — 2025-11-08T13:56:48.597820+00:00
DECISION: CONTINUE

R1 Reproducibility: PASS — Seed recorded (artifacts/session_info.txt:6), actions/commands logged (analysis/decision_log.csv), and reproducibility artifacts present (artifacts/repro_report.md; artifacts/state.json).

R2 Statistical Rigor: PASS — No confirmatory results yet; SRS explicitly justified (analysis/pre_analysis_plan.md) and results registry prepared (analysis/results.csv).

R3 Literature/Evidence: PASS — Evidence map and bibliography seeded (lit/evidence_map.csv; lit/bibliography.bib). Semantic Scholar queries saved (lit/queries/loop_000/query_001.json; lit/queries/loop_000/query_002.json); helper exists (scripts/semantic_scholar_cli.py).

R4 Privacy: PASS — No public tables produced; `tables/` is empty. Small-cell suppression policy noted for future outputs.

R5 Completeness: WARN — Core artifacts exist (analysis/pre_analysis_plan.md [status: draft], analysis/hypotheses.csv, analysis/results.csv header, notebooks/research_notebook.md, reports/paper.md). Commit checkpoint not requested (artifacts/git_message.txt missing). Literature CLI run awaits API key; results not yet populated (appropriate for literature phase).

Notes: Add artifacts/git_message.txt with a one-line checkpoint message. Once `.env` holds S2_API_Key, rerun the saved search and extract DOIs into lit/evidence_map.csv.

## Loop 002 — 2025-11-08T14:02:48.831520+00:00
DECISION: CONTINUE

- R1 Reproducibility: PASS — Seeds logged (`artifacts/seed.txt`), commands recorded in `analysis/decision_log.csv` (e.g., EDA), and regenerable code present (`scripts/analysis/eda.py`). Outputs exist (`outputs/eda_summary.json`, `tables/key_vars_value_counts.csv`).
- R2 Statistical Rigor: PASS — No confirmatory tests yet; SRS explicitly justified in `analysis/pre_analysis_plan.md` and `config/survey_design.yaml`. FDR plan noted. No effect estimates reported yet; `analysis/results.csv` header prepared.
- R3 Literature/Evidence: WARN — One citable source with DOI in `lit/bibliography.bib` and mapped in `lit/evidence_map.csv`. Semantic Scholar query artifacts are placeholders (`lit/queries/loop_000/query_001.json`) due to missing `S2_API_Key`; helper exists (`scripts/semantic_scholar_cli.py`) but query not executed.
- R4 Privacy: PASS — Public table `tables/key_vars_value_counts.csv` masks cells with n<10 (“<10”), meeting the small-cell rule.
- R5 Completeness: WARN — Core artifacts present (`analysis/*`, `notebooks/research_notebook.md`, `reports/paper.md`, `lit/*`, `tables/*`). However, `artifacts/git_message.txt` is missing (no commit request logged). `analysis/results.csv` has no rows yet (acceptable at this phase).

Notes: Add `.env` with `S2_API_Key` and run the saved search to populate `lit/queries/*` and update `lit/evidence_map.csv`. Write a commit message to `artifacts/git_message.txt` to checkpoint this loop.

## Loop 003 — 2025-11-08T14:10:39.174365+00:00
DECISION: CONTINUE

R1 Reproducibility: PASS — Seed logged (`artifacts/seed.txt`), environment captured (`artifacts/session_info.txt`), actions/commands recorded (`analysis/decision_log.csv`), deterministic scripts present (`scripts/analysis/eda.py`, `scripts/analysis/run_models.py`), outputs reproducible (`analysis/results.csv`, `outputs/eda_summary.json`).

R2 Statistical Rigor: PASS — Survey design handled via SRS with explicit justification (`analysis/pre_analysis_plan.md`, `analysis/results.csv:srs_justification`); all rows `confirmatory=false`; families assigned; effects reported with SE/CI/p (`analysis/results.csv`); no q-values required yet.

R3 Literature/Evidence: WARN — Minimal but present: DOI logged in `lit/evidence_map.csv` and cited in `reports/paper.md`. Semantic Scholar queries attempted via helper with structured errors saved (`lit/queries/loop_000/query_002.json`, `lit/queries/loop_003/query_002.json`) pending `.env` API key.

R4 Privacy: PASS — Public table masks n<10 as “<10” (`tables/key_vars_value_counts.csv`); non-public EDA lives under `outputs/`.

R5 Completeness: PASS — Required artifacts exist (`analysis/*`, `notebooks/research_notebook.md`, `reports/paper.md`, `lit/*`, `tables/*`); PAP is `status: draft` with freeze protocol noted; no confirmatory results yet.

Notes: Provide `.env` `S2_API_Key` to advance literature; consider adding `artifacts/git_message.txt` to request a commit.

## Loop 004 — 2025-11-08T14:17:04.564139+00:00
DECISION: CONTINUE
R1 Reproducibility: PASS — Seeds and commands documented (analysis/pre_analysis_plan.md; seed 20251016) with environment snapshot (artifacts/session_info.txt) and reproducibility report (artifacts/repro_report.md). Decision log includes loop_004 entries (analysis/decision_log.csv:18,20). Scripts under scripts/analysis/ reproduce artifacts.
R2 Statistical Rigor: PASS — SRS explicitly justified (config/survey_design.yaml) and echoed per-row in analysis/results.csv; effect sizes, SE, CIs, and p-values recorded. No confirmatory families yet; FDR not applicable.
R3 Literature/Evidence: PASS — Peer-reviewed source captured (lit/evidence_map.csv with DOI 10.1016/S0749-3797(98)00017-8; lit/bibliography.bib). Semantic Scholar query saved with error payload (lit/queries/loop_004/query_001.json) per protocol.
R4 Privacy: PASS — Public outputs apply n<10 suppression (scripts/analysis/make_tables.py). tables/key_vars_value_counts.csv masks sparse cells (“<10”); tables/religion_by_monogamy.csv has no n<10 cells.
R5 Completeness: PASS — PAP present and labeled draft (analysis/pre_analysis_plan.md); results captured (analysis/results.csv); manuscript maintained (reports/paper.md). No confirmatory results, so freeze/tag not yet required.

Notes: Consider adding artifacts/git_message.txt for the next checkpoint. Literature expansion awaits `.env` S2_API_Key.

## Loop 006 — 2025-11-08T14:30:18.971608+00:00
DECISION: CONTINUE

R1 Reproducibility: WARN — Seeds, commands, and logs are present (`artifacts/seed.txt:1`, `analysis/pre_analysis_plan.md:1`, `analysis/decision_log.csv:1`, scripts under `scripts/analysis/`). However, `artifacts/git_message.txt` is missing despite being claimed; add a one‑line commit message to align with the commit protocol.

R2 Statistical Rigor: PASS — SRS is explicitly justified (`analysis/pre_analysis_plan.md:1`; `analysis/results.csv:1` has `design_used=false` and `srs_justification`). Effect sizes, SEs, CIs, and p‑values are recorded (`analysis/results.csv:1`). No confirmatory families yet; q‑values not required.

R3 Literature/Evidence: PASS — At least one citable source with DOI is recorded and cited (`lit/bibliography.bib:1`, `lit/evidence_map.csv:1`, `reports/paper.md:1`). Semantic Scholar queries are executed via the helper and saved, albeit rate‑limited pending API key (`lit/queries/...`).

R4 Privacy: PASS — Public tables mask n<10 cells (e.g., `tables/key_vars_value_counts.csv:1`; `tables/religion_by_monogamy.csv:1` shows no small cells).

R5 Completeness: PASS — Required artifacts exist and are coherent for the literature phase: PAP (draft) (`analysis/pre_analysis_plan.md:1`), hypotheses (`analysis/hypotheses.csv:1`), results (`analysis/results.csv:1`), notebook (`notebooks/research_notebook.md:1`), paper (`reports/paper.md:1`), state (`artifacts/state.json:1`).

Notes: Please add `artifacts/git_message.txt` to request a checkpoint. Provide `.env` `S2_API_Key` to run Semantic Scholar queries and expand `lit/evidence_map.csv`.

## Loop 007 — 2025-11-08T14:36:22.015348+00:00
DECISION: CONTINUE

R1 Reproducibility: WARN – Seeds and environment recorded (artifacts/seed.txt, artifacts/session_info.txt), commands logged in analysis/decision_log.csv and analysis/pre_analysis_plan.md; scripts produce all artifacts deterministically. However, the commit request file referenced this loop is missing (artifacts/git_message.txt), so no checkpoint message is present.

R2 Statistical Rigor: PASS – Survey design handled with explicit SRS justification (config/survey_design.yaml; analysis/results.csv: design_used=false with srs_justification). All results are exploratory (confirmatory=false); effect sizes, SEs, CIs, and p-values reported; no q-values required yet.

R3 Literature/Evidence: PASS – Semantic Scholar query saved (lit/queries/loop_007/query_001.json); DOIs extracted into lit/evidence_map.csv; manuscript cites a peer‑reviewed source (reports/paper.md; lit/bibliography.bib).

R4 Privacy: PASS – Public tables suppress small cells (tables/key_vars_value_counts.csv shows “<10”; tables/religion_by_monogamy.csv contains no cells <10).

R5 Completeness: PASS – Minimal deliverables present: analysis/pre_analysis_plan.md (status: draft), analysis/hypotheses.csv, analysis/results.csv, notebooks/research_notebook.md, reports/paper.md, lit/bibliography.bib, lit/evidence_map.csv, tables/*.csv. No confirmatory results, so PAP freeze/tag not yet required.

Notes: Please add artifacts/git_message.txt with a one‑line message to request the checkpoint for Loop 007.

## Loop 008 — 2025-11-08T14:41:33.992585+00:00
DECISION: CONTINUE

- R1 Reproducibility: WARN — Seeds and environment recorded (artifacts/session_info.txt; seed 20251016), code paths and commands documented (notebooks/research_notebook.md; analysis/pre_analysis_plan.md), decision log maintained (analysis/decision_log.csv). However, no commit request present (artifacts/git_message.txt missing), which weakens checkpointing.
- R2 Statistical Rigor: PASS — Survey design honored via explicit SRS justification (config/survey_design.yaml; analysis/pre_analysis_plan.md). Results include effect sizes, SEs, CIs, and p-values (analysis/results.csv). No confirmatory families yet; q_value appropriately blank.
- R3 Literature/Evidence: PASS — Evidence map maintained with DOIs (lit/evidence_map.csv) and a canonical reference in bibliography (lit/bibliography.bib). Saved Semantic Scholar payloads, including an error capture (lit/queries/loop_008/query_001.json) and a successful search (lit/queries/loop_008/query_002.json). Manuscript cites Felitti 1998 (reports/paper.md).
- R4 Privacy: PASS — Public outputs use n<10 suppression (tables/key_vars_value_counts.csv shows “<10”; scripts/analysis/eda.py and make_tables.py enforce thresholds). Public crosstab (tables/religion_by_monogamy.csv) contains no sub-threshold cells.
- R5 Completeness: PASS — Required artifacts present: analysis/pre_analysis_plan.md (status: draft), analysis/hypotheses.csv, analysis/results.csv, notebooks/research_notebook.md, lit/evidence_map.csv, reports/paper.md, and tables/*.csv. No confirmatory results; PAP not yet frozen (appropriate).

Notes: Recommend adding artifacts/git_message.txt to request a checkpoint commit and pruning off-topic literature entries in lit/evidence_map.csv for focus.

## Loop 009 — 2025-11-08T14:46:53.449933+00:00
DECISION: CONTINUE

R1 Reproducibility: PASS — Seed recorded (artifacts/seed.txt), environment captured (artifacts/session_info.txt), actions/commands logged (analysis/decision_log.csv), and literature query saved (lit/queries/loop_009/query_001.json). Minor gap: commit message file not found (artifacts/git_message.txt).

R2 Statistical Rigor: PASS — Results are exploratory only (analysis/results.csv; confirmatory=false). SRS assumption is explicit (config/survey_design.yaml; srs_justification in results). Effect sizes, SEs, CIs, and p-values reported. No FDR required yet.

R3 Literature/Evidence: PASS — Evidence map maintained with DOIs (lit/evidence_map.csv) extracted from saved queries; manuscript cites a peer‑reviewed DOI (reports/paper.md).

R4 Privacy: PASS — Public tables under tables/ apply n<10 suppression (e.g., tables/key_vars_value_counts.csv shows “<10”; tables/religion_by_monogamy.csv has no <10 cells).

R5 Completeness: PASS — PAP present and clearly status: draft (analysis/pre_analysis_plan.md); hypotheses/results registries exist (analysis/hypotheses.csv, analysis/results.csv); manuscript present (reports/paper.md). No confirmatory results; freeze/tag not yet required.

Notes: Please add artifacts/git_message.txt to request a checkpoint. Continue expanding literature via scripts/semantic_scholar_cli.py and move toward PAP-freeze criteria.

## Loop 010 — 2025-11-08T14:51:59.398618+00:00
DECISION: CONTINUE

- R1 Reproducibility — PASS: Seeds recorded (`artifacts/seed.txt`), commands and paths logged (`analysis/decision_log.csv`, `notebooks/research_notebook.md`), saved query JSON (`lit/queries/loop_010/query_001.json`), and a repro report with HEAD noted (`artifacts/repro_report.md`). Rate limit tracked (`artifacts/.s2_rate_limit.json`).
- R2 Statistical Rigor — PASS: All results are exploratory with `confirmatory=false` (`analysis/results.csv`), include effect sizes, SE, CIs, and p-values; SRS explicitly justified (no weights/strata/clusters) in both PAP and results (`analysis/pre_analysis_plan.md`, `analysis/results.csv`). No confirmatory families → no q-values required.
- R3 Literature/Evidence — PASS: Evidence map maintained with DOIs and sources (`lit/evidence_map.csv`, e.g., E17–E21 from `lit/queries/loop_010/query_001.json`). Manuscript cites a peer‑reviewed source with DOI (`reports/paper.md`).
- R4 Privacy — PASS: Public tables suppress n<10 (`tables/key_vars_value_counts.csv` uses “<10”); crosstab has no <10 cells (`tables/religion_by_monogamy.csv`).
- R5 Completeness — PASS: PAP present and marked `status: draft` (`analysis/pre_analysis_plan.md`), hypotheses/results registries exist, manuscript present (`reports/paper.md`). No confirmatory testing performed → freeze/tag not yet required.

Notes: Consider writing `artifacts/git_message.txt` to request a commit for this loop.

## Loop 011 — 2025-11-08T14:57:30.000707+00:00
DECISION: CONTINUE

R1 Reproducibility: PASS — Seeds and commands recorded in analysis/decision_log.csv; seed in artifacts/seed.txt; state tracked in artifacts/state.json; scripts present to regenerate results (scripts/analysis/*.py). Minor gap: artifacts/git_message.txt not found this loop.
R2 Statistical Rigor: PASS — Survey design explicitly justified as SRS in analysis/pre_analysis_plan.md and config/survey_design.yaml; results in analysis/results.csv include estimates, SEs, CIs, p-values; no confirmatory families yet, so no q-values required.
R3 Literature/Evidence: PASS — Saved query at lit/queries/loop_011/query_001.json; DOIs appended to lit/evidence_map.csv; manuscript cites peer-reviewed source in reports/paper.md; bibliography in lit/bibliography.bib.
R4 Privacy: PASS — Public tables under tables/ apply n<10 suppression (e.g., tables/key_vars_value_counts.csv and tables/religion_by_monogamy.csv).
R5 Completeness: PASS — PAP exists and is clearly marked “status: draft” (analysis/pre_analysis_plan.md); results registry present (analysis/results.csv); manuscript scaffold present (reports/paper.md). No confirmatory results before PAP freeze.

Notes: The notebook claims a commit message was written, but artifacts/git_message.txt is missing; add it next loop to keep reproducibility aligned. Phase remains literature; no invariant violations observed.

## Loop 012 — 2025-11-08T15:02:33.728994+00:00
DECISION: CONTINUE

R1 Reproducibility: WARN — Loop is logged with commands and seeds (`analysis/decision_log.csv`, `artifacts/state.json`, `seed.txt`; commands echoed in `notebooks/research_notebook.md` and `artifacts/llm_raw/loop_012.txt`). However, no `artifacts/git_message.txt` exists despite the loop narrative claiming it (needed to request a checkpoint commit).

R2 Statistical Rigor: PASS — No confirmatory tests; SRS explicitly justified in `analysis/results.csv` (`design_used=false`, `srs_justification` filled). FDR plan deferred until confirmatory work. Effect sizes and uncertainty recorded.

R3 Literature/Evidence: PASS — Literature query saved at `lit/queries/loop_012/query_001.json`; DOIs appended to `lit/evidence_map.csv` (E27–E31). Manuscript cites peer‑reviewed source (Felitti 1998 DOI) in `reports/paper.md`.

R4 Privacy: PASS — Public tables respect n<10 suppression (`tables/key_vars_value_counts.csv` masks “<10”). `tables/religion_by_monogamy.csv` has no cells <10.

R5 Completeness: PASS — Required artifacts present and coherent: `analysis/pre_analysis_plan.md` (status: draft), `analysis/hypotheses.csv`, `analysis/results.csv`, `notebooks/research_notebook.md`, `reports/paper.md`, `lit/evidence_map.csv`. No PAP freeze yet (appropriate for literature phase).

Notes: Create `artifacts/git_message.txt` to request the commit for loop_012 changes. Keep citing saved JSON paths in the PAP/manuscript.

## Loop 013 — 2025-11-08T15:09:24.910957+00:00
DECISION: CONTINUE

R1 Reproducibility: PASS — Seeds recorded (artifacts/session_info.txt), deterministic commands specified (analysis/pre_analysis_plan.md; scripts/analysis/{eda.py,run_models.py}), decision log maintained (analysis/decision_log.csv), and repro artifacts present (artifacts/repro_report.md).

R2 Statistical Rigor: PASS — Survey design handled via explicit SRS justification in results (analysis/results.csv: design_used=false, srs_justification set). Effect sizes, SEs, CIs, and p-values reported. All tests marked confirmatory=false; no q-values required yet.

R3 Literature/Evidence: PASS — Saved Semantic Scholar queries (lit/queries/loop_013/query_002.json), DOIs extracted to lit/evidence_map.csv, and manuscript cites a peer-reviewed source with DOI (reports/paper.md; lit/bibliography.bib).

R4 Privacy: PASS — Public tables suppress small cells (tables/key_vars_value_counts.csv masks counts as “<10”; tables/religion_by_monogamy.csv has no <10 cells).

R5 Completeness: WARN — PAP remains “status: draft” (analysis/pre_analysis_plan.md), appropriate for literature phase; core artifacts exist (analysis/hypotheses.csv, analysis/results.csv, notebooks/research_notebook.md, reports/paper.md, lit/evidence_map.csv). artifacts/git_message.txt not found to request a checkpoint commit.

Notes: Before any confirmatory tests, freeze/tag the PAP and control FDR with q-values for any confirmatory family >1 test.

## Loop 014 — 2025-11-08T15:14:18.350187+00:00
DECISION: CONTINUE

R1 Reproducibility: PASS — Seed recorded (`artifacts/seed.txt`), actions/commands logged (`analysis/decision_log.csv` includes `run_models`), scripts present and runnable (`scripts/analysis/run_models.py`, `scripts/analysis/eda.py`), query artifacts saved (`lit/queries/loop_014/query_001.json`). Minor: no commit request found (`artifacts/git_message.txt` missing).

R2 Statistical Rigor: PASS — Survey design justified as SRS (`config/survey_design.yaml`); results include effect sizes, SEs, CIs, p-values (`analysis/results.csv`), and `confirmatory=false` so FDR/q-values not required.

R3 Literature/Evidence: PASS — Evidence map maintained with DOIs (`lit/evidence_map.csv`), saved queries exist (`lit/queries/*`), and manuscript cites peer‑reviewed source with DOI (`reports/paper.md`).

R4 Privacy: PASS — Public tables suppress small cells (e.g., `<10` in `tables/key_vars_value_counts.csv`); cross‑tabs show counts >=10 (`tables/religion_by_monogamy.csv`).

R5 Completeness: PASS — PAP present and marked draft (`analysis/pre_analysis_plan.md`), hypotheses/results registries exist (`analysis/hypotheses.csv`, `analysis/results.csv`), manuscript present (`reports/paper.md`). No confirmatory results, so freeze/tagging not yet required.

Notes: Recommend adding a commit message to `artifacts/git_message.txt` to checkpoint this loop for full reproducibility alignment.

## Loop 015 — 2025-11-08T15:18:58.620493+00:00
DECISION: CONTINUE

R1 Reproducibility: WARN — Seeds and environment recorded (`artifacts/session_info.txt`, seed 20251016); actions and commands logged (`analysis/decision_log.csv`); scripts exist to regenerate (`scripts/analysis/*.py`, `scripts/semantic_scholar_cli.py`). However, no commit request found for this loop (`artifacts/git_message.txt` missing), which weakens checkpointing.

R2 Statistical Rigor: PASS — Results are exploratory with effect sizes, SEs, CIs, and p-values (`analysis/results.csv`). Survey design is honored via explicit SRS justification (“design_used=false” with rationale). No confirmatory families yet, so q-values appropriately blank.

R3 Literature/Evidence: PASS — Literature queries are saved (`lit/queries/loop_015/query_001.json`), DOIs captured in `lit/evidence_map.csv`; manuscript cites a peer‑reviewed DOI (`reports/paper.md`).

R4 Privacy: PASS — Public tables apply small‑cell suppression (n<10 masked) in `tables/key_vars_value_counts.csv`; `tables/religion_by_monogamy.csv` has no cells <10.

R5 Completeness: PASS — PAP present and clearly marked `status: draft` (`analysis/pre_analysis_plan.md`); hypotheses (`analysis/hypotheses.csv`), results, notebook, and draft manuscript exist. No confirmatory results, so freezing/tagging not yet required.

Notes: Recommend adding `artifacts/git_message.txt` to request a commit for this loop to strengthen reproducibility.

## Loop 016 — 2025-11-08T15:39:37.908244+00:00
DECISION: CONTINUE

R1 Reproducibility: PASS — Seeds and commands recorded in analysis/decision_log.csv; default seed noted in notebooks/research_notebook.md and PAP; scripts exist (scripts/analysis/*.py; scripts/semantic_scholar_cli.py); queries saved under lit/queries/loop_016/query_001.json.

R2 Statistical Rigor: PASS — No survey design provided; SRS justified (config/survey_design.yaml:1). Results include estimate, SE, CI, p (analysis/results.csv:2). All rows marked confirmatory=false; no FDR/q-values required yet.

R3 Literature/Evidence: PASS — Evidence map maintained (lit/evidence_map.csv); Semantic Scholar JSON saved (lit/queries/loop_016/query_001.json); manuscript cites a DOI (reports/paper.md:9) and bibliography exists (lit/bibliography.bib).

R4 Privacy: PASS — Public tables apply n<10 masking (tables/key_vars_value_counts.csv:8 shows “<10”); cross-tab table has all cells ≥10 (tables/religion_by_monogamy.csv).

R5 Completeness: PASS — PAP present and clearly “status: draft” (analysis/pre_analysis_plan.md:1); results registry populated (analysis/results.csv); manuscript present (reports/paper.md); required artifacts exist.

Notes: Recommend adding artifacts/git_message.txt for a checkpoint in the next loop to keep reproducibility aligned.

## Loop 017 — 2025-11-08T15:44:29.367985+00:00
DECISION: CONTINUE

- R1 Reproducibility: PASS — Commands and outcomes logged in analysis/decision_log.csv; seed recorded (artifacts/seed.txt) and environment captured (artifacts/session_info.txt); reproducibility note/report present (artifacts/repro_report.md, artifacts/state.json). Minor: artifacts/git_message.txt is missing though referenced.
- R2 Statistical Rigor: PASS — Exploratory results in analysis/results.csv include estimates, SE, CI, p-values; all confirmatory=false (no FDR needed). Survey design documented with SRS justification (design_used=false; srs_justification set; config/survey_design.yaml aligns). Effect sizes reported.
- R3 Literature/Evidence: PASS — Evidence map maintained (lit/evidence_map.csv with DOIs/URLs). Saved query payloads exist (e.g., lit/queries/loop_017/query_001.json with 429 captured). Manuscript cites a peer-reviewed source with DOI (reports/paper.md).
- R4 Privacy: PASS — Public tables under tables/ use suppression: key_vars_value_counts.csv masks n<10 as “<10”; cross-tab counts in religion_by_monogamy.csv are all ≥10.
- R5 Completeness: PASS — PAP present and marked status: draft (analysis/pre_analysis_plan.md); hypotheses registry complete (analysis/hypotheses.csv); manuscript present (reports/paper.md). No confirmatory results before freeze/tag, so compliant.

Notes: Add artifacts/git_message.txt to trigger a checkpoint. Provide S2_API_Key to avoid 429s and continue literature extraction.

