# Compliance Appendix — High-Wealth Refresh (Loop 025)

## Remote Identity & Net-Worth Verification
1. **Bank letter requirement**: Every remote respondent must upload a PDF letter on financial-institution letterhead confirming ≥$10M liquid net worth. Letters must be signed within 30 days of interview and cite the private-banking officer’s contact information. Copies are stored under `outputs/high_wealth_refresh/proof_docs/` with AES-256 encryption.
2. **Recorded verification call**: Vendors schedule a live video call (preferred platforms: Teams or Zoom Gov) attended by the enumerator and the respondent. Enumerators must (a) capture the respondent showing a government ID, (b) read the PSU ID aloud, and (c) confirm the banker letter reference ID. Recordings are exported to MP4, hashed with SHA-256, and logged in `docs/h3_high_wealth_refresh/verification_register.csv`.
3. **Data retention**: Video files, banker letters, and chat transcripts are retained for 36 months and then purged. Vendors must furnish deletion attestations referencing the SHA-256 hash list.
4. **Cross-border storage waiver**: If domestic privacy law forbids vendors from storing encrypted videos beyond 12 months, they must (a) transfer the AES-256 archive to the GFS secure vault within 30 days of the local deadline and (b) attach the waiver text below to their submission so GFS assumes the remaining retention window. Sample clause: *“Vendor authorizes Global Flourishing Study to retain the banker-letter and verification archives for 36 months on Vendor’s behalf, consistent with Annex D of RFP 2025-11-09, notwithstanding domestic storage caps.”*

## Documentation Hooks
- Appendix 3.4 of `docs/h3_high_wealth_refresh/rfp_2025-11-09.md` cites this workflow so bidders know which forms of evidence qualify as “verified high net worth.”
- The procurement inbox auto-responds with the hash template to ensure every vendor submits the required logs even during the Q&A window.
- Any deviation (e.g., missing video, unsigned banker letter) must be recorded in the deviation register and reported in the weekly compliance summary distributed to Partnerships and Methods.
