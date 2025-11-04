# CSA–Anxiety Diagnostics & Heterogeneity Plan
Generated: 2025-11-04T14:05:00Z | Seed: 20251016

## Objectives
1. Diagnose why CSA exposure associates with lower agreement on “I tend to suffer from anxiety (npvfh98)-neg,” contrary to prior literature and preregistered expectations.
2. Evaluate whether anxiety measurement behaves consistently across demographic strata (gender, cis identity, age cohorts, childhood class).
3. Integrate diagnostic evidence into reporting, with reproducible code paths and suppression safeguards.

## Work Packages
| WP | Focus | Description | Deliverables | Status |
|---|---|---|---|---|
| WP1 | Convergent validity | Correlate anxiety item with companion affect measures (depression, stress, self-love), estimate polychoric correlations, and benchmark reliability. | `tables/diagnostics/anxiety_convergence.csv`, `qc/anxiety_convergence.md`, literature note in `lit/evidence_map.csv`. | Planned (Task T-017/T-022). |
| WP2 | Subgroup heterogeneity | Extend CSA models with CSA×(cis identity, age cohort, childhood class) interactions in OLS and ordinal logit; report weighted and unweighted subgroup means with suppression checks. | `analysis/code/anxiety_interactions.py`, `tables/diagnostics/anxiety_interactions.csv`, `qc/anxiety_subgroup_extensions.md`. | Planned (Task T-018). |
| WP3 | Scale behaviour | Recode anxiety item to 0–6 and 3-bin scales; compare descriptive distributions and re-estimate CSA effects to ensure directional consistency. | `tables/diagnostics/anxiety_scale_transformations.csv`, `qc/anxiety_scale_transformations.md`. | Pending (follow-on). |
| WP4 | Reporting integration | Summarise diagnostic findings in `reports/findings_v*.md` and `papers/main/manuscript.tex`, updating limitations and interpretation sections. | Report changelog entry; manifest note. | Pending (after WP1–WP3). |

## Required Scripts & Commands
- Convergent validity (WP1) — to be implemented:  
  `python analysis/code/evaluate_anxiety_convergence.py --dataset data/clean/childhoodbalancedpublic_with_csa_indicator.csv --config config/agent_config.yaml --out-table tables/diagnostics/anxiety_convergence.csv --out-md qc/anxiety_convergence.md --seed 20251016`
- Interaction modelling (WP2) — to be implemented:  
  `python analysis/code/anxiety_interactions.py --dataset data/clean/childhoodbalancedpublic_with_csa_indicator.csv --config config/agent_config.yaml --interactions CSA_score_indicator:cis_identity CSA_score_indicator:age_cohort CSA_score_indicator:classchild_collapsed --out-table tables/diagnostics/anxiety_interactions.csv --out-md qc/anxiety_subgroup_extensions.md --seed 20251016`
- Scale transformations (WP3) — extension of existing robustness driver:  
  `python analysis/code/run_robustness_checks.py --dataset data/clean/childhoodbalancedpublic_with_csa_indicator.csv --config config/agent_config.yaml --hypotheses HYP-003 --robustness-set anxiety_scale_recodes --qc-dir qc --tables-dir tables/robustness --seed 20251016`

All scripts must log the seed, reference `docs/codebook.json` for variable labels, and honour the n < 10 suppression rule. Prototype notebooks should export code to `analysis/code/` before integration.

## Data & Privacy Considerations
- Maintain derived dataset `data/clean/childhoodbalancedpublic_with_csa_indicator.csv`; do not overwrite raw inputs.
- Suppress or aggregate subgroup cells with post-weighted counts <10; consider collapsing age 60+ with 45–59 if required.
- Document any imputation (currently none planned) and justify deterministic handling of missing data.

## Integration Checkpoints
1. Append Decision Log entries per executed module, referencing Task IDs.
2. Update `papers/main/MANIFEST.md` with regeneration commands and diagnostic status notes.
3. Propagate findings to `reports/findings_v0.5.md` (next version) and sync with LaTeX.
4. Refresh `artifacts/state.json` backlog after each module.

## Next Steps (Loop Priorities)
- **Task T-017** (Priority 2): Build `evaluate_anxiety_convergence.py`, generate WP1 outputs, and summarise implications for measurement validity.
- **Task T-018** (Priority 3): Draft interaction modelling script (`anxiety_interactions.py`) and pre-specify reporting tables/QC templates.
- After T-017 and T-018, queue WP3 execution and reporting updates (new backlog items).

> _This plan is curated manually; edit this Markdown directly to reflect progress. Include the command snippets above in the MANIFEST once scripts exist._
