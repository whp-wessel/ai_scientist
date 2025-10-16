# Research Notebook

## 2025-10-16T14:45Z — Loop 10 (Exploratory)
- Checked existing reproducibility artifacts (`artifacts/session_info.txt`, `artifacts/checksums.json`); no regeneration needed this loop.
- Authored and ran `analysis/code/eda_monogamy_by_religion.py` (seed 20251016) to create `tables/exploratory_monogamy_by_religion.csv` + `.md` and metadata JSON.
- Cross-tab indicates higher religious engagement corresponds to greater shares of full monogamy (e.g., 80% among "Yes, very seriously" vs 54% among non-practitioners) under the SRS assumption.
- All cells cleared the k=10 disclosure threshold; suppression flag retained in outputs for downstream audit.
- Outstanding: survey-weight metadata request (`T-003`) remains with data provider; PAP still marked draft pending design clarification.
