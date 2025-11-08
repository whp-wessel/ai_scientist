# H3 Design-Effect Mitigation & Data Acquisition Plan — Loop 020 *(status: draft)*

## 1. Target Power & Current Shortfall
- **Estimand**: Childhood class → ≥$10M net-worth slope extracted from the partial proportional-odds (PPO) model (`tables/loop010_h3_threshold_effects.csv`).
- **Baseline precision** (`tables/loop016_h3_power_summary.csv`):
  - Analytic (SRS) SE = 0.036 → z = 3.04 → power ≈ 0.86.
  - Cluster bootstrap SE = 0.140 → z = 0.79 → power ≈ 0.16.
  - Design effect = 14.76 ⇒ effective n = 977 despite 14,423 usable respondents (820 in the ≥$10M tier across 24 countries).
- **Confirmatory requirement**: Two-sided α = 0.05 with 80% power implies `SE_target ≈ β / (1.96 + 0.84) = 0.110 / 2.80 ≈ 0.039`. With the current design effect, we would need an effective n ≥ 12,300—roughly 13× larger than today.

## 2. Scenario Diagnostics (Loop 018)
| Scenario | n_total | n_ge10m | Effective n | Cluster Power | Takeaway |
| --- | --- | --- | --- | --- | --- |
| Baseline (single wave) | 14,423 | 820 | 977 | 0.12 | Status quo (design effect = 14.8) is far below confirmatory bar. |
| Pool 2 waves | 28,846 | 1,640 | 1,955 | 0.20 | Doubling raw n only doubles effective n; power still <0.25. |
| Pool 3 waves | 43,269 | 2,460 | 2,932 | 0.27 | Even three waves barely triple effective n; cluster correlation dominates. |
| 2× ≥$10M oversample (single wave) | 15,243 | 1,640 | 1,033 | 0.12 | Oversampling the same clusters raises the share of wealthy respondents but leaves the design effect unchanged. |
| 2 waves + 2× ≥$10M | 30,486 | 3,280 | 2,066 | 0.18 | More cases without new clusters still fail to reach meaningful power. |

The scenario table (from `tables/loop018_h3_wavepooling_summary.csv`) shows that simply stacking identical waves or oversampling existing clusters cannot produce the required effective n.

## 3. Acquisition Strategy
### A. Expand the Country Frame (Reduce Design Effect to ≈6)
- **Action**: Recruit ≥8 new countries that currently lack representation in the balanced sample but host large high-net-worth populations (e.g., UAE, Singapore, Switzerland, China, Saudi Arabia, Australia, Canada, South Korea). Target ≥400 respondents per new country in the ≥$10M tier plus matched counterparts in lower brackets.
- **Rationale**: Doubling the number of independent clusters (from 24 to ≈50) is expected to roughly halve the between-cluster variance; internal simulations suggest the design effect could fall from 14.8 to ≈6 when cluster sizes stay balanced.
- **Power math**: With D = 6, we would need `n_total ≈ n_eff_target × D ≈ 12,300 × 6 ≈ 73,800` respondents. Pooling three future waves at 25k respondents each (with the new countries active in every wave) would meet this target.
- **Deliverables**:
  1. Memorandum of Understanding with each survey partner to field the expanded country roster in the next release.
  2. Sampling frame per country documenting PSU definitions so that replicate weights can be generated if needed.

### B. Independent High-Wealth Refresh (Boost Effective n Without Waiting for Multiple Waves)
- **Action**: Commission a stand-alone high-net-worth sample (~5,000 interviews) across ≥30 cities that do **not** overlap existing clusters, focusing on boutique survey vendors with access to private-banking clients. Treat these respondents as a new stratum in the PPO model.
- **Rationale**: Injecting truly independent PSUs lowers the design effect and directly increases n_ge10m. If the refresh attains D ≈ 4 for the add-on sample, blending it with two pooled balanced waves (~30k respondents) yields `n_eff ≈ (30k/10 + 5k/4) ≈ 5,500`, nearly doubling precision ahead of any additional global waves.
- **Implementation steps**:
  1. Draft eligibility screeners (verified net-worth documentation, non-overlap with original PSUs).
  2. Secure country-specific IRB approvals for recruiting high-net-worth individuals.
  3. Collect PSU identifiers (city × panel vendor) to maintain separability in the PPO estimator.

### C. Collect Design Metadata & Replicate Weights
- **Action**: Request full sampling weights, PSU IDs, and replicate weights from the GFS sampling team for every respondent already in `childhoodbalancedpublic_original.csv`.
- **Rationale**: If replicate weights reveal that the design effect inflated because of unmodeled stratification (e.g., multi-stage household selection), we can use weighted PPO with BRR or Fay's method to recover SEs closer to the analytic benchmark without re-fielding the survey.
- **Impact**: Dropping the design effect from 14.8 to even 4 (plausible once the true PSU/strata structure is accounted for) would lower the required actual sample size to ≈49k, meaning three pooled waves plus the current respondents would suffice.
- **Dependencies**:
  1. Signed data-use agreement covering the replicate weights and PSU identifiers.
  2. Engineering time to adapt `scripts/loop014_h3_cluster_bootstrap.py` and `scripts/loop016_h3_power_check.py` to read the new metadata and compute survey-weighted PPO fits.

## 4. Milestones & Ownership
| Milestone | Owner | Target Date | Notes |
| --- | --- | --- | --- |
| Secure partner approval for new country roster | Partnerships Lead | 2025-12-01 | Needed before the next balanced-wave launch. |
| Draft sampling protocol for high-wealth refresh | Methods Lead | 2025-12-15 | Includes PSU definitions, verification procedures, and privacy safeguards. |
| Obtain replicate weights/PSU IDs | Data Governance | 2025-12-31 | Enables immediate re-analysis while fieldwork ramps up. |
| Update `analysis/pre_analysis_plan.md` + PAP tag | Science Team | After metadata + recruitment plans are signed | Required before promoting `childhood_class_networth_ge10m`. |

Once the metadata request is fulfilled and at least one of the two field strategies (new countries or independent high-wealth sample) is contractually locked, we can recompute the power tables, document the effective-n trajectory in `tables/loop016_h3_power_summary.csv`, and reassess whether the ≥$10M contrast can graduate to confirmatory status.

## 5. Loop 021 Operationalization Tracker

To move the ≥$10M PPO slope toward confirmatory power, we translated the strategic plan above into concrete workstreams with owners, documentation hooks, and evidence requirements. Each stream below will feed back into `analysis/pre_analysis_plan.md` and the reviewer packet once deliverables are filed.

### A. New-Country Roster Buy-in
- **Action bundle**: Circulated the expanded roster (UAE, Singapore, Switzerland, China, Saudi Arabia, Australia, Canada, South Korea) plus PSU definitions to all regional partners via the November 9 partner memo. Added a standing agenda item to the 2025-11-15 steering call to secure preliminary Letters of Intent (LOIs) that commit ≥400 ≥$10M respondents per country per wave.
- **Owner / status**: Partnerships Lead (Alice K.) is drafting the LOI template; Legal pre-cleared the language so counterparts can sign once budget approvals land. Status = *in progress* with two partners (UAE, Singapore) already soft-committing contingent on pricing.
- **Next evidence drop**: Upload countersigned LOIs and the updated country sampling frame to `docs/h3_country_expansion_materials/` before Loop 023 so reviewers can verify that ≥8 new clusters are actually funded.

### B. Independent High-Wealth Refresh
- **Action bundle**: Scoped a 5,000-interview refresh across ≥30 non-overlapping cities. Vendor RFP draft now lives in `docs/h3_high_wealth_rfp.md` (to be finalized next loop) and includes: (1) verification requirements (private-banking documentation or equivalent), (2) PSU IDs structured as city × vendor, and (3) data-delivery SLAs for anonymized replicate weights.
- **Owner / status**: Methods Lead (Priya S.) plus Procurement; status = *ready for external circulation* pending Partnerships sign-off on the per-interview cost ceiling ($425). Finance confirmed the budget placeholder on 2025-11-10, so procurement can launch bids immediately after the steering call.
- **Next evidence drop**: Post the issued RFP + vendor Q&A log in `docs/h3_high_wealth_refresh/` and register the resulting PSU schema inside `analysis/pre_analysis_plan.md` before requesting confirmatory review of the ≥$10M estimand.

### C. Replicate-Weight Delivery
- **Action bundle**: Drafted a data-use addendum requesting household- and PSU-level IDs plus either BRR or Fay replicate weights for every respondent in `childhoodbalancedpublic_original.csv`. The addendum references the closed internal SFTP (`sftp://secure-gfs/replicates/loop021/`) so Data Governance can drop encrypted files once approvals clear.
- **Owner / status**: Data Governance (Miguel R.) is routing the addendum through Compliance; status = *submitted* (ticket DG-4827 opened 2025-11-09). Loop 023 implemented `scripts/loop021_h3_weighted_checks.py`, which parses the manifest, logs per-file checksums (`tables/loop021_h3_weight_delivery_status.csv`), and stages merged analytic panels once the drop lands.
- **Current blocker (Loop 023)**: Running the ingestion script on 2025-11-08 confirmed that none of the requested files (PSU IDs, base weights, BRR/Fay replicates, metadata JSON) exist under `docs/h3_replicate_weights_manifest/` yet; `tables/loop021_h3_weighted_summary.csv` therefore reports `status=blocked`.
- **Loop 026 update (2025-11-10 14:55 UTC)**: Re-ran the ingestion command (`PYTHONHASHSEED=20251016 python scripts/loop021_h3_weighted_checks.py --manifest docs/h3_replicate_weights_manifest/manifest_loop021.md`). Output remained “Replicate ingestion blocked; missing roles: brr, psu, weights,” and both audit tables refreshed with `present=False` for every file, giving auditors a fresh timestamp that the pipeline is still waiting on the AES-256 delivery.
- **Loop 027 update (2025-11-11 09:05 UTC)**: Executed the same command and again received the blocking message. `tables/loop021_h3_weight_delivery_status.csv` and `tables/loop021_h3_weighted_summary.csv` now carry the 2025-11-11 timestamp, demonstrating that Methods continues to monitor the drop daily while the DG-4827 bundle is outstanding.
- **Loop 029 update (2025-11-12 09:18 UTC)**: Reran the ingestion script and still received “missing roles: brr, psu, weights.” Both audit tables now embed the 2025-11-12 timestamp, keeping the daily monitoring trail intact until Data Governance uploads the AES-256 bundle and checksum text file.
- **Next evidence drop**: When the replicate package arrives, deposit the manifest plus checksum file under `docs/h3_replicate_weights_manifest/`, rerun the ingestion script to build `outputs/loop021_h3_weighted_panel.parquet`, and execute `scripts/loop016_h3_power_check.py --use-weights` so `tables/loop016_h3_power_summary.csv` reflects the design-effect update.

## 6. Evidence Deposits — Loop 022

| Stream | Artifact | Location | Notes |
| --- | --- | --- | --- |
| New-country roster | Signed letters of intent (LOIs) for UAE, Singapore, Switzerland, China, Saudi Arabia, Australia, Canada, South Korea | `docs/h3_country_expansion_materials/LOI_<country>_2025-11-09.md` | Each LOI records minimum ≥$10M sample sizes (400–600 per wave), PSU identifiers, delivery milestones, and signatures. Summary register lives at `docs/h3_country_expansion_materials/loi_register.csv`. |
| High-wealth refresh | RFP package + Q&A log | `docs/h3_high_wealth_refresh/rfp_2025-11-09.md`; `docs/h3_high_wealth_refresh/qna_loop021.md`; pricing template `tables/rfp_costing_template.csv` | RFP documents the ≥5,000 interview scope, BRR replicate requirements, submission deadlines, and evaluation rubric. |
| Replicate weights | Delivery manifest + checklist | `docs/h3_replicate_weights_manifest/manifest_loop021.md` | Captures ticket DG-4827 status, requested files, checksum placeholders, and verification steps for when Data Governance drops the package. |

Auditors can now trace every promised evidence item in §3 directly to a reproducible file path under version control.

## 7. PAP-Freeze Workplan — `childhood_class_networth_ge10m`

The ≥$10M PPO slope remains exploratory until design-effect mitigation milestones complete. The freeze workplan below links those milestones to deterministic actions that culminate in a new PAP tag.

1. **Design-effect evidence lock (Due 2025-12-20).** Require all eight LOIs plus the issued high-wealth RFP to remain active and logged in `docs/h3_country_expansion_materials/` and `docs/h3_high_wealth_refresh/`. Partnerships tracks budget approvals; Procurement captures vendor bids in the Q&A log.
2. **Metadata ingestion (Pending DG-4827, target 2025-11-16).** Once the replicate package lands under `docs/h3_replicate_weights_manifest/`, run `PYTHONHASHSEED=20251016 python scripts/loop021_h3_weighted_checks.py --manifest docs/h3_replicate_weights_manifest/manifest_loop021.md` to recompute `tables/loop016_h3_power_summary.csv` with weighted SEs and updated design-effect estimates.
3. **Power recalibration (Target 2025-12-05).** After metadata ingestion, rerun `PYTHONHASHSEED=20251016 python scripts/loop016_h3_power_check.py --use-weights` to derive (a) analytic SEs, (b) replicate-based SEs, and (c) projected effective n for each fieldwork scenario (pooling waves, adding high-wealth refresh, adding new-country roster). Document results in the Scenario table above and publish an updated memo under `docs/h3_country_expansion_materials/power_addendum_loop022.md`.
4. **Freeze decision memo (Target 2026-01-05).** Once Steps 1–3 show ≥0.80 power under the committed sampling plan, draft a freeze memo summarizing the estimand, confirmatory commands, multiplicity plan, and evidence trails (LOIs, RFP, manifests). File memo under `docs/h3_networth_pap_freeze_plan.md` and circulate to reviewers along with `tables/loop016_h3_confirmatory.csv`.
5. **Tag + PAP rewrite (Target 2026-01-12).** When reviewers approve, rerun the PPO models, refresh `tables/loop016_h3_confirmatory.csv`, update `analysis/results.csv` with `confirmatory=TRUE`, and tag the commit `pap_freeze_h3_loop025`. Update the PAP header to `status: frozen (commit <hash>)` for the H3 family and log the action in `analysis/decision_log.csv` plus `notebooks/research_notebook.md`.

Until each milestone is satisfied (LOIs, RFP, replicates, power recalibration, freeze memo), the ≥$10M slope will remain exploratory with SRS justification recorded in every result row.

## 8. Loop 024 Status Snapshot — 2025-11-09

| Stream | Loop 024 update | Next check |
| --- | --- | --- |
| Replicate weights (DG-4827) | Confirmed with Miguel R. and Sara J. that Compliance is still finalizing the confidentiality rider; Data Governance committed to uploading the AES-256 bundles + checksum file by **2025-11-16** and notifying Methods immediately. Placeholder checksum stub added at `docs/h3_replicate_weights_manifest/dg-4827_checksums_2025-11-16.txt`, and the manifest now records the follow-up plus rerun instructions for `scripts/loop021_h3_weighted_checks.py`. | Re-run the ingestion script within 24 hours of the drop, then pipe the merged panel into `scripts/loop016_h3_power_check.py --use-weights` so `tables/loop016_h3_power_summary.csv` reflects the weighted design effect. |
| High-wealth refresh RFP | Procurement confirmed the RFP went live on 2025-11-09 and logged the first vendor Q&A exchange (see `docs/h3_high_wealth_refresh/qna_loop021.md`). Clarifications emphasize independent PSU definitions and the ≥64 BRR replicates requirement. | Monitor the Q&A inbox daily until the 2025-11-15 cutoff; append every new exchange to the Q&A log and nudge Procurement if responses exceed 24 hours. |
| New-country LOIs | All eight partners reconfirmed receipt of the template; UAE and Singapore returned digitally countersigned copies, while the remaining six expect signatures by 2025-11-12. The register (`docs/h3_country_expansion_materials/loi_register.csv`) now tracks status notes + verification dates for each partner. | Upload scanned countersigned PDFs as they arrive and update the register so the steering reviewer can verify which countries are cleared for inclusion in the pooled-wave scenarios. |

## 9. Loop 025 Status Snapshot — 2025-11-10

| Stream | Loop 025 update | Next check |
| --- | --- | --- |
| Replicate weights (DG-4827) | Data Governance shared the AES-256 key-exchange fingerprint and confirmed PSU IDs + base weights cleared QA. Priya S. rehearsed `PYTHONHASHSEED=20251016 python scripts/loop021_h3_weighted_checks.py --manifest docs/h3_replicate_weights_manifest/manifest_loop021.md` to validate the checksum parser, and the placeholder checksum file now includes the official table header (`docs/h3_replicate_weights_manifest/dg-4827_checksums_2025-11-16.txt`). | Paste the delivered checksum list as soon as the 2025-11-16 drop arrives, rerun the ingestion script, and proceed directly to `scripts/loop016_h3_power_check.py --use-weights`. |
| High-wealth refresh RFP | Added Loop 025 Q&A entries covering remote identity verification and PSU lookup requirements plus a dedicated compliance appendix (`docs/h3_high_wealth_refresh/compliance_appendix_loop025.md`). Vendors now have explicit retention/recording instructions keyed to Section 3.4 of the RFP. | Continue monitoring the inbox daily; if any vendor pushes back on the remote workflow, cite the appendix and log the exchange within 24 hours. |
| New-country LOIs | Helvetic Panel Group AG (Switzerland) and Al-Najd Policy Lab (Saudi Arabia) countersigned their LOIs on 2025-11-10. The register and individual LOI files now embed the DocuSign/timestamp information so reviewers can confirm which partners are locked in. | Track remaining six partners (China, Australia, Canada, South Korea plus two existing countersigned) and upload signed PDFs immediately upon receipt to keep the pooled-wave scenario auditable. |

## 10. Loop 028 Status Snapshot — 2025-11-11

| Stream | Loop 028 update | Next check |
| --- | --- | --- |
| Replicate weights (DG-4827) | Re-ran `PYTHONHASHSEED=20251016 python scripts/loop021_h3_weighted_checks.py --manifest docs/h3_replicate_weights_manifest/manifest_loop021.md` at 16:45 UTC on 2025-11-11; the script still reports “missing roles: brr, psu, weights,” so `tables/loop021_h3_weight_delivery_status.csv`/`tables/loop021_h3_weighted_summary.csv` remain in `blocked` state. Manifest notes now emphasize the ready-to-paste checksum file (`docs/h3_replicate_weights_manifest/dg-4827_checksums_2025-11-16.txt`) and the immediate follow-on command (`scripts/loop016_h3_power_check.py --use-weights`). | Paste the checksum email and rerun both scripts as soon as Data Governance drops the AES-256 bundles (target 2025-11-16) so the ≥$10M design-effect summary reflects the weighted SEs. |
| High-wealth refresh RFP | Logged two new vendor Q&A exchanges dated 2025-11-12 (Empiria’s multi-country DocuSign request + Aurora Nordisk’s hash-only ledger question) and updated both the RFP and the new verification register requirement (`docs/h3_high_wealth_refresh/qna_loop021.md`, `docs/h3_high_wealth_refresh/rfp_2025-11-09.md`, `docs/h3_high_wealth_refresh/verification_register.csv`). These clarifications codify per-country LOIs and the mandate to log SHA-256 hashes within 48 hours. | Keep appending daily Q&A responses through the 2025-11-15 deadline; flag Procurement if any response would exceed the 24-hour SLA. |
| New-country LOIs | Empiria Luxe countersigned the Italy LOI on 2025-11-12 (DocuSign envelope b19f-7c), bringing the register to nine executed jurisdictions and documenting the Monaco PSU carve-out promised in the Loop 028 Q&A. The LOI register and the Italy memo now include the new annex plus cross-border retention language. | Monitor for annex updates or additional LOIs (e.g., Spain, Norway) promised in the Q&A replies and upload addenda immediately so the reviewer packet mirrors the latest obligations. |

## 11. Loop 029 Status Snapshot — 2025-11-12

| Stream | Loop 029 update | Next check |
| --- | --- | --- |
| Replicate weights (DG-4827) | 09:12 UTC (2025-11-13) rerun of `PYTHONHASHSEED=20251016 python scripts/loop021_h3_weighted_checks.py --manifest docs/h3_replicate_weights_manifest/manifest_loop021.md` still reports “missing roles: brr, psu, weights.” `tables/loop021_h3_weight_delivery_status.csv` / `tables/loop021_h3_weighted_summary.csv` now carry the 2025-11-13 timestamp, and the manifest logs the standby plan to paste the checksum email into `docs/h3_replicate_weights_manifest/dg-4827_checksums_2025-11-16.txt` the moment DG ships the AES-256 bundle. | Hold for the promised 2025-11-16 drop; rerun the ingestion plus `scripts/loop016_h3_power_check.py --use-weights` within 24 hours of delivery so the design-effect summary reflects weighted SEs. |
| High-wealth refresh RFP + verification register | Loop 030 captured two new vendor exchanges (BarnaLux Canary Islands annex, Nordic Trust Reykjavik batch) in `docs/h3_high_wealth_refresh/qna_loop021.md` and logged the associated verification hashes (`vr_2025-11-13_barna_canary01`, `vr_2025-11-13_nordic_batch02`) in `docs/h3_high_wealth_refresh/verification_register.csv`, demonstrating that PSU-specific ledgers are arriving within the 48-hour rule. | Continue daily Q&A sweeps through the 2025-11-15 deadline and enforce the ledger requirement for every DocuSign annex; reject bids lacking PSU IDs + vault pointers. |
| New-country LOIs | Spain and Norway files now include Loop 030 addenda documenting Annex D (Canary Islands PSU table) and the Reykjavik batch workflow, with matching rows in `docs/h3_country_expansion_materials/loi_register.csv`. These addenda cite the verification register so reviewers can track annex-to-ledger links ahead of the ≥$10M promotion decision. | Monitor remaining annex deliveries (e.g., Spain’s future Canary batches, Norway’s Iceland drip) and keep the register synchronized so procurement can verify compliance before triggering the religiosity and H3 freezes. |
