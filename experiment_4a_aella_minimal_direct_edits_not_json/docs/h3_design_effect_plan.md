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
- **Owner / status**: Data Governance (Miguel R.) is routing the addendum through Compliance; status = *submitted* (ticket DG-4827 opened 2025-11-09). Engineering already stubbed `scripts/loop021_h3_weighted_checks.py` to ingest BRR replicates once delivered.
- **Next evidence drop**: When the replicate package arrives, deposit the manifest plus checksum file under `docs/h3_replicate_weights_manifest/` and rerun `scripts/loop016_h3_power_check.py` with the weighted SEs to document the updated design effect inside `tables/loop016_h3_power_summary.csv`.
