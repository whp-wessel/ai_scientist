## Baseline Inputs

- **Dataset**: `childhoodbalancedpublic_original.csv` (14,443 rows × 718 columns). Initial skim via pandas (command logged in `analysis/decision_log.csv`) confirms rich childhood environment measures plus adult well-being scales.
- **Survey design**: No weight/strata/cluster columns detected in the raw header scan. Default stance is Simple Random Sample (SRS) with an explicit justification to be written in the PAP unless design files surface.
- **Codebook status**: _Missing_. TODO — request or derive a machine-readable codebook summarizing question text, response scales, and recodes.
- **Config + tooling**: Default seed 20251016. Semantic Scholar access routed through `scripts/semantic_scholar_cli.py` (creates `artifacts/.s2_rate_limit.json` to enforce 1 req/s).

### TODOs
1. ✅ Confirmed dataset dimensions and lack of design variables.
2. ☐ Build/ingest official codebook (blocked until provided).
3. ☐ Document SRS justification + diagnostics in PAP once descriptive stats are ready.
