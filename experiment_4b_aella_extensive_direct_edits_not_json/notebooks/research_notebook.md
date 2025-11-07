# Research Notebook — Childhood Resilience Study
_Date: 2025-11-07_

## Project Setup
- Dataset copied into `data/raw/childhoodbalancedpublic_original.csv` (original remains read-only). 718 columns, 14,443 rows.
- Seed set to `20251016` per `config/agent_config.yaml`; all future scripts must accept this seed.
- Manuscript alignment plan: every analysis step will cite the corresponding section in `papers/main/manuscript.tex` and its Markdown twin. Drafting notes captured here before syncing to LaTeX via `latexmk` logs in `papers/main/build_log.txt`.

## Data Audit (Exploratory)
Command to reproduce snapshot statistics:
```bash
python - <<'PY'
import pandas as pd
path = 'data/raw/childhoodbalancedpublic_original.csv'
df = pd.read_csv(path)
print({'rows': len(df), 'cols': len(df.columns), 'missing_frac': float(df.isna().mean().mean())})
PY
```
Observations: `missing_frac ≈ 0.446`, dtype warning on some mixed columns (address in data cleaning script). No survey weights detected; default to SRS until confirmed otherwise (see `docs/survey_design.yaml`).

## Candidate Hypotheses (Descriptive/Associational)
1. **H1 (Wellbeing):** Higher childhood religious adherence (`externalreligion`) associates with greater adult depression tendency (`wz901dj`), potentially indicating internalized pressure.
2. **H2 (Guidance → Health):** Strong parental guidance (`pqo6jmj`) predicts better adult self-rated health (`okq5xh8`).
3. **H3 (Abuse → Self-worth):** Childhood emotional abuse (`mds78zu`) correlates with lower adult self-love (`2l8994l`).
4. **H4 (Politics ↔ Religion):** Liberal self-placement (`liberal`) negatively associated with current religious practice (`religion`).
5. **H5 (SES Mobility):** Higher teen class (`classteen`) predicts higher current net worth bracket (`networth`).

Details captured in `analysis/hypotheses.csv` with family assignments for later BH correction.

## Pre-Analysis Plan Draft
- `analysis/pre_analysis_plan.md` (status: draft) specifies estimands for H1–H3 with modeling approach (ordered logit / linear probability with robust SEs).
- Repro command placeholder: `python analysis/scripts/run_pap_models.py --config analysis/pre_analysis_plan.md --seed 20251016` (script to be implemented before freezing).
- Freeze procedure: once design finalized, tag commit `pap-v1` and record `freeze_commit` + registry URL.

## Literature Workflow
- Semantic Scholar queries will be executed via `python scripts/semantic_scholar_cli.py ...` with outputs stored in `lit/queries/loop_000/` and logged in `analysis/decision_log.csv`.
- Evidence tracking: `lit/evidence_map.csv` (with DOI-backed entries) and `lit/bibliography.bib/.json` kept in sync. Each manuscript claim will map to at least one entry via `claim_id`.

## Next Steps
1. Implement reproducible data cleaning scripts (`analysis/code/`) to construct analysis-ready variables.
2. Enrich codebook/code design docs with automated generation.
3. Expand literature base to ≥3 DOI-backed sources before advancing phase.
4. Draft DAG + identification memo skeleton once key pathways confirmed.
