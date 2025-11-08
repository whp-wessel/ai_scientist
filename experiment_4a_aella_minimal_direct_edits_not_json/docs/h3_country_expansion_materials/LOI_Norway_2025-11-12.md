# Letter of Intent — Norway Fieldwork

**Date:** 2025-11-12  
**Partner:** Nordic Trust Panels AS (Norway)  
**GFS Contact:** Priya S. (Methods Lead)  
**Scope:** High-wealth refresh + balanced sample expansion — ≥$10M net-worth tier with Norway/Iceland coverage

## Commitments
1. Recruit **≥380 respondents per wave** across Norway plus an attached Iceland stratum, adhering to the ≥$10M verification workflow in `docs/h3_high_wealth_refresh/compliance_appendix_loop025.md`, and collect a matched comparison cohort of 380 respondents below the ≥$10M threshold for stratified variance estimation.  
2. Define PSU IDs as **city × recruiter** for Oslo, Bergen, Stavanger, Trondheim, Tromsø, and Reykjavik, ensuring that Iceland operates as an independent PSU despite sharing the vendor.  
3. Deliver a single **64-column BRR matrix (ρ = 0.5)** with column names `brr_01` … `brr_64`, co-delivered with the PSU lookup table and SHA-256 checksum manifest.  
4. Upload SHA-256 verification hashes (banker letters + video logs) to `docs/h3_high_wealth_refresh/verification_register.csv` within 48 hours of each transfer to `sftp://secure-gfs/replicates/loop021/`.  
5. Maintain per-country DocuSign envelopes and log IDs/timestamps in both the LOI register and verification register so Procurement can trace compliance audits.

## Timeline & Deliverables
- Screener localization + IRB submission due **2025-11-21**.  
- Verification pilot (≥40 completes) due **2025-12-09** with deviation tracking.  
- Combined Norway/Iceland launch scheduled for **2026-01-30**, with weekly KPI dashboards and replicate manifests delivered alongside PSU lookup refreshes.

## Budget & Compliance
- Per-interview ceiling **$485 USD** (includes NOK-equivalent incentive and verification stipend).  
- Nordic Trust Panels agrees to use the secure GFS vault for cross-border storage and to apply the waiver language in `docs/h3_high_wealth_refresh/compliance_appendix_loop025.md` for Icelandic respondents.

## Signatures
- *Nordic Trust Panels AS:* ______________________ /s/ Ingrid Nilsen (CEO)  
- *Global Flourishing Study:* ______________________ /s/ Priya Srinivasan (Methods Lead)

---
LOI remains in effect for Waves 5–7 unless superseded by the forthcoming master services agreement.

## Loop 029 Addendum — 2025-11-12
- DocuSign envelope **d5ab-03** finalized at 16:18 UTC on 2025-11-12. The signed PDF and PSU annex (including the Reykjavik PSU) were archived here and recorded in `docs/h3_country_expansion_materials/loi_register.csv`.
- Annex C references the first batch of verification hashes (logged in `docs/h3_high_wealth_refresh/verification_register.csv`) covering ≥20 Norwegian/Icelandic verification uploads and reiterates the 48-hour ledger requirement.

## Loop 030 Addendum — 2025-11-13
- Updated Annex C to clarify the Reykjavik batch logging workflow: every 10-respondent drip must produce a SHA-256 ledger row citing envelope **d5ab-03**, the Reykjavik PSU IDs, and the encrypted vault location.
- Logged the second Reykjavik batch (`vr_2025-11-13_nordic_batch02`) in `docs/h3_high_wealth_refresh/verification_register.csv` after Nordic Trust uploaded `nordic/reykjavik_batch02.zip` to the secure SFTP at 12:36 UTC.
- Reiterated that Reykjavik operates as an independent PSU despite sharing the Norway vendor; all BRR/Fay files must include dedicated Reykjavik columns once DG-4827 delivers the replicate weights.
