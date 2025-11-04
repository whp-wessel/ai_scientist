# MANIFEST — Main Paper
Created: 2025-11-04T07:58:50Z | Seed: 20251016

## Frozen PAP reference
- File: `analysis/pre_analysis_plan.md`
- Status: Frozen (2025-11-04T07:58:50Z)
- Planned tag: `pap-freeze-20251104` (create immediately after committing freeze artifacts).
- Regeneration: `python analysis/code/bootstrap_setup.py --artifact analysis/pre_analysis_plan.md` (for archival comparison only; do **not** overwrite frozen content post-freeze).

## Data lineage
1. Raw dataset (`data/raw/childhoodbalancedpublic_original.csv`) — checksum tracked in `artifacts/checksums.json`.
2. Derived dataset (`data/clean/childhoodbalancedpublic_with_csa_indicator.csv`) — regenerate via  
   `python analysis/code/derive_csa_indicator.py --dataset data/raw/childhoodbalancedpublic_original.csv --out-dataset data/clean/childhoodbalancedpublic_with_csa_indicator.csv --out-distribution tables/csa_indicator_distribution.csv --config config/agent_config.yaml --codebook-in docs/codebook.json --codebook-out docs/codebook.json`.

## Confirmatory analyses
- Command (frozen):  
  `python analysis/code/confirmatory_models.py --dataset data/clean/childhoodbalancedpublic_with_csa_indicator.csv --config config/agent_config.yaml --survey-design docs/survey_design.yaml --hypotheses HYP-001 HYP-003 --results-csv analysis/results.csv --overwrite`
- Expected outputs: `analysis/results.csv`, QC diagnostics under `qc/`, confirmatory tables under `tables/confirmatory/`, plots under `figures/confirmatory/`.
- FDR adjustment command (executed 2025-11-04T09:25Z):  
  `python analysis/code/fdr_adjust.py --results analysis/results.csv --hypotheses analysis/hypotheses.csv --config config/agent_config.yaml --family-scope confirmatory --out analysis/results.csv --audit-table tables/fdr_adjustment_confirmatory.csv`  
  Outputs: `analysis/results.csv` (q-values updated), `tables/fdr_adjustment_confirmatory.csv`.
- Robustness automation command (executed 2025-11-04T09:25Z):  
  `python analysis/code/run_robustness_checks.py --dataset data/clean/childhoodbalancedpublic_with_csa_indicator.csv --config config/agent_config.yaml --qc-dir qc --tables-dir tables/robustness --hypotheses HYP-001 HYP-003`  
  Outputs: `tables/robustness/robustness_checks_summary.{csv,json}`, QC notes (`qc/hyp-001_*`, `qc/hyp-003_*`).

## Manuscript parity
- Markdown: `reports/findings_v0.2.md` (supersedes v0.1; retain v0.1 for archival comparison)
- LaTeX: `papers/main/manuscript.tex`
- Guideline: Apply synchronized edits; record regeneration commands (e.g., `pandoc reports/findings_v0.2.md -o papers/main/manuscript.tex`) when automation is introduced. Update the changelog in Markdown when substantive revisions occur.

## Environment checkpoints
- Session info: `artifacts/session_info.txt`
- Checksums: `artifacts/checksums.json`
- Seed: `artifacts/seed.txt`
- Git reference: record commit SHA after freeze commit/tag; append here during next update.

## Outstanding tasks
1. Review anxiety item coding and routing documentation (backlog T-017).
2. Contextualize CSA–anxiety findings with literature synthesis (backlog T-018).

### Notes (2025-11-04T10:45Z)
- Findings report advanced to v0.2 with expanded confirmatory interpretation; manuscript updated in lockstep.
- CSA–anxiety diagnostics (2025-11-04T10:45Z) logged via `analysis/code/diagnose_csa_anxiety_direction.py`; outputs stored under `tables/diagnostics/` and `qc/`.

> **Note:** Any deviation from the frozen PAP requires an amendment documented in both the decision log and this manifest, with updated tags.
