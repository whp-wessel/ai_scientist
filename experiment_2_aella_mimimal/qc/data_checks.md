# Data Quality Checklist (Bootstrap)

- [ ] Confirm file integrity for `childhoodbalancedpublic_original.csv` (checksum pending).
- [x] Verify survey weight variable presence once metadata is populated in `docs/survey_design.yaml`. (2025-01-17; see `qc/design_validation.md`.)
- [x] Inspect missingness for key variables (`religion`, `biomale`, `externalreligion`, `h33e6gg`). (2025-01-17; see `tables/summary_key_outcomes.csv`.)
- [x] Monitor sponsor channels for incoming design metadata; confirm none received as of 2025-11-03 (see `qc/design_metadata_monitor.md`).
- [x] Confirm `religion` active-practice recode (`religion > 0`) before H1 analysis (2025-11-04; see `tables/h1_religion_by_biomale.csv`).
- [ ] Validate categorical coding against `docs/codebook.json` once completed.
- [ ] Record any data issues and remediation steps here before analysis loops proceed.

**Regeneration commands:**
- `python scripts/bootstrap_artifacts.py`
- `python scripts/design_scan.py --csv childhoodbalancedpublic_original.csv`
- `python scripts/exploratory_summaries.py --csv childhoodbalancedpublic_original.csv --config config/agent_config.yaml --out tables/summary_key_outcomes.csv`
- `python scripts/analyze_h1_religion_by_biomale.py --csv childhoodbalancedpublic_original.csv --config config/agent_config.yaml --design docs/survey_design.yaml --out tables/h1_religion_by_biomale.csv --diff-out tables/h1_religion_by_biomale_diff.csv --manifest artifacts/h1_religion_by_biomale_manifest.json`
