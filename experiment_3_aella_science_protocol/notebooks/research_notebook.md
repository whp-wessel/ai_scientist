# Research Notebook
Updated: 2025-11-03T20:56:41Z | Seed: 20251016

Reproducibility: run `python analysis/code/bootstrap_setup.py`; env info in `artifacts/session_info.txt`; checksums in `artifacts/checksums.json`.

Hypotheses: HYP-001 childhood class ↑ self-love; HYP-002 current class ↓ depression; HYP-003 CSA ↑ anxiety; HYP-004 support ↑ self-love.

2025-11-03T20:29Z — Survey design validation confirms no sampling weights/strata/clusters present in `childhoodbalancedpublic_original.csv`; working under simple random sampling assumption. See `qc/survey_design_validation.md` regenerated via `python analysis/code/validate_survey_design.py`.

2025-11-03T20:34Z (Exploratory) — Generated outcome distributions under SRS assumption via\
 `python analysis/code/eda_weighted_summaries.py --dataset childhoodbalancedpublic_original.csv --codebook docs/codebook.json --config config/agent_config.yaml --out-summary tables/exploratory_outcome_summary.csv --out-distribution tables/exploratory_outcome_distribution.csv`.\
 Key findings: self-love skews positive (median=1), while depression/anxiety skew negative (median -1). All categories exceed the small-cell threshold (10). Outputs: `tables/exploratory_outcome_summary.csv`, `tables/exploratory_outcome_distribution.csv`.

TODO: document literature and exploratory findings (labelled "Exploratory"); derive CSA indicator prior to PAP freeze. Prepare `papers/main/MANIFEST.md` when manuscript drafting begins.

2025-11-03T20:50Z — Schema alignment completed via \
`python analysis/code/align_codebook_schema.py --dataset childhoodbalancedpublic_original.csv --codebook-in docs/codebook.json --codebook-out docs/codebook.json`.\
Validated storage types, allowed ranges, and missingness for six analysis variables; suppressed small cells (<10) and now omit detailed frequency tables to avoid sparse tail disclosure. Details recorded in `qc/schema_alignment.md`.

2025-11-03T20:56Z (QC) — Profiled hypothesis-relevant missingness via \
`python analysis/code/profile_missingness.py --dataset childhoodbalancedpublic_original.csv --codebook docs/codebook.json --hypotheses analysis/hypotheses.csv --config config/agent_config.yaml --out-csv tables/missingness_profile.csv --out-patterns tables/missingness_patterns.csv`.\
Suppressed cell counts <10; see `tables/missingness_profile.csv` (+ `.meta.json`) and `tables/missingness_patterns.csv`. Social support predictor `In general, people in my *current* social circles tend treat me really well (tmt46e6)` exhibits 97.35% missingness—flagged for feasibility review. `CSA_score_indicator` absent in raw data; queued derivation task (T-006) before PAP freeze.
