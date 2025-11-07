# Sensitivity Strategy: Missing Survey Weights and Replicate Designs

- Generated: 2025-11-04T08:24:44Z
- Seed: 20251016 (from `config/agent_config.yaml`)
- Dataset: `childhoodbalancedpublic_original.csv`

## Reproducibility
Regenerate this plan with:
```bash
python scripts/generate_sensitivity_plan.py --config config/agent_config.yaml --design docs/survey_design.yaml --dataset childhoodbalancedpublic_original.csv --out analysis/sensitivity_plan.md --timestamp 2025-11-04T08:24:44Z
```
The script is deterministic aside from the timestamp, which is fixed via `--timestamp`.

## Purpose and Scope
Document how ongoing analyses will quantify uncertainty introduced by missing survey weights, strata, PSUs, and replicate designs. All follow-up steps must retain deterministic execution under the shared seed and respect the privacy guardrail (suppress estimates where contributing cell counts fall below 10).

## Current Design Constraints
- Assumption: Treat as simple random sample until sponsor provides design metadata.
- Notes: 2025-01-17: python scripts/design_scan.py (see qc/design_validation.md) found no survey weight or replicate columns.; Variance estimation defaults to Taylor linearization with equal weights.; Revisit once codebook metadata or sponsor indicates design weights/strata.; 2025-11-03: Re-ran scripts/design_scan.py (qc/design_metadata_monitor.md); still no sponsor design metadata or calibrated weights.
- Metadata status:
  - Calibrated weight column: missing
  - Stratum identifier: missing
  - Primary sampling unit identifier: missing
  - Replicate weights: missing
  - Finite population correction: missing

## Proposed Sensitivity Scenarios
### Scenario 0: Baseline SRS Benchmark
- Maintain current simple random sampling assumption as the comparison anchor.
- Archive existing H1/H2 outputs and manifests to support contrasts once weights arrive.
- Deliverable: updated manifest documenting baseline metrics (already complete via prior loops).

### Scenario 1: Proxy Weight Calibration
- Construct pseudo-weights by calibrating to external population margins (age x sex, region) derived from public sources.
- Implementation outline:
  1. Assemble candidate calibration targets (e.g., Census CPS) and document provenance.
  2. Fit raking or generalized regression weighting using deterministic solvers seeded with 20251016.
  3. Re-compute key estimands (H1, H2, forthcoming hypotheses) under pseudo-weights and compare to Scenario 0.
- Privacy: ensure each calibration cell retains at least 10 respondents; otherwise merge categories deterministically.
- Anticipated artifact: `tables/sensitivity_proxy_weights_{hypothesis}.csv` with manifests noting calibration inputs.

### Scenario 2: Variance Inflation via Design Effect Grid
- Emulate plausible design effects by inflating standard errors using fixed multipliers (e.g., 1.2, 1.5, 2.0).
- Implementation outline:
  1. Define a deterministic grid of design effect multipliers informed by literature and sponsor guidance.
  2. Apply multipliers to Scenario 0 standard errors and adjust confidence intervals accordingly.
  3. Record thresholds where inference (e.g., significance at alpha=0.05) changes.
- Anticipated artifact: `tables/sensitivity_design_effect_grid.csv` with multiplier annotations.

### Scenario 3: Replicate Design Imputation
- Approximate replicate variance by generating synthetic strata/PSU structures using stable clustering rules.
- Implementation outline:
  1. Deterministically cluster respondents on geography and demographics to form pseudo-PSUs.
  2. Assign equal-within-cluster weights (or use Scenario 1 weights if available) and build BRR/JK replicates.
  3. Re-estimate focal statistics using survey packages that accept replicate weight matrices.
- Deliverable: manifest recording clustering rules, seed, and replicate counts.

## Implementation Roadmap
- T-013 (new): Curate external margin targets and develop deterministic raking script.
- T-014 (new): Generate design-effect multiplier grid and reporting template.
- T-015 (new): Prototype pseudo-PSU clustering and replicate weight generation.
- Dependencies: completion of Scenario 1 informs Scenario 3 weighting; Scenario 2 can proceed in parallel.

## Quality Assurance and Logging
- Log all commands and seeds in `analysis/decision_log.csv` and relevant manifests.
- Update `artifacts/state.json` with new artifacts and regeneration commands after each scenario.
- Store intermediate calibration inputs under `artifacts/` with deterministic filenames.

## External Coordination
- Continue sponsor outreach for official design files; once provided, rerun baseline scripts with authentic weights and retire proxy scenarios.
- Maintain `reports/design_metadata_brief.md` and `reports/sponsor_follow_up.md` to reflect status changes.