# Experiment Focus Notes

## experiment_1_aella_stopped_midway
Baseline Survey Science Agent run. The inline runner prompts focus on bootstrapping a reproducible survey-analysis workspace: verify `docs/codebook.json`, `docs/survey_design.yaml`, `config/agent_config.yaml`, scaffold hypotheses, PAP, notebook, QC checklist, and log next actions while keeping every reply in a single JSON block. The accompanying agent brief emphasizes maintaining a full publication pipeline (research notebook, PAP, hypotheses/results registries, figures/tables, literature files, reproducibility manifests, and submission-ready manuscripts) with strict git checkpointing and deterministic seeds.

## experiment_2a_aella_mimimal
“Minimal” protocol that externalizes all prompts into `agents.md` so the runner can load phase-specific instructions dynamically. It layers practical safeguards on top of the baseline: honor `artifacts/last_abort.json`, require Semantic Scholar as the default literature source, keep Markdown/LaTeX manuscripts in sync, use the `outputs/` directory for scratch payloads, and insist that every file edit be emitted incrementally through the `files` array. The focus is a lightweight but highly disciplined loop with default 30 total loops and explicit privacy plus reproducibility guardrails.

## experiment_2b_aella_science_protocol
Full “Science Protocol” variant that uses the same modular runner but restores the comprehensive deliverable list. In addition to the minimal requirements, it adds standing expectations for `analysis/results.csv`, robustness checks, MANIFEST-style regeneration notes, Semantic Scholar-first literature logging, and routine git commits aligned with every major artifact. Scratch exports stay under `outputs/`, and agents must keep LaTeX/Markdown manuscripts synchronized while following the more exhaustive research-reporting standards.

## experiment_3_aella_review_agent_and_explicit_semantic_scholar
Phase-gated pipeline with a built-in reviewer. The runner enforces allowed directories/file types, tracks the current phase (`literature → pap → analysis → sensitivity → writing → review → release`), and validates that every payload reports a scorecard plus Semantic Scholar query metadata via `signals`. Agents must archive each Semantic Scholar response under `lit/queries/…`, produce review notes (`review/loop_<idx>.txt`), and follow micro-prompts tailored to each phase (e.g., literature minimum of three DOI-backed papers before advancing, analysis phase requiring falsification tests). A separate Science Agent Review rubric audits each loop before the next one runs.

## Cross-experiment differences

### How experiment 2* (2a + 2b) differs from experiment 1
- 2* moves run instructions out of the runner and into `agents.md`, enabling dynamic prompt loading, per-loop budgets, and last-abort recovery handling, whereas experiment 1 hard-codes a single bootstrap/loop prompt inside the runner.
- 2* explicitly mandates Semantic Scholar as the preferred literature source, LaTeX/Markdown parity, and the use of `outputs/` for scratch payloads, none of which are mentioned in the experiment 1 spec.
- 2* adds operational safeguards such as acknowledging `artifacts/last_abort.json`, enforcing incremental file writes through the `files` array, and tracking a `total_loops` counter (default 30) in `artifacts/state.json`, while experiment 1 simply initializes loop_counter without those controls.

### How experiment 3 differs from experiment 2*
- Experiment 3 introduces enforced research phases plus per-phase micro prompts, so advancing work requires meeting phase gates (e.g., ≥3 DOI-backed papers before leaving literature, falsification checks before exiting analysis); 2* treats all loops uniformly without phase advancement logic.
- Experiment 3 validates rich `signals` metadata (phase, review scorecard, privacy compliance, Semantic Scholar queries/reasons) and refuses payloads missing required Semantic Scholar activity—2* merely “prefers” Semantic Scholar without gating payload validity.
- Experiment 3 bakes in a reviewer agent that audits each loop and records findings under `review/loop_<idx>.txt`, adding an explicit QA step that the 2* experiments do not have.
