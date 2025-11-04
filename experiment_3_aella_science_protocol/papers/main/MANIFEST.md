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
- BH-FDR adjustment script placeholder: `analysis/code/fdr_adjust.py` (to be implemented prior to reporting results).

## Manuscript parity
- Markdown: `reports/findings_v0.1.md`
- LaTeX: `papers/main/manuscript.tex`
- Guideline: Apply synchronized edits; record regeneration commands (e.g., `pandoc reports/findings_v0.1.md -o papers/main/manuscript.tex`) when automation is introduced.

## Environment checkpoints
- Session info: `artifacts/session_info.txt`
- Checksums: `artifacts/checksums.json`
- Seed: `artifacts/seed.txt`
- Git reference: record commit SHA after freeze commit/tag; append here during next update.

## Outstanding tasks
1. Implement FDR computation script and robustness automation (backlog T-011).
2. Populate manuscript sections once confirmatory results are available.

> **Note:** Any deviation from the frozen PAP requires an amendment documented in both the decision log and this manifest, with updated tags.
