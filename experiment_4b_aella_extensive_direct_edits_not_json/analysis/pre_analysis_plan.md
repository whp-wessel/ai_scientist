status: draft

# Pre-Analysis Plan — Bootstrap Draft

> This document is a working outline for the PAP. It will remain in **draft** status
> until: (a) survey design inputs are confirmed, (b) hypotheses are finalized, and
> (c) the plan is frozen with a recorded git commit/tag (`freeze_commit:`) plus an
> external registry URL. No confirmatory analysis will run before that freeze.

## 1. Governance and Provenance
- Dataset: `childhoodbalancedpublic_original.csv` (n=14,443; 718 columns).
- Codebook: `docs/codebook.json` (placeholder, to be replaced by the official version).
- Survey design: `docs/survey_design.yaml` (SRS assumption until weights appear).
- Global seed: `20251016` (see `config/agent_config.yaml` and `artifacts/seed.txt`).
- Future freeze metadata will appear at the top of this file as `status: frozen (commit <sha>, tag pap-v1)` plus `registry_url: <OSF link>`.
- Corresponding manuscript: `papers/main/manuscript.tex` (to be kept in sync with Markdown outputs per `notebooks/research_notebook.md`).

## 2. Analytic Targets (Priority Hypotheses)

| ID | Outcome | Predictors | Estimand (draft) | Notes |
| --- | --- | --- | --- | --- |
| H1 (C1) | `religion` (binary) | `externalreligion`, `Religionchildhood`; controls `selfage`, `education` | Weighted difference in probability of currently practicing religion between top vs. bottom tertiles of `externalreligion`. | Requires harmonizing ordinal scale; logistic regression with marginal effects. |
| H2 (C2) | `networth` (ordinal) | `classchild`, `classcurrent`, `education`; controls `selfage`, `biomale` | Ordered logit slope of `classchild` on `networth`, reported as marginal effect on probability of being in the top wealth bin. | Restrict to respondents with `networth` ∈ [1,4]; handle potential non-monotonicity. |
| H3 (C3) | `liberal` (ordinal) | `religion`; controls `selfage`, `education`, `classcurrent` | Average marginal effect of `religion` on probability of selecting the most liberal response. | Treat `liberal` as ordered categorical; confirm coding from codebook. |

Hypotheses H4+ remain exploratory and will not be promoted to PAP until the above three are finalized.

## 3. Data Preparation Plan
1. Load raw CSV (`python -m analysis.scripts.load_raw --input childhoodbalancedpublic_original.csv --seed 20251016` — script to be implemented).
2. Create clean dataset under `data/clean/childhood_baseline.parquet` with:
   - Column selection limited to PAP variables plus audit columns.
   - Harmonized categorical levels (see `docs/codebook.json` todos).
3. Record checksums for every derivative file via `python scripts/hash_artifacts.py data/clean/childhood_baseline.parquet`.
4. Document all transformations in `notebooks/research_notebook.md` (Exploratory) and `qc/data_checks.md`.

## 4. Survey Design Handling
- Pending official design inputs, assume simple random sampling with transparent caveats.
- Once weights are delivered, update `docs/survey_design.yaml`, rerun `qc/data_checks.md`, and only then freeze PAP.
- Regardless of design, enforce small-cell suppression (`k=10`) and document checks in `qc/disclosure_check_loop_000.md`.

## 5. Estimation Strategy (Draft)
| Hypothesis | Model | Weighting/Variance | Key Outputs |
| --- | --- | --- | --- |
| H1 | Logistic regression + AMEs | Use survey weights if delivered; otherwise SRS with HC2 SEs | Estimate, SE, 95% CI, n (weighted/unweighted), q-value (BH within family). |
| H2 | Ordered logit (survey-weighted) | Same as above; check proportional odds via Brant test | Report marginal effects for moving from lower to higher wealth tiers. |
| H3 | Ordered logit or multinomial logit if proportional odds fails | Survey design as above | AME on `liberal=3` plus contrasts vs. middle category. |

Robustness checks per hypothesis (to be executed post-freeze):
1. Alternative codings (e.g., dichotomizing `liberal`).
2. Excluding respondents with missing childhood class data.
3. Negative-control predictor (e.g., `randomize` columns) to verify Type I error.

## 6. Multiplicity and Reporting
- Hypothesis families align with `analysis/hypotheses.csv` (`socialization`, `socioeconomic`, `ideology`).
- Apply Benjamini–Hochberg per family at q=0.05.
- Record outcome paths in `analysis/results.csv` (`family`, `targeted`, `bh_in_scope` columns mandatory).

## 7. Reproducibility Hooks
- Core command sequence (to be scripted in `analysis/code/`):
  1. `python analysis/code/prepare_data.py --config config/agent_config.yaml`
  2. `python analysis/code/run_models.py --hypotheses H1,H2,H3 --seed 20251016`
  3. `python analysis/code/postprocess.py --results analysis/results.csv`
- Each command will log to `artifacts/repro_report.md`. Randomness (e.g., bootstraps) must set `numpy.random.seed(20251016)` and counterpart seeds for other libs.

## 8. Outstanding Items Before Freeze
- [ ] Validate survey design inputs (weights, strata, clusters).
- [ ] Build measurement validity dossier (`qc/measures_validity.md`) for all PAP variables.
- [ ] Collect ≥3 DOI-backed sources per claim and record them in `lit/evidence_map.csv`.
- [ ] Draft `reports/identification.md` and `figures/dag_design.png`.
- [ ] Sync `papers/main/manuscript.tex` with Markdown narrative and log LaTeX build in `papers/main/build_log.txt`.

Once all checkboxes are resolved, update the header to `status: frozen`, append `registry_url`, and record `freeze_commit`. Until then, analyses remain exploratory only.
