# Research Notebook

## 2025-10-16T14:45Z — Loop 10 (Exploratory)
- Checked existing reproducibility artifacts (`artifacts/session_info.txt`, `artifacts/checksums.json`); no regeneration needed this loop.
- Authored and ran `analysis/code/eda_monogamy_by_religion.py` (seed 20251016) to create `tables/exploratory_monogamy_by_religion.csv` + `.md` and metadata JSON.
- Cross-tab indicates higher religious engagement corresponds to greater shares of full monogamy (e.g., 80% among "Yes, very seriously" vs 54% among non-practitioners) under the SRS assumption.
- All cells cleared the k=10 disclosure threshold; suppression flag retained in outputs for downstream audit.
- Outstanding: survey-weight metadata request (`T-003`) remains with data provider; PAP still marked draft pending design clarification.

## 2025-10-16T14:52:28Z — Loop 11 (Planning)
- Re-verified reproducibility artifacts (`artifacts/session_info.txt`, `artifacts/checksums.json`, `artifacts/seed.txt`) remain current; no regeneration required.
- Updated `analysis/pre_analysis_plan.md` with ordered-logit specification for HYP-003, incorporating SRS assumption while weight metadata request (`T-003`) is pending.
- Marked HYP-003 as `in_PAP` in `analysis/hypotheses.csv`, adding relationship-status control and reference to exploratory monogamy cross-tab.
- Documented confirmatory command path (`analysis/code/run_pap_models.py`) and disclosure safeguards in PAP to pre-position confirmatory run once weights arrive.
- Next: await survey-design response; once resolved, freeze PAP and script confirmatory analysis for HYP-003 alongside HYP-001/002.


## 2025-10-17T15:59:28+00:00 — Loop 12 (Exploratory)
- Confirmed reproducibility artifacts remained current and refreshed `artifacts/checksums.json` for raw and derived datasets.
- Authored `analysis/code/run_pap_models.py` implementing the PAP ordered-logit path for HYP-003 with SRS assumptions and HC1 SEs.
- Ran the script in exploratory mode (seed 20251016), generating coefficient and probability tables under disclosure checks.
- Logged that relationship-status control variables are unavailable at required counts; script records omission until data provider resolves.

## 2025-10-17T16:18Z — Loop 13 (Exploratory)
- Spot-checked reproducibility artifacts (`artifacts/session_info.txt`, `artifacts/checksums.json`, `artifacts/seed.txt`) — no refresh required this loop.
- Extended `analysis/code/run_pap_models.py` to cover HYP-001 (MI-pooled HC1 linear model) and HYP-002 (MI-pooled ordered logit) with Rubin pooling seeded at 20251016.
- Executed exploratory runs for HYP-001/002 producing `tables/exploratory_hyp001_*` and `tables/exploratory_hyp002_*` bundles plus metadata JSON for manifesting.
- Updated `analysis/pre_analysis_plan.md` with the MI runner milestone while PAP remains in draft pending weight metadata (T-003).

## 2025-10-17T22:59Z — Loop 14 (Exploratory)
- Refreshed reproducibility artifacts: captured current environment/package snapshot in `artifacts/session_info.txt` and recomputed dataset SHA-256 hashes in `artifacts/checksums.json`.
- Patched `analysis/code/run_mi_robustness.py` to restore the HYP-002 complete-case ordered-logit path (Series casting + category labeling) and prevent numpy attribute errors.
- Re-ran `python analysis/code/run_mi_robustness.py --seed 20251016` to generate robustness bundles for HYP-001/002 across complete-case, MI prototype, and reduced-auxiliary scenarios with disclosure checks.
- Logged scenario narratives in `analysis/imputation/robustness_hyp001_mi_scenarios.md` / `_hyp002_...` and regenerated coefficient/probability tables under the global seed.
