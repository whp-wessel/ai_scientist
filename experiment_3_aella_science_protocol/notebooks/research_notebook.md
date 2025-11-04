# Research Notebook
Updated: 2025-11-04T09:25:35Z | Seed: 20251016

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
 Suppressed cell counts <10; see `tables/missingness_profile.csv` (+ `.meta.json`) and `tables/missingness_patterns.csv`. Social support predictor `In general, people in my *current* social circles tend treat me really well (tmt46e6)` exhibits 97.35% missingness—flagged for feasibility review. At that point `CSA_score_indicator` was absent in raw data, motivating derivation task T-006 prior to PAP freeze.

2025-11-03T21:05Z (Derived) — Established canonical data folders (`data/raw`, `data/clean`) and derived CSA exposure indicator via \
`python analysis/code/derive_csa_indicator.py --dataset data/raw/childhoodbalancedpublic_original.csv --out-dataset data/clean/childhoodbalancedpublic_with_csa_indicator.csv --out-distribution tables/csa_indicator_distribution.csv --config config/agent_config.yaml --codebook-in docs/codebook.json --codebook-out docs/codebook.json`.\
Output dataset stored at `data/clean/childhoodbalancedpublic_with_csa_indicator.csv`; distribution table `tables/csa_indicator_distribution.csv` confirms 22.31% report any CSA (no cells <10). Updated `docs/codebook.json` with new binary predictor metadata and refreshed `artifacts/checksums.json`. PAP robustness section expanded for HYP-001/HYP-003 (see `analysis/pre_analysis_plan.md`).

2025-11-03T21:35Z (Exploratory) — Assessed feasibility of the social support predictor for HYP-004 via \
`python analysis/code/social_support_missingness.py --dataset data/clean/childhoodbalancedpublic_with_csa_indicator.csv --out-csv tables/social_support_missingness.csv --config config/agent_config.yaml`.\
 Key finding: original item (`...tend treat me really well (tmt46e6)`) covers only 383 respondents (97.35% missing), while an instrument twin (`...tend to treat me really well (71mn55g)`) covers 14,054 respondents. Responses do not overlap, suggesting form-version routing. Recommendation logged in `qc/social_support_feasibility.md` to pivot HYP-004 to the high-coverage item pending instrument confirmation.

2025-11-03T22:05Z (QC) — Verified instrument equivalence across the tmt46e6 and 71mn55g social-support items via \
`python analysis/code/verify_social_support_equivalence.py --dataset data/clean/childhoodbalancedpublic_with_csa_indicator.csv --out-summary tables/social_support_equivalence_summary.csv --out-distribution tables/social_support_equivalence_distributions.csv --out-overlap tables/social_support_instrument_overlap.csv --config config/agent_config.yaml --columns "In general, people in my *current* social circles tend treat me really well (tmt46e6)" "In general, people in my *current* social circles tend to treat me really well (71mn55g)"`.\
 Findings: identical 7-point scales (−3 to +3), shared prompt wording apart from insertion of “to,” and mutually exclusive routing (no respondents with both non-missing). Distribution tables suppress cells <10 as required. Documented evidence in `qc/social_support_equivalence.md`; updated codebook and hypothesis registry to pivot HYP-004 to instrument 71mn55g.

2025-11-03T22:45Z (Planning) — Drafted confirmatory model equations and executable skeleton via \
`python analysis/code/confirmatory_models.py --dataset data/clean/childhoodbalancedpublic_with_csa_indicator.csv --config config/agent_config.yaml --survey-design docs/survey_design.yaml --hypotheses HYP-001 HYP-003 --results-csv analysis/results.csv --overwrite`.\
 Outcome: PAP now records explicit model statements for HYP-001 and HYP-003, and hypothesis registry flags them `in_PAP`. The script writes deterministic HC3 OLS outputs seeded at 20251016 and will feed `analysis/results.csv` post-freeze. Next step: freeze PAP and tag commit prior to confirmatory execution.

2025-11-04T07:58Z (Confirmatory prep) — Frozen the PAP (HYP-001, HYP-003) and established reproducibility checkpoint. Created `reports/findings_v0.1.md`, `papers/main/manuscript.tex`, and `papers/main/MANIFEST.md` to enforce manuscript parity. Updated PAP scope to classify HYP-002/HYP-004 as exploratory backlog. Next action: tag commit `pap-freeze-20251104` after confirming reproducibility artifacts (`artifacts/session_info.txt`, `artifacts/checksums.json`) and implement FDR scripting (T-011).

2025-11-04T08:19Z (Confirmatory) — Executed PAP-frozen HC3 OLS for HYP-001 and HYP-003 via\
`python analysis/code/confirmatory_models.py --dataset data/clean/childhoodbalancedpublic_with_csa_indicator.csv --config config/agent_config.yaml --survey-design docs/survey_design.yaml --hypotheses HYP-001 HYP-003 --results-csv analysis/results.csv --overwrite`.\
Listwise deletion removed ≤0.05% rows per model. Self-love rises ~0.18 points per childhood class step (95% CI [0.16, 0.20]); CSA exposure associates with −0.49 anxiety agreement shift (95% CI [−0.56, −0.42]). Results recorded in `analysis/results.csv`; q-values pending BH adjustment (T-013).

2025-11-04T09:10Z (Planning) — Implemented Benjamini–Hochberg utility (`analysis/code/fdr_adjust.py`) and robustness automation driver (`analysis/code/run_robustness_checks.py`) per PAP commitments. Regeneration commands captured in PAP/manifest; outputs will populate `tables/fdr_adjustment_confirmatory.csv` and `tables/robustness/robustness_checks_summary.{csv,json}` with QC notes in `qc/`. Ready to proceed with confirmatory estimation (T-012).

2025-11-04T09:25Z (Confirmatory) — Applied BH FDR via\
`python analysis/code/fdr_adjust.py --results analysis/results.csv --hypotheses analysis/hypotheses.csv --config config/agent_config.yaml --family-scope confirmatory --audit-table tables/fdr_adjustment_confirmatory.csv`.\
Only the two confirmatory hypotheses qualified; q-values matched raw p-values (both <1e-40). Audit log stored at `tables/fdr_adjustment_confirmatory.csv` with seed annotation 20251016.

2025-11-04T09:25Z (Robustness) — Executed pre-specified sensitivity checks via\
`python analysis/code/run_robustness_checks.py --dataset data/clean/childhoodbalancedpublic_with_csa_indicator.csv --config config/agent_config.yaml --qc-dir qc --tables-dir tables/robustness --hypotheses HYP-001 HYP-003`.\
HYP-001 retained positive slope across helmert, ordinal-logit, and z-score codings (e.g., z-score beta=0.097, p=1.6e-51). HYP-003 consistently showed a negative CSA association (logit OR=0.57, 95% CI approx [0.51, 0.64]), contradicting the preregistered direction. Outputs recorded in `tables/robustness/robustness_checks_summary.{csv,json}` with QC notes under `qc/`.

2025-11-04T10:35Z (Synthesis) — Drafted confirmatory narrative describing magnitudes, interpretability, and robustness for HYP-001/HYP-003. Updated `reports/findings_v0.2.md` (with changelog from v0.1), synchronized `papers/main/manuscript.tex`, and refreshed `papers/main/MANIFEST.md` parity notes. Regeneration remains manual editing; cite this entry when propagating future revisions.

2025-11-04T10:45Z (Diagnostics) — Ran \
`python analysis/code/diagnose_csa_anxiety_direction.py --dataset data/clean/childhoodbalancedpublic_with_csa_indicator.csv --config config/agent_config.yaml --out-table tables/diagnostics/csa_anxiety_direction.csv --out-md qc/csa_anxiety_direction.md`.\
Group means show CSA-exposed respondents average −1.50 vs −0.64 for non-exposed (difference = −0.861, 95% CI [−0.932, −0.789]), confirming the sign reversal stems from lower reported anxiety among the exposed group rather than coding inversion. Documented details in `qc/csa_anxiety_direction.md`.

2025-11-04T11:05Z (QC) — Reviewed anxiety instrument coding and routing via \
`python analysis/code/review_anxiety_instrument.py --dataset data/raw/childhoodbalancedpublic_original.csv --config config/agent_config.yaml --codebook docs/codebook.json --out-table tables/diagnostics/anxiety_item_review.csv --out-md qc/anxiety_item_routing.md`.\
Confirmed the instrument-coded column `npvfh98` aligns with a centred −3 to +3 agreement scale, with coverage ≈99.96% and no detected routing flags; alias column `I tend to suffer from anxiety -neg` is identical. Missingness remains below the disclosure threshold (<10) and mirrors other mental-health items. Findings recorded in `qc/anxiety_item_routing.md` and summary table `tables/diagnostics/anxiety_item_review.csv`.

2025-11-04T12:28Z (Literature) — Contextualized the CSA-anxiety sign reversal by querying Semantic Scholar. To avoid rate limits, ran `sleep 120 && curl -s 'https://api.semanticscholar.org/graph/v1/paper/search?query=childhood%20sexual%20abuse%20anxiety%20adult&limit=3&fields=title,authors,year,venue,url,journal,externalIds'` (stored in `lit/queries/20251104_semanticscholar_csa_anxiety_adult.json`) and `sleep 120 && curl -s 'https://api.semanticscholar.org/graph/v1/paper/search?query=childhood%20sexual%20abuse%20anxiety%20depression%20network%20analysis&limit=1&fields=title,authors,year,venue,url,journal,externalIds,abstract'` (stored in `lit/queries/20251104_semanticscholar_csa_anxiety_network.json`); documented meta-query results manually in `lit/queries/20251104_semanticscholar_csa_anxiety_meta.json` due to intermittent 429 responses. Summarized high-quality syntheses (Lindert et al. 2014; Hashim et al. 2024) and a network study (Li et al. 2023) showing elevated anxiety burden among CSA survivors. Updated `lit/bibliography.bib`, `lit/bibliography.json`, and `lit/evidence_map.csv`; added interpretive narrative to `reports/findings_v0.3.md` and synchronized `papers/main/manuscript.tex`.
