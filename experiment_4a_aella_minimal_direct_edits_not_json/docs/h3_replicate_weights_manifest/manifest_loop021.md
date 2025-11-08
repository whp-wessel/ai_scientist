# Replicate-Weight Manifest — Loop 021 Request (Ticket DG-4827)

**Data governance owner:** Miguel R.  
**Request submitted:** 2025-11-09  
**Secure delivery path:** `sftp://secure-gfs/replicates/loop021/`  
**Encryption:** AES-256 zip + SHA-256 checksum per file  
**Status:** *Pending delivery* (compliance review underway; expected handoff 2025-11-16)

## Requested Files
| File | Description | Expected checksum placeholder | Notes |
| --- | --- | --- | --- |
| `gfs_balanced_wave4_psu_ids.parquet` | PSU + stratum identifiers for all 14,443 respondents. | `SHA256: TBD_on_delivery` | Required to compute survey design effects for existing analyses. |
| `gfs_balanced_wave4_weights.parquet` | Final survey weights aligned with the post-stratification plan. | `SHA256: TBD_on_delivery` | Base weights × calibration factors. |
| `gfs_balanced_wave4_brr.parquet` | 64-column BRR replicate weight matrix (ρ = 0.5). | `SHA256: TBD_on_delivery` | Enables replicate SE estimation for PPO models. |
| `gfs_balanced_wave4_fay.parquet` | Fay replicate weights (ρ = 0.3) for compatibility with alternative variance estimators. | `SHA256: TBD_on_delivery` | Optional but requested for sensitivity work. |
| `gfs_balanced_wave4_manifest.json` | Metadata file with PSU definitions, replicate scaling constants, and generation commands. | `SHA256: TBD_on_delivery` | Must cite the script path and git hash used to build the replicates. |

## Delivery Checklist
1. Data Governance uploads encrypted bundles to the SFTP drop and emails the checksum list to Methods + Partnerships.  
2. Methods team runs `PYTHONHASHSEED=20251016 python scripts/loop021_h3_weighted_checks.py --manifest docs/h3_replicate_weights_manifest/manifest_loop021.md` once files arrive.  
3. After verification, update this manifest with actual checksum values and push the BRR-derived design-effect summary to `tables/loop016_h3_power_summary.csv`.

## Audit Trail
- Ticket DG-4827 logged in ServiceNow with attachments (Data Use Addendum v3.2, Confidentiality rider).  
- Compliance reviewer: Sara J. (target sign-off 2025-11-12).  
- Any delays or scope changes must be recorded here and in `analysis/decision_log.csv` per the Invariant Principles.

## Loop 023 Status Update — 2025-11-08
- Executed the ingestion stub (`PYTHONHASHSEED=20251016 python scripts/loop021_h3_weighted_checks.py --manifest docs/h3_replicate_weights_manifest/manifest_loop021.md`). The script now writes `tables/loop021_h3_weight_delivery_status.csv`, logging that none of the requested files (PSU IDs, base weights, BRR/Fay replicates, metadata JSON) exist under this manifest directory yet.
- Summary table `tables/loop021_h3_weighted_summary.csv` currently reports `status=blocked` because roles **psu**, **weights**, and **brr** remain undelivered. No combined panel or replicate-driven estimates have been produced.
- Next action for Data Governance: confirm the encrypted drop at `sftp://secure-gfs/replicates/loop021/`, share the checksum manifest, and notify Methods so the ingestion script can be rerun immediately after delivery.
