# QC Checklist
Generated: 2025-11-03T20:01:43Z | Seed: 20251016
Regeneration: `python analysis/code/bootstrap_setup.py --artifact qc/data_checks.md`
- [x] Dataset present (read-only).
- [x] Align schema with codebook (see `qc/schema_alignment.md`).
- [x] Confirm weight/strata/cluster variables (see `qc/survey_design_validation.md`).
- [ ] Summarise missingness for key variables.
- [ ] Ensure no small cells (n<10) in shared outputs.
