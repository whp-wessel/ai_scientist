# FDR and Robustness Execution Plan

Prepared: 2025-11-04T10:30Z by automation agent (seed 20251016). This document operationalises backlog item **T-011** by detailing the deterministic workflow for (a) applying Benjamini–Hochberg (BH) false-discovery-rate adjustments and (b) executing the frozen robustness checks for confirmatory hypotheses. All steps assume the PAP (`analysis/pre_analysis_plan.md`) remains frozen as of 2025-11-04T10:06Z and that confirmatory estimates have been regenerated via the registered command.

## Preconditions
- Clean dataset: `data/clean/childhoodbalancedpublic_with_csa_indicator.csv`
- Confirmatory results populated: `analysis/results.csv` (seed column populated, timestamped)
- Registry: `analysis/hypotheses.csv` with `status ∈ {in_PAP, tested}` for confirmatory entries
- Configuration: `config/agent_config.yaml` (global seed = 20251016; contains `fdr_q`)
- Survey design metadata: `docs/survey_design.yaml`
- Manifest coordinates recorded in `papers/main/MANIFEST.md`

## Step 1 — Validate inputs (deterministic)
```bash
python analysis/code/update_repro_checkpoints.py \
  --config config/agent_config.yaml \
  --data data/raw/childhoodbalancedpublic_original.csv \
  --data data/clean/childhoodbalancedpublic_with_csa_indicator.csv
```
Outputs (for traceability only): `artifacts/session_info.txt`, `artifacts/checksums.json`. This step confirms file checksums and ensures the environment snapshot predates FDR/robustness runs.

## Step 2 — Apply BH FDR adjustment
```bash
python analysis/code/fdr_adjust.py \
  --results analysis/results.csv \
  --hypotheses analysis/hypotheses.csv \
  --config config/agent_config.yaml \
  --family-scope confirmatory \
  --status-filter in_PAP tested \
  --out analysis/results.csv \
  --audit-table tables/fdr_adjustment_confirmatory.csv
```
- Deterministic: no randomness; script records the global seed for auditing.
- Outputs:
  - `analysis/results.csv` with `q_value` updated for each targeted hypothesis
  - `tables/fdr_adjustment_confirmatory.csv` documenting BH ranks, p-values, q-values, and seed
- QC: confirm added/updated `q_value` column is non-missing for targeted hypotheses and that `rank_within_family` starts at 1; if additional hypotheses are introduced, verify each family contains ≥1 entry before BH proceeds (script logs warnings otherwise).

## Step 3 — Execute frozen robustness checks
```bash
python analysis/code/run_robustness_checks.py \
  --dataset data/clean/childhoodbalancedpublic_with_csa_indicator.csv \
  --config config/agent_config.yaml \
  --qc-dir qc \
  --tables-dir tables/robustness \
  --hypotheses HYP-001 HYP-003
```
- Deterministic: script seeds NumPy using the global seed (20251016) and performs analytic (non-resampled) estimators.
- Outputs:
  - `qc/hyp-001_*.md`, `qc/hyp-003_*.md` summarising check-specific statistics
  - `tables/robustness/robustness_checks_summary.csv` and `.json`
- QC / Suppression: outputs are aggregated statistics (no individual-level cells); no small-cell disclosures arise. If checks are restricted (via `--checks`), document rationale in `analysis/decision_log.csv` and the PAP amendment log.

## Step 4 — Update downstream artifacts
1. Append a decision-log entry describing the execution (include command strings).
2. For each confirmatory hypothesis, update `analysis/results.csv` `robustness_passed` once all planned checks are reviewed.
3. Refresh reporting artifacts:
   - `reports/findings_v*.md` (include BH-adjusted inference wording)
   - `tables/` or `figures/` derivatives, if regenerated
   - Sync `papers/main/manuscript.tex` with Markdown via `pandoc` command recorded in the manifest.
4. Update `artifacts/state.json`: mark **T-011** as completed; queue subsequent tasks (e.g., sensitivity interpretations).

## Extension guidance
- **New hypotheses**: set `family` in `analysis/hypotheses.csv`, ensure `status` transitions to `in_PAP` or `tested`, and re-run Step 2 to incorporate them. Families are adjusted independently, so ensure each family contains at least one observation before FDR execution.
- **Alternative seeds**: any change to the global seed requires an explicit amendment and regeneration of all randomised steps (none currently) to maintain determinism.
- **Automation**: to run Steps 2–3 sequentially after confirmatory model execution, use (or incorporate into a CI job):
  ```bash
  python analysis/code/fdr_adjust.py --results analysis/results.csv --hypotheses analysis/hypotheses.csv --config config/agent_config.yaml --family-scope confirmatory --status-filter in_PAP tested --out analysis/results.csv --audit-table tables/fdr_adjustment_confirmatory.csv && \
  python analysis/code/run_robustness_checks.py --dataset data/clean/childhoodbalancedpublic_with_csa_indicator.csv --config config/agent_config.yaml --qc-dir qc --tables-dir tables/robustness --hypotheses HYP-001 HYP-003
  ```
  Record the combined command string in `analysis/decision_log.csv` and `papers/main/MANIFEST.md` (if used) each time it is executed.

## Documentation hooks
- Notebook link: add loop entry referencing this plan to `notebooks/research_notebook.md`.
- Manifest: confirm the command strings remain current (already registered under “Confirmatory analyses”).
- Evidence: if robustness checks motivate literature updates, append sources to `lit/bibliography.bib` and `lit/evidence_map.csv` with Semantic Scholar metadata.

All commands assume execution from repository root with Python 3.11 environment captured in `artifacts/session_info.txt`.
