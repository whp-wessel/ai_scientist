# Manuscript Annotations Summary

## Overview
The `manuscript_annotated.tex` file has been updated with critical scientific and methodological annotations using LaTeX native comment tools:
- `\usepackage[colorinlistoftodos,textsize=footnotesize]{todonotes}` for inline todo notes
- `\usepackage{pdfcomment}` for PDF comments with author/subject tags

## Annotations Added

### 1. **CRITICAL: NC1 Contradiction** (Abstract, Line 17)
**Location:** After the first sentence in abstract  
**Type:** PDF Comment  
**Issue:** Abstract claims NC1 "stays near zero" but Results table reports +0.2388 [0.2209, 0.2568], p≈0.  
**Comment:** "NC1 abstract claim 'stays near zero' contradicts Results table (+0.2388 [0.2209, 0.2568], p≈0). This is a large effect, not near-zero."

---

### 2. **SURVEY DESIGN** (Methods, Line 22)
**Location:** Methods section, after SRS assumption mention  
**Type:** Inline Todo  
**Issue:** If survey_design.yaml defines strata/PSUs/weights, confirmatory estimands must be design-based by default.  
**Comment:** "SURVEY DESIGN: If survey_design.yaml defines strata/PSUs/weights, confirmatory estimands must be design-based by default. Current SRS baseline + ad-hoc sensitivity risks bias. Clarify scope: are results sample-level descriptive or population-level design-adjusted?"

---

### 3. **AMBIGUOUS ESTIMAND** (Results H1, Line 25)
**Location:** H1 / Depression result  
**Type:** PDF Comment  
**Issue:** Ordered logit contrast scale is unclear (latent log-odds? marginal effect? probability difference?).  
**Comment:** "Is −0.120 a latent log-odds parameter? Marginal effect on 5-level score? Probability difference for top category? Without explicit scale definition, uninterpretable. Also missing: Brant test or PO assumption check."

---

### 4. **EFFECT SCALE NOT CONTEXTUALIZED** (Results H3, Line 27)
**Location:** H3 / Self-love result  
**Type:** PDF Comment  
**Issue:** −0.6544 has no contextual scale (range, SD, standardized units).  
**Comment:** "−0.6544 reduction magnitude is meaningless without scale (range, SD). How big is this? Report standardized effect or absolute range to aid interpretation."

---

### 5. **ZERO P/Q VALUES** (Results H3, Line 27)
**Location:** H3 / Self-love result, after the q=0 mention  
**Type:** PDF Comment  
**Issue:** p=0 and q=0 are numerical underflow, not true zeros. Should be reported as p<1e-k, q<1e-k.  
**Comment:** "q=0 is underflow, not a true zero. Report as q<0.0001 or similar. Same for p≈0 in H2 and NC1. These affect downstream BH calculations."

---

### 6. **JACKKNIFE k=6** (Sensitivity, Line 31)
**Location:** Sensitivity section, at k=6 mention  
**Type:** Inline Todo  
**Issue:** Six pseudo-replicates is non-standard; accepted schemes use #replicates ≈ #PSUs or official replicate-weight schemes.  
**Comment:** "JACKKNIFE k=6: Six pseudo-replicates is non-standard. Accepted schemes use #replicates≈#PSUs or official replicate-weight scheme. k=6 appears arbitrary and will draw criticism. Justify or revert to standard bootstrap/BRR."

---

### 7. **NC1 VALIDITY & INTERPRETATION** (Discussion, Line 33)
**Location:** Discussion section, at NC1 conclusion  
**Type:** Inline Todo  
**Issue:** NC1 (sibling count) is not a "clean null" because parental religiosity predicts both exposure and sibling count; hence confounded by design.  
**Comment:** "NC1 VALIDITY & INTERPRETATION: NC1 (sibling count) shows a large effect (+0.2388). This is NOT a 'clean null' because parental religiosity likely predicts both sibling count and the exposure. Sibling count is not independent of parental traits—it is confounded by design. A true null control should be unrelated by causal structure, not just 'not in the BH family.'"

---

### 8. **LITERATURE & ROBUSTNESS** (Discussion, Line 35)
**Location:** Final paragraph, after CLAIM:C* mention  
**Type:** Inline Todo  
**Issue:** Three concerns: (1) [CLAIM:*] assertions lack mechanism integration; (2) CrossRef fallbacks lack primary status; (3) robustness_passed = N but text claims stability.  
**Comment:** "LITERATURE & ROBUSTNESS: (1) [CLAIM:*] tags are asserted but do not integrate mechanisms (resilience as moderator vs mediator?). (2) CrossRef fallbacks should be demoted from primary evidence. (3) In results.csv, robustness_passed = N for H1–H3, yet text claims stability. This is inconsistent and should block celebratory language until prespecified checks pass or are transparently labeled exploratory."

---

## How to Compile to PDF

Use any LaTeX distribution (TeX Live, MacTeX, MikTeX, Overleaf):

```bash
pdflatex manuscript_annotated.tex
```

Or use XeLaTeX/LuaLaTeX:

```bash
xelatex manuscript_annotated.tex
lualatex manuscript_annotated.tex
```

The compiled PDF will display:
- **Inline todos** as colored boxes with the comment text
- **PDF comments** as clickable annotations in the PDF viewer

---

## Key Issues Highlighted

| Issue | Severity | Impact |
|-------|----------|--------|
| NC1 contradiction (near zero vs +0.2388) | CRITICAL | Invalidates falsification logic |
| Survey design not honored | HIGH | Potential bias in estimates |
| Ordered logit estimand undefined | HIGH | Uninterpretable results |
| NC1 not a clean null (confounded) | HIGH | Confounding by parental traits |
| Zero p/q values (underflow) | MEDIUM | Statistical reporting error |
| Effect scale not contextualized (H3) | MEDIUM | Uninterpretable magnitude |
| Robustness flags = N but text claims stability | MEDIUM | Inconsistent messaging |
| Jackknife k=6 non-standard | MEDIUM | Methodological concern |
| CLAIM:* assertions not mechanistic | MEDIUM | Literature integration weak |


