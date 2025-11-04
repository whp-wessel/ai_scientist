# Findings Report v0.1
Version: 0.1.0 (frozen PAP reference)  
Updated: 2025-11-04T07:58:50Z | Seed: 20251016

> **Parity requirement:** Keep this Markdown report in sync with `papers/main/manuscript.tex`. Any change here must be mirrored in LaTeX during the same commit.

## Abstract
_Placeholder — populate after confirmatory analyses in alignment with frozen PAP._

## Methods
- Data source: `data/raw/childhoodbalancedpublic_original.csv` (SHA-256 logged in `artifacts/checksums.json`).
- Derived dataset: `data/clean/childhoodbalancedpublic_with_csa_indicator.csv` regenerated via  
  `python analysis/code/derive_csa_indicator.py --dataset data/raw/childhoodbalancedpublic_original.csv --out-dataset data/clean/childhoodbalancedpublic_with_csa_indicator.csv --out-distribution tables/csa_indicator_distribution.csv --config config/agent_config.yaml --codebook-in docs/codebook.json --codebook-out docs/codebook.json`.
- Confirmatory scope: HYP-001, HYP-003 (see `analysis/pre_analysis_plan.md`, frozen 2025-11-04T07:58:50Z).
- Statistical plan: HC3 OLS under SRS assumption; Benjamini–Hochberg at q=0.05 within confirmatory family; robustness checks pre-specified in PAP.

## Results
_Pending confirmatory execution. No results reported prior to PAP freeze._

## Robustness and Sensitivity
_To be completed post-confirmatory analysis._

## Limitations
1. Survey provider has not yet confirmed absence of design weights; we proceed under SRS with transparent caveats.
2. CSA exposure indicator derived from composite scores; potential measurement error to be explored in robustness checks.

## Ethics, Privacy, and Disclosure
- Small-cell suppression threshold: n < 10 (per `config/agent_config.yaml`); adhere to rounding/binning in all outputs.
- Data contain sensitive childhood trauma indicators; confirm IRB posture before dissemination.

## Open Questions
1. Should HYP-004 (social support) advance to confirmatory status once routing documentation is secured?
2. How robust are self-reported mental health outcomes to mode effects or temporal framing?

## Reproducibility Notes
- Environment snapshot: `artifacts/session_info.txt`.
- Seed: `artifacts/seed.txt` (20251016).
- Regeneration command for this report: manual edit synchronized with `papers/main/manuscript.tex`. Include command lineage in `papers/main/MANIFEST.md`.
