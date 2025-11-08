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
