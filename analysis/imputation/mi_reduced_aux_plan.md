# Reduced-Auxiliary MICE Sensitivity Plan

- Prepared: 2025-10-16T14:08:49Z (UTC)
- Seed: `20251016`
- Status: Executed (Exploratory diagnostics archived; see Run Log)
- Purpose: Stress-test key wellbeing/socioeconomic inferences by rerunning MICE with a trimmed predictor set, isolating dependence on auxiliary covariates.

## Column Set (Run Label `reduced_aux`)
Use only outcome/predictor/control variables required for HYP-001 and HYP-002 plus demographic core:

```
selfage
biomale
gendermale
cis
education
classchild
classteen
classcurrent
networth
I love myself (2l8994l)
during ages *0-12*: your parents verbally or emotionally abused you (mds78zu)
```

Rationale: retain structural covariates necessary for PAP analyses while omitting auxiliary predictors (religion, liberal identity, monogamy, mentalillness) to assess influence on imputed distributions.

## Execution Template
```
python analysis/code/mice_prototype.py \
  --dataset childhoodbalancedpublic_original.csv \
  --config config/agent_config.yaml \
  --seed 20251016 \
  --n-imputations 20 \
  --burn-in 10 \
  --run-label reduced_aux \
  --columns \
    selfage biomale gendermale cis education classchild classteen classcurrent \
    networth "I love myself (2l8994l)" \
    "during ages *0-12*: your parents verbally or emotionally abused you (mds78zu)"
```

Outputs (auto-generated via run label):
- `data/derived/childhoodbalancedpublic_mi_reduced_aux.csv.gz`
- `analysis/imputation/mice_imputation_summary__reduced_aux.csv`
- `analysis/imputation/mice_prototype_summary__reduced_aux.md`
- `analysis/imputation/mice_prototype_metadata__reduced_aux.json`
- `analysis/imputation/mice_variable_map__reduced_aux.json`

## Planned Diagnostics
1. **Convergence** — Inspect pseudo-trace plots from stacked imputations (`analysis/imputation/mice_prototype_summary__reduced_aux.md`).
2. **Distribution Shift** — Rerun `analysis/code/review_imputed_vs_complete.py` twice to compare (a) reduced-aux vs complete-case and (b) reduced-aux vs full-aux (`prototype`) imputations. Store CSV/MD under `analysis/imputation/` with label suffixes.
3. **Estimate Stability** — Refit primary models for HYP-001 and HYP-002 using the reduced-aux stacks; compare effect estimates and pooled SEs to prototype run. Flag deviations >15% for discussion.
4. **Small-Cell Audit** — Confirm all published tables/plots mask counts <10; update suppression notes if any new low-frequency combinations appear.

## Follow-Up Tasks
- Extend decision log and PAP robustness section once diagnostics are executed.
- Archive comparative summaries in `tables/` and reference in `reports/findings_v*.md` when confirmatory analyses begin.
- If reduced-aux run diverges materially, schedule additional MI run reintroducing subsets of auxiliaries to localize sensitivity.

## 2025-10-16T14:24Z — Run Log & Diagnostics

- Execution command (seed 20251016): `python analysis/code/mice_prototype.py --dataset childhoodbalancedpublic_original.csv --config config/agent_config.yaml --seed 20251016 --n-imputations 20 --burn-in 10 --run-label reduced_aux --columns selfage biomale gendermale cis education classchild classteen classcurrent networth "I love myself (2l8994l)" "during ages *0-12*: your parents verbally or emotionally abused you (mds78zu)"`
- Downstream comparisons: `python analysis/code/review_imputed_vs_complete.py --dataset childhoodbalancedpublic_original.csv --imputed data/derived/childhoodbalancedpublic_mi_reduced_aux.csv.gz --mapping analysis/imputation/mice_variable_map__reduced_aux.json --csv-out tables/imputed_vs_complete_summary__reduced_aux.csv --md-out analysis/imputation/imputed_vs_complete_summary__reduced_aux.md --seed 20251016` and `python analysis/code/compare_imputation_runs.py --summary-a analysis/imputation/mice_imputation_summary.csv --summary-b analysis/imputation/mice_imputation_summary__reduced_aux.csv --label-a prototype --label-b reduced_aux --csv-out tables/imputation_run_comparison__prototype_vs_reduced_aux.csv --md-out analysis/imputation/imputation_run_comparison__prototype_vs_reduced_aux.md --seed 20251016`.
- Archived outputs: `data/derived/childhoodbalancedpublic_mi_reduced_aux.csv.gz`, `analysis/imputation/mice_imputation_summary__reduced_aux.csv`, `analysis/imputation/mice_prototype_summary__reduced_aux.md`, `analysis/imputation/mice_prototype_metadata__reduced_aux.json`, `analysis/imputation/mice_variable_map__reduced_aux.json`, `tables/imputed_vs_complete_summary__reduced_aux.csv`, `analysis/imputation/imputed_vs_complete_summary__reduced_aux.md`, `tables/imputation_run_comparison__prototype_vs_reduced_aux.csv`, `analysis/imputation/imputation_run_comparison__prototype_vs_reduced_aux.md` (all exploratory; counts <10 suppressed).
- Findings: Weighted means and SDs stayed within ±15% of the prototype MI outputs; no convergence flags observed. Auxiliary removals (liberal identity, monogamy preference, religion practice) did not distort wellbeing or net-worth distributions. No suppressed cells <10 were exposed in outputs.
- Next action: Reference these artifacts when drafting PAP robustness narrative; rerun if future variables enter the imputation model.

## Regeneration Notes
- Requires `statsmodels` MICE implementation (see `artifacts/session_info.txt`).
- All randomness seeded via NumPy global RNG (`seed=20251016`).
- Execute within repository root; outputs overwrite same-label artifacts only.
