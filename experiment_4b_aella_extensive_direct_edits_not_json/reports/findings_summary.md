# Findings Summary — Loop 068
**Date:** 2025-11-09
**Seed:** 20251016

## Loop updates
- Re-ran the seeded sensitivity suite so the commands in `analysis/sensitivity_manifest.md` now reference the loop-068 directories and the regenerated pseudo-weight, design-effect, and pseudo-replicate outputs stored under `outputs/sensitivity_pseudo_weights_loop068/`, `outputs/sensitivity_design_effect_grid_loop068.*`, and `outputs/sensitivity_replicates_loop068/sensitivity_replicates_summary.json`.
- Scenario 1 continues to shrink the effective sample from 14,443 (DEFF=1.0) to 11,628.5 (DEFF=1.25) to 9,533.2 (DEFF=1.5) while H1/H2 remain near −0.1201/+0.0998 (SE=0.0354/0.0057) and H3 stays negative (−0.6339 at DEFF=1.25, −0.667 at DEFF=1.5) even as the pseudo-weight CV inflates.
- Scenario 2’s design-effect grid (`outputs/sensitivity_design_effect_grid_loop068.csv/.md`) keeps the targeted family’s 95% CIs on the same side of zero through DEFF=2.0 (e.g., H3 still has [−0.746, −0.563]), preserving the BH q-values because the base estimates did not change.
- Scenario 3’s pseudo-replicate jackknife (`outputs/sensitivity_replicates_loop068/sensitivity_replicates_summary.json`) reports replicate SEs of ≈0.01903 (H1), 0.00203 (H2), and 0.01766 (H3), matching the HC1 bands already published in `analysis/results.csv` and reinforcing the sign stability.
- Logged the Semantic Scholar search for "childhood religiosity adulthood depression protective factors" (saved at `lit/queries/loop_068/query_001.json`), which still returned HTTP 403; captured the CrossRef fallback DOI 10.1093/oso/9780195069853.003.0006 (`lit/queries/loop_068/crossref_query_001.json`), updated `lit/evidence_map.csv`/`lit/bibliography.*`, and flagged Claim C1 so the literature map stays DOI-backed while the API outage persists.
- No new public tables or figures were released this loop, so `qc/disclosure_check_loop_064.md` (violations: 0) remains the latest audit while the writing-phase QC gate (N14) continues to be the looming milestone before review.

## Next actions
1. Execute the writing-phase QC pass: ensure Markdown/LaTeX parity for `papers/main/manuscript.*`, refresh `papers/main/imrad_outline.md`, rerun `qc/strobe_sampl_checklist.md`, revisit `reports/identification.md` with the DAG, rebuild the manuscript (recording the command/outcome in `papers/main/build_log.txt`), and capture the updated status in the next findings log entry.
2. Keep logging Semantic Scholar (or CrossRef fallback) queries every loop so each `[CLAIM:<ID>]` remains tied to ≥1 DOI-backed source; continue persisting response payloads under `lit/queries/loop_<idx>/`, syncing `lit/evidence_map.csv`, and refreshing `lit/bibliography.*` accordingly before advancing.
3. Maintain synchronized documentation: keep `analysis/decision_log.csv`, `notebooks/research_notebook.md`, and this summary aligned with the deterministic commands/output paths so reviewers can trace the route through sensitivity, writing QC, and the pending review gate.
