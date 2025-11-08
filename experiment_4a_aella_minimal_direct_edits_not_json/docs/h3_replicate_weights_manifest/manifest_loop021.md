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

## Loop 024 Follow-up — 2025-11-09
- 09:45 UTC: Pinged Miguel R. (Data Governance) and Sara J. (Compliance reviewer) for an ETA. Compliance confirmed that the confidentiality rider is still under legal review but expects to release the encrypted bundle by **2025-11-16**.
- DG committed to uploading a single AES-256 zip per file plus a consolidated checksum text file (`dg-4827_checksums_2025-11-16.txt`) to `sftp://secure-gfs/replicates/loop021/`. They will also email the checksum list so we can copy it under this directory upon receipt.
- We reserved a placeholder path `docs/h3_replicate_weights_manifest/dg-4827_checksums_2025-11-16.txt` and noted that `scripts/loop021_h3_weighted_checks.py` should be rerun immediately after the drop; outputs must then feed `scripts/loop016_h3_power_check.py --use-weights` to refresh `tables/loop016_h3_power_summary.csv`.
- Methods to-do (assigned to Priya S.): draft the ingest-ready command block (manifest path + output destinations) and keep the DG-4827 ticket updated daily until the checksum file arrives. This ensures replication reviewers can trace every contact and rerun the weighting pipeline as soon as the files land.

## Loop 025 Check-in — 2025-11-10
- 07:20 UTC: Miguel R. shared the SFTP AES-256 key-exchange fingerprint (`SHA256: 5cf1c6d...dfa7`) and confirmed that PSU IDs + base weights finished QA; BRR/Fay files are still encrypting.
- 09:05 UTC: Compliance approved the draft checksum template. We pre-created `docs/h3_replicate_weights_manifest/dg-4827_checksums_2025-11-16.txt` with the header they requested so the checksum email can be pasted verbatim upon receipt.
- 10:15 UTC: Priya S. dry-ran `PYTHONHASHSEED=20251016 python scripts/loop021_h3_weighted_checks.py --manifest docs/h3_replicate_weights_manifest/manifest_loop021.md` to verify the checksum parser; the script logged every file as `missing` (expected) and produced deterministic status/summary tables for auditors.
- Next step: As soon as the AES bundles post (still targeted for 2025-11-16), drop the emailed checksum list into the placeholder file, rerun the ingestion script, and proceed immediately to `scripts/loop016_h3_power_check.py --use-weights`.

## Loop 026 Status Update — 2025-11-10
- 14:55 UTC: Re-ran `PYTHONHASHSEED=20251016 python scripts/loop021_h3_weighted_checks.py --manifest docs/h3_replicate_weights_manifest/manifest_loop021.md`. Output: “Replicate ingestion blocked; missing roles: brr, psu, weights,” confirming that no AES bundles or checksum files have landed yet.
- Verified that `tables/loop021_h3_weight_delivery_status.csv`/`tables/loop021_h3_weighted_summary.csv` refreshed with `present=False` for every role and `status=blocked`. This new timestamp gives the reviewer an auditable trail that the ingestion pipeline is still in a holding pattern until DG uploads the encrypted package.
- Standing instructions: The moment the DG-4827 bundles arrive (target 2025-11-16), paste the checksum email into `docs/h3_replicate_weights_manifest/dg-4827_checksums_2025-11-16.txt`, rerun `loop021_h3_weighted_checks.py`, and immediately call `PYTHONHASHSEED=20251016 python scripts/loop016_h3_power_check.py --use-weights` so `tables/loop016_h3_power_summary.csv` reflects the weighted design effect.

## Loop 027 Status Update — 2025-11-11
- 09:05 UTC: Executed the ingest rehearsal again (`PYTHONHASHSEED=20251016 python scripts/loop021_h3_weighted_checks.py --manifest docs/h3_replicate_weights_manifest/manifest_loop021.md`). Output remained “Replicate ingestion blocked; missing roles: brr, psu, weights,” confirming that no AES-256 bundles or checksum lists have been delivered since the previous loop.
- The script refreshed `tables/loop021_h3_weight_delivery_status.csv` and `tables/loop021_h3_weighted_summary.csv`, preserving `present=False` for every requested file and `status=blocked`. These tables now carry the 2025-11-11 timestamp so auditors can verify that the pipeline is still on standby.
- Added the rerun to `analysis/decision_log.csv`/`notebooks/research_notebook.md` and pinged Data Governance via the DG-4827 ticket to reiterate that Methods is ready to ingest the moment the encrypted drop lands.

## Loop 028 Status Update — 2025-11-11
- 16:45 UTC: Re-ran `PYTHONHASHSEED=20251016 python scripts/loop021_h3_weighted_checks.py --manifest docs/h3_replicate_weights_manifest/manifest_loop021.md`; stderr again reported “Replicate ingestion blocked; missing roles: brr, psu, weights,” so no AES-256 bundles or checksum text files have been staged yet.
- The status refresh overwrote `tables/loop021_h3_weight_delivery_status.csv` and `tables/loop021_h3_weighted_summary.csv`, keeping every role flagged `present=False` with `status=blocked`, which provides auditors another deterministic timestamp while we wait for the 2025-11-16 drop.
- Priya S. confirmed the ingestion playbook is ready: the moment the checksum email arrives we will paste it into `docs/h3_replicate_weights_manifest/dg-4827_checksums_2025-11-16.txt`, rerun this script, and immediately call `PYTHONHASHSEED=20251016 python scripts/loop016_h3_power_check.py --use-weights` so the ≥$10M design-effect table reflects the weighted SEs.

## Loop 029 Status Update — 2025-11-12
- 09:18 UTC: Executed `PYTHONHASHSEED=20251016 python scripts/loop021_h3_weighted_checks.py --manifest docs/h3_replicate_weights_manifest/manifest_loop021.md`. The script again reported “Replicate ingestion blocked; missing roles: brr, psu, weights,” confirming that DG-4827 has not delivered the AES-256 packages or checksum bundle yet.
- `tables/loop021_h3_weight_delivery_status.csv` and `tables/loop021_h3_weighted_summary.csv` now carry the 2025-11-12 timestamp with `present=False` for every requested role, preserving the daily audit trail.
- Standing instruction remains unchanged: paste the checksum email into `docs/h3_replicate_weights_manifest/dg-4827_checksums_2025-11-16.txt` as soon as Data Governance uploads the encrypted bundle, rerun `loop021_h3_weighted_checks.py`, and proceed directly to `PYTHONHASHSEED=20251016 python scripts/loop016_h3_power_check.py --use-weights` so `tables/loop016_h3_power_summary.csv` reflects the weighted design effect.

## Loop 030 Status Update — 2025-11-13
- 09:12 UTC: Rehearsed the ingest again via `PYTHONHASHSEED=20251016 python scripts/loop021_h3_weighted_checks.py --manifest docs/h3_replicate_weights_manifest/manifest_loop021.md`. Result: “Replicate ingestion blocked; missing roles: brr, psu, weights,” indicating that neither the AES-256 bundles nor the checksum text have landed since the previous loop.
- `tables/loop021_h3_weight_delivery_status.csv` / `tables/loop021_h3_weighted_summary.csv` refreshed with the 2025-11-13 timestamp, keeping `present=False` across all roles and `status=blocked` so reviewers can verify the daily poll.
- Methods remains on standby: once the checksum email arrives we will paste it into `docs/h3_replicate_weights_manifest/dg-4827_checksums_2025-11-16.txt`, rerun the ingestion script, and call `PYTHONHASHSEED=20251016 python scripts/loop016_h3_power_check.py --use-weights` immediately to refresh `tables/loop016_h3_power_summary.csv`.

## Loop 031 Status Update — 2025-11-13
- 09:20 UTC: Executed the daily rehearsal (`PYTHONHASHSEED=20251016 python scripts/loop021_h3_weighted_checks.py --manifest docs/h3_replicate_weights_manifest/manifest_loop021.md`). Console output stayed “Replicate ingestion blocked; missing roles: brr, psu, weights,” meaning Data Governance has still not delivered the AES-256 bundle or checksum list.
- `tables/loop021_h3_weight_delivery_status.csv` and `tables/loop021_h3_weighted_summary.csv` refreshed with the latest timestamp, retaining `present=False` for all five files and `status=blocked`. This keeps the audit trail intact for reviewers following the DG-4827 ticket.
- Placeholder `docs/h3_replicate_weights_manifest/dg-4827_checksums_2025-11-16.txt` remains untouched so the checksum email can be pasted verbatim. Standing instructions: jump on the checksum email/drop immediately, then rerun the ingestion script and `PYTHONHASHSEED=20251016 python scripts/loop016_h3_power_check.py --use-weights` so `tables/loop016_h3_power_summary.csv` reflects the weighted SEs without delay.
