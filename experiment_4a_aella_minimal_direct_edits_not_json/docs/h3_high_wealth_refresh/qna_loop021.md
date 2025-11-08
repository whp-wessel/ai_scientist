# RFP Q&A Log — High-Wealth Refresh (Loop 021)

*Status:* Open for submissions through 2025-11-15. Entries below capture every vendor question and official response so procurement reviewers can trace timelines and commitments.

## Loop 024 Entries — 2025-11-09
1. **2025-11-09 10:12 UTC — Orion Fieldworks (Singapore)**  
   - *Question:* Can previously fielded affluent-city PSUs (e.g., Singapore + Hong Kong) count toward the ≥30 independent PSUs if the vendor guarantees no respondent overlap with GFS Wave 4?  
   - *Response (10:32 UTC):* Existing PSUs may count **only** if the vendor assigns new PSU IDs that combine city × panel source and certifies (a) zero overlap with Wave 4 PSUs, (b) refreshed recruitment lists post-2024, and (c) independent replicate-weight generation. Appendix B of the RFP now cites `docs/h3_country_expansion_materials/LOI_Singapore_2025-11-09.md` as the template for PSU documentation.
2. **2025-11-09 10:40 UTC — NorthBridge Insights (UAE/UK)**  
   - *Question:* Is it acceptable to deliver 32 BRR replicates plus 32 Fay replicates instead of the requested 64 BRR columns?  
   - *Response (11:05 UTC):* No. The refresh must deliver **64 BRR replicate weights** (ρ = 0.5) to maintain parity with the balanced sample. Fay replicates are welcome as a supplement, but they cannot replace the BRR columns. Updated FAQ now references `docs/h3_replicate_weights_manifest/manifest_loop021.md` so vendors understand how the files will be audited.

## Loop 025 Entries — 2025-11-10
3. **2025-11-10 08:18 UTC — Atlas Sampling Consortium (Switzerland/Luxembourg)**  
   - *Question:* May high-net-worth respondents upload private-banking attestation letters and complete a recorded video verification instead of attending in-person sessions for screener validation?  
   - *Response (08:42 UTC):* Yes, provided each respondent submits (a) a banker-signed asset letter dated ≤30 days before interview, (b) a recorded verification call that captures the respondent’s ID and banker letter, and (c) encryption/transcript logs retained for 36 months. Section 3.4 of `docs/h3_high_wealth_refresh/rfp_2025-11-09.md` now cites this remote workflow and links to the archival checklist in `docs/h3_high_wealth_refresh/compliance_appendix_loop025.md`.
4. **2025-11-10 11:42 UTC — Lumina Field Partners (Canada/Australia)**  
   - *Question:* If we deliver hashed PSU identifiers for each city × recruiter combination, can we delay delivering the underlying lookup table until after award to protect vendor relationships?  
   - *Response (12:03 UTC):* No. The PSU lookup table (city, recruiter, sampling list) must arrive **with** the 64-column BRR matrix so the Methods team can validate non-overlap before award. We added a line to Appendix C referencing `docs/h3_country_expansion_materials/loi_register.csv` and clarified that hashed PSUs without a lookup table will be marked non-responsive.

## Loop 026 Entries — 2025-11-10
5. **2025-11-10 13:58 UTC — Meridian Luxe Panels (Monaco/France)**  
   - *Question:* Can we shorten the required retention window for banker letters and verification recordings to 12 months if local privacy law limits video storage?  
   - *Response (14:15 UTC):* No. Section 3.4 of `docs/h3_high_wealth_refresh/rfp_2025-11-09.md` now clarifies that all vendors must retain banker letters, encryption logs, and verification recordings for **36 months** regardless of jurisdiction, with optional vaulting via the GFS secure archive if domestic limits apply. The compliance appendix (`docs/h3_high_wealth_refresh/compliance_appendix_loop025.md`) was updated to include the cross-border storage waiver language vendors can attach to their submissions.
6. **2025-11-10 15:02 UTC — TerraQuant Research (Brazil/Argentina)**  
   - *Question:* Our internal infrastructure generates 32 BRR replicates per PSU. May we submit two independent 32-column matrices (even/odd replicates) instead of a single 64-column file?  
   - *Response (15:27 UTC):* No. Section 4.2 of the RFP now states that the delivery must be a **single 64-column BRR matrix** with Fay factor ρ = 0.5, column names `brr_01`–`brr_64`, and the PSU lookup table co-delivered. Vendors may supplement with Fay replicates, but splitting the BRR matrix across files or deliveries will be marked non-compliant because the ingestion script (`scripts/loop021_h3_weighted_checks.py`) assumes one contiguous parquet.

## Loop 027 Entries — 2025-11-11
7. **2025-11-11 09:32 UTC — Empiria Luxe Sampling (Italy/Spain)**  
   - *Question:* To keep Monaco fieldwork feasible, may we treat Monaco respondents as part of the Paris PSU and simply flag them in the sample log instead of counting Monaco as an additional PSU toward the ≥30-city requirement?  
   - *Response (09:54 UTC):* No. Section 2.1 of `docs/h3_high_wealth_refresh/rfp_2025-11-09.md` requires **non-overlapping PSU IDs defined as city × vendor**. Monaco must appear as its own PSU in both the PSU lookup table and the 64-column BRR file. We updated Appendix C to reference `docs/h3_country_expansion_materials/loi_register.csv`, which shows how newly countersigned LOIs (e.g., Switzerland, Singapore, China) enumerate each PSU so vendors can mirror the format.
8. **2025-11-11 12:47 UTC — JadeVista Social Metrics (China)**  
   - *Question:* After we countersign the China LOI, can we store the banker-letter/video archives on our Shanghai data center through 2026 and transfer them to GFS only if regulators block the retention window?  
   - *Response (13:05 UTC):* Yes, provided you execute the cross-border storage waiver in `docs/h3_high_wealth_refresh/compliance_appendix_loop025.md` and deliver the encrypted vault to `sftp://secure-gfs/replicates/loop021/` within 30 days of any domestic retention limit. The waiver text has been appended to `docs/h3_country_expansion_materials/LOI_China_2025-11-09.md` so your legal team can reference the clause directly. Remember that verification hashes must also be logged in `docs/h3_high_wealth_refresh/verification_register.csv` at the time of transfer.

## Loop 028 Entries — 2025-11-12
9. **2025-11-12 08:05 UTC — Empiria Luxe Sampling (Italy/Monaco)**  
   - *Question:* We plan to cover Italy and Spain via a single DocuSign envelope; can Monaco respondents remain inside the Paris PSU we already run for the balanced sample, or do you require separate LOIs/PSU IDs for each geography?  
   - *Response (08:37 UTC):* Each country needs its own LOI and DocuSign envelope so Partnerships can audit deliverables country by country. Monaco must retain a standalone PSU ID (`city × recruiter`) even if the fieldwork hub is in Paris. We logged the Italy LOI (`docs/h3_country_expansion_materials/LOI_Italy_2025-11-12.md`, envelope **b19f-7c**) and will expect a distinct Spain LOI/envelope before award. The LOI register (`docs/h3_country_expansion_materials/loi_register.csv`) demonstrates how we track these signatures.
10. **2025-11-12 14:22 UTC — Aurora Nordisk Field Labs (Norway/Iceland)**  
    - *Question:* Can we submit a hashed verification ledger instead of raw banker-letter filenames? Also, where should we log the DocuSign envelope ID once our LOIs are countersigned?  
    - *Response (14:45 UTC):* Hash-only ledgers are acceptable, but you must populate `docs/h3_high_wealth_refresh/verification_register.csv` with one row per respondent that includes the SHA-256 hash, PSU ID, verification timestamp, and vault location. Append the DocuSign envelope ID and signature timestamp to both the LOI PDF and the register so reviewers can trace compliance. Section 2 of the RFP now references this requirement explicitly.

## Loop 029 Entries — 2025-11-12
11. **2025-11-12 18:07 UTC — IberBarna Field Labs (Spain/Portugal)**  
    - *Question:* Now that Spain has a signed LOI, may we reuse the Italy DocuSign envelope for Canary Islands respondents to avoid reconfiguring our legal template?  
    - *Response (18:25 UTC):* No. Each country must retain its own DocuSign envelope and annex so Procurement can audit obligations per jurisdiction. `docs/h3_country_expansion_materials/LOI_Spain_2025-11-12.md` and the LOI register now list envelope **c47a-91**, and any Canary Islands PSU addition must ship a dedicated annex referencing that envelope ID. Section 2.1 of `docs/h3_high_wealth_refresh/rfp_2025-11-09.md` has been updated to reiterate the per-country envelope rule and cites the Spain LOI as the template.
12. **2025-11-12 19:22 UTC — Aurora Nordisk Field Labs (Norway/Iceland)**  
    - *Question:* We uploaded a batch SHA-256 ledger covering 22 Norwegian/Icelandic verification videos. Is it acceptable to log the batch as a single row in the verification register if we include the DocuSign envelope ID and per-PSU metadata?  
    - *Response (19:40 UTC):* Yes, batch logging is acceptable so long as each row lists the PSU(s) covered, the DocuSign envelope, the hash algorithm, and a pointer to the encrypted vault location. We recorded entry `vr_2025-11-12_aurora_batch01` in `docs/h3_high_wealth_refresh/verification_register.csv`, which references DocuSign envelope **d5ab-03** from `docs/h3_country_expansion_materials/LOI_Norway_2025-11-12.md`. Future batches must follow the same format within 48 hours of each upload.

## Loop 030 Entries — 2025-11-13
13. **2025-11-13 09:10 UTC — BarnaLux Insights (Spain/Canary Islands)**  
    - *Question:* Can the Canary Islands PSU share the Madrid BRR replicate columns if we commit to a separate verification hash log, or do we need standalone PSU IDs and DocuSign annexes before launching those interviews?  
    - *Response (09:32 UTC):* Each Canary Islands PSU must retain its own `city × recruiter` code plus a DocuSign annex tied to envelope **c47a-91**. We appended Annex D to `docs/h3_country_expansion_materials/LOI_Spain_2025-11-12.md` and updated `docs/h3_country_expansion_materials/loi_register.csv` to show the Canary PSU carve-out with its submission timestamp. Verification hashes from those respondents must be logged row-by-row in `docs/h3_high_wealth_refresh/verification_register.csv` within 48 hours, pointing to the SFTP vault path that now houses the `barna_canary_batch01.zip` ledger.
14. **2025-11-13 12:26 UTC — Nordic Trust Panels AS (Norway/Iceland)**  
    - *Question:* Our Reykjavik verification team needs to drip SHA-256 ledgers in 10-respondent batches due to data-export limits. Is it compliant if we log each batch with a single hash so long as the PSU IDs, DocuSign envelope, and vault path cover the Reykjavik subset explicitly?  
    - *Response (12:44 UTC):* Yes, provided every batch entry references the Reykjavik PSU IDs, envelope **d5ab-03**, and the encrypted vault path. We documented this in `docs/h3_country_expansion_materials/LOI_Norway_2025-11-12.md` (Loop 030 addendum) and inserted register row `vr_2025-11-13_nordic_batch02` in `docs/h3_high_wealth_refresh/verification_register.csv`. Future Reykjavik uploads must continue this batch logging within 48 hours of each transfer.
