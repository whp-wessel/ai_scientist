# Sponsor Brief: Survey Design Metadata

- Generated: 2025-11-03T20:13:09+00:00
- Seed: 20251016
- Dataset: `childhoodbalancedpublic_original.csv`

## Current Assumptions
Treat as simple random sample until sponsor provides design metadata. Notes: 2025-01-17: python scripts/design_scan.py (see qc/design_validation.md) found no survey weight or replicate columns.; Variance estimation defaults to Taylor linearization with equal weights.; Revisit once codebook metadata or sponsor indicates design weights/strata.; 2025-11-03: Re-ran scripts/design_scan.py (qc/design_metadata_monitor.md); still no sponsor design metadata or calibrated weights.

## Metadata Gaps
- Calibrated base weight column: missing
- Stratum identifier: missing
- Primary sampling unit identifier: missing
- Replicate weights: missing
- Finite population correction: missing

## Requested Sponsor Deliverables
- Calibrated individual weight file or integrated weight column metadata.
- Stratum definitions and primary sampling unit (PSU) identifiers.
- Replicate weight specification (e.g., BRR, JK1/JK2) with scaling factors.
- Weighting and variance estimation methodology documentation.
- Any finite population correction values or universe totals used in calibration.

## Audit Trail
- Initial validation: 2025-01-17
- Latest monitoring pass: 2025-11-03

## Reproducibility
To regenerate this brief, run:
```bash
python scripts/generate_design_brief.py --out reports/design_metadata_brief.md
```

This script is deterministic and relies on the metadata files referenced above.