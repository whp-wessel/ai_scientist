# MANIFEST — Main Paper
Created: 2025-11-04T07:58:50Z | Seed: 20251016 (refreshed 2025-11-04T10:06:22Z)

## Frozen PAP reference
- File: `analysis/pre_analysis_plan.md`
- Status: Frozen (2025-11-04T10:06:00Z)
- Planned tag: `pap-freeze-20251104` (create immediately after committing freeze artifacts).
- Regeneration: `python analysis/code/bootstrap_setup.py --artifact analysis/pre_analysis_plan.md` (archival diff only; do **not** overwrite frozen content post-freeze).

## Data lineage
1. Raw dataset (`data/raw/childhoodbalancedpublic_original.csv`) — checksum tracked in `artifacts/checksums.json`.
2. Derived dataset (`data/clean/childhoodbalancedpublic_with_csa_indicator.csv`) — regenerate via  
   `python analysis/code/derive_csa_indicator.py --dataset data/raw/childhoodbalancedpublic_original.csv --out-dataset data/clean/childhoodbalancedpublic_with_csa_indicator.csv --out-distribution tables/csa_indicator_distribution.csv --config config/agent_config.yaml --codebook-in docs/codebook.json --codebook-out docs/codebook.json`.

## Confirmatory analyses
- Command (frozen):  
  `python analysis/code/confirmatory_models.py --dataset data/clean/childhoodbalancedpublic_with_csa_indicator.csv --config config/agent_config.yaml --survey-design docs/survey_design.yaml --hypotheses HYP-001 HYP-003 --results-csv analysis/results.csv --overwrite`
- Expected outputs: `analysis/results.csv`, QC diagnostics under `qc/`, confirmatory tables under `tables/confirmatory/`, plots under `figures/confirmatory/`.
- FDR adjustment command (to execute post-results, registered 2025-11-04T10:06Z):  
  `python analysis/code/fdr_adjust.py --results analysis/results.csv --hypotheses analysis/hypotheses.csv --config config/agent_config.yaml --family-scope confirmatory --out analysis/results.csv --audit-table tables/fdr_adjustment_confirmatory.csv`  
  Outputs: `analysis/results.csv` (q-values updated), `tables/fdr_adjustment_confirmatory.csv`.
- Robustness automation command (to execute post-results, registered 2025-11-04T10:06Z):  
  `python analysis/code/run_robustness_checks.py --dataset data/clean/childhoodbalancedpublic_with_csa_indicator.csv --config config/agent_config.yaml --qc-dir qc --tables-dir tables/robustness --hypotheses HYP-001 HYP-003`  
  Outputs: `tables/robustness/robustness_checks_summary.{csv,json}`, QC notes (`qc/hyp-001_*`, `qc/hyp-003_*`).

## Robustness synthesis
- Memo: `qc/robustness_summary.md` (2025-11-04T14:05Z) — manual synthesis of `tables/robustness/robustness_checks_summary.{csv,json}`; no additional randomness beyond seed 20251016.
- To refresh: rerun `python analysis/code/run_robustness_checks.py ...` above, then update the memo to reflect any new checks.

## Manuscript parity
- Markdown: `reports/findings_v0.4.md` (supersedes v0.3; retain prior versions for archival comparison)
- LaTeX: `papers/main/manuscript.tex`
- Guideline: Apply synchronized edits; record regeneration commands (e.g., `pandoc reports/findings_v0.4.md -o papers/main/manuscript.tex`) when automation is introduced. Update the changelog in Markdown when substantive revisions occur.

## Environment checkpoints
- Session info: `artifacts/session_info.txt` (updated 2025-11-04T10:06:22Z)
- Checksums: `artifacts/checksums.json` (updated 2025-11-04T10:06:22Z)
- Seed: `artifacts/seed.txt`
- Git reference: record commit SHA after freeze commit/tag; append here during next update.

## Outstanding tasks
1. Execute convergent validity diagnostics for the anxiety item with companion affect measures (backlog T-017; maps to WP1 in `analysis/csa_anxiety_diagnostics_plan.md`).
2. Develop CSA×(cis, age, class) interaction scripts and archive QC outputs (backlog T-018; WP2 in `analysis/csa_anxiety_diagnostics_plan.md`).

## Measurement diagnostics plan
- Command:  
  `python analysis/code/create_csa_anxiety_measurement_plan.py --config config/agent_config.yaml --out-md qc/csa_anxiety_measurement_plan.md --generated-at 2025-11-04T13:15:00Z`
- Output: `qc/csa_anxiety_measurement_plan.md`
- DIF execution (2025-11-04T09:36Z):  
  `python analysis/code/test_anxiety_dif.py --dataset data/clean/childhoodbalancedpublic_with_csa_indicator.csv --config config/agent_config.yaml --outcome "I tend to suffer from anxiety (npvfh98)-neg" --csa CSA_score_indicator --group gender --group-value-column gendermale --out-table tables/diagnostics/anxiety_dif.csv --out-md qc/anxiety_dif.md`  
  Outputs: `tables/diagnostics/anxiety_dif.csv`, `qc/anxiety_dif.md`
- Subgroup summary (2025-11-04T09:57Z):  
  `python analysis/code/anxiety_subgroup_summary.py --dataset data/clean/childhoodbalancedpublic_with_csa_indicator.csv --config config/agent_config.yaml --out-table tables/diagnostics/anxiety_subgroup_summary.csv --out-md qc/anxiety_subgroup_summary.md`  
  Outputs: `tables/diagnostics/anxiety_subgroup_summary.csv`, `qc/anxiety_subgroup_summary.md`
- CSA–anxiety diagnostics scope (2025-11-04T14:05Z): `analysis/csa_anxiety_diagnostics_plan.md` — manual plan covering convergent validity (Task T-017) and interaction modelling (Task T-018); future scripts must log seed 20251016 and update this manifest.

### Notes (2025-11-04T13:36Z)
- Findings report advanced to v0.3 with literature synthesis; manuscript updated in lockstep.
- Semantic Scholar queries stored under `lit/queries/` (see reproducibility notes) with bibliography/evidence map refreshed to cite Lindert et al. 2014, Hashim et al. 2024, and Li et al. 2023.
- CSA–anxiety measurement diagnostic plan recorded in `qc/csa_anxiety_measurement_plan.md`. Ordinal DIF diagnostic (T-021) executed; outputs archived in `tables/diagnostics/anxiety_dif.csv` and `qc/anxiety_dif.md`.

### Notes (2025-11-04T10:38:43Z)
- Robustness statuses and confidence ratings applied in `analysis/results.csv`; narratives synchronised across Markdown and LaTeX (v0.4).
- No new analytic commands executed; updates draw on `tables/robustness/robustness_checks_summary.csv` and prior confirmatory outputs.

### Notes (2025-11-04T14:05:00Z)
- Archived `qc/robustness_summary.md` to centralise robustness evidence and reference regeneration commands.
- Authored `analysis/csa_anxiety_diagnostics_plan.md`, elevating new backlog tasks T-017 (convergent validity) and T-018 (interaction scripting) for execution in subsequent loops.
- Updated `artifacts/state.json` and `notebooks/research_notebook.md` to reflect the new QC focus areas.

> **Note:** Any deviation from the frozen PAP requires an amendment documented in both the decision log and this manifest, with updated tags.
