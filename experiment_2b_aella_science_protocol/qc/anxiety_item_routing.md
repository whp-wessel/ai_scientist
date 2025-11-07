# Anxiety Item Coding & Routing Review
Generated: 2025-11-04T08:48:25.300856+00:00 | Seed: 20251016

## Reproduction
```bash
python analysis/code/review_anxiety_instrument.py \
    --dataset data/raw/childhoodbalancedpublic_original.csv \
    --config config/agent_config.yaml \
    --codebook docs/codebook.json \
    --out-table tables/diagnostics/anxiety_item_review.csv \
    --out-md qc/anxiety_item_routing.md
```

## Coding Summary
- Instrument-coded column: `I tend to suffer from anxiety (npvfh98)-neg` (ID `npvfh98`)
- Scale span: -3 to 3 on a centred 7-point agreement scale
- Value labels:
  - -3: Strongly disagree
  - -2: Disagree
  - -1: Somewhat disagree
  - 0: Neutral
  - 1: Somewhat agree
  - 2: Agree
  - 3: Strongly agree
- Mean agreement: -0.827 (SD 2.031); coverage 99.96% (missing <10)

## Routing Assessment
- No routing/skip-tracking columns containing the instrument code were found.
- Missingness is below the disclosure threshold; observed nonresponse aligns with other mental-health battery items, suggesting refusals rather than programmed skips.

## Alias Checks
- `I tend to suffer from anxiety -neg` matches the instrument-coded column: True

## Outputs
- Summary table: `tables/diagnostics/anxiety_item_review.csv` (suppresses counts below 10)
- Codebook reference: `docs/codebook.json` entry for `I tend to suffer from anxiety (npvfh98)-neg`
