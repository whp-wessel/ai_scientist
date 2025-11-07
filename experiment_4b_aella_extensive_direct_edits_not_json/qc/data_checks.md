# Data Checks — Loop 000 (Bootstrap)

| Check | Status | Details | Command / Evidence |
| --- | --- | --- | --- |
| Raw CSV available | ✅ | `childhoodbalancedpublic_original.csv` found in repo root. | `python - <<'PY' ... print(path.exists())` |
| Row/column counts | ✅ | 14,443 rows × 718 columns (header includes text + coded variables). | `python - <<'PY' ... print('rows', row_count)` |
| Encoding/read errors | ✅ | UTF-8 read via Python `csv` module without decoding issues. | Same command as above |
| Codebook placeholder | ⚠️ | `docs/codebook.json` drafted; requires authoritative metadata. | Manual inspection |
| Survey design info | ⚠️ | `docs/survey_design.yaml` notes missing weights/strata; assume SRS until updated. | Manual inspection |
| Confidentiality guardrail | ✅ | Small-cell threshold set to `k=10` per config/agent_config.yaml. | Config file |

## TODOs
- Replace placeholder codebook notes with the official codebook once available.
- Confirm whether probability weights exist; if referenced but missing, halt work and escalate.
- Add automated schema validation script under `analysis/code/`.
