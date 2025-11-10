# Manuscript Annotations Complete ✅

## Summary
**`manuscript_annotated.tex`** has been successfully updated with **8 critical scientific annotations** using LaTeX native tools.

All annotations are **non-intrusive** and preserve the original text flow while flagging serious methodological issues.

---

## Annotations Embedded (Ready to Compile)

### 1️⃣ **NC1 Contradiction** — CRITICAL
- **Location:** Abstract, line 17
- **Type:** `\pdfcomment` (PDF metadata annotation)
- **Issue:** Abstract claims NC1 "stays near zero" but Results report +0.2388 [0.2209, 0.2568], p≈0
- **Flag:** Large effect ≠ near-zero; signals confounding or invalid negative control

```latex
\pdfcomment[author=Wes,subject={CRITICAL: NC1 Contradiction}]{NC1 abstract claim "stays near zero" contradicts Results table (+0.2388 [0.2209, 0.2568], p≈0). This is a large effect, not near-zero.}
```

---

### 2️⃣ **Survey Design Mismatch** — HIGH PRIORITY
- **Location:** Methods section, line 22
- **Type:** `\todo[inline]` (Colored todo box)
- **Issue:** SRS baseline used despite survey design/strata/PSU definitions in `survey_design.yaml`
- **Flag:** Risks bias; should clarify sample-level vs population-level scope

```latex
\todo[inline]{SURVEY DESIGN: If survey_design.yaml defines strata/PSUs/weights, confirmatory estimands must be design-based by default...}
```

---

### 3️⃣ **Ambiguous Estimand** — HIGH PRIORITY
- **Location:** Results H1, line 25
- **Type:** `\pdfcomment` (PDF metadata annotation)
- **Issue:** Ordered logit contrast (−0.120) scale undefined
- **Flag:** Is it latent log-odds? Marginal effect? Probability difference? Missing Brant test.

```latex
\pdfcomment[author=Wes,subject={AMBIGUOUS ESTIMAND}]{Is −0.120 a latent log-odds parameter? ...}
```

---

### 4️⃣ **Effect Scale Not Contextualized** — MEDIUM PRIORITY
- **Location:** Results H3, line 27
- **Type:** `\pdfcomment` (PDF metadata annotation)
- **Issue:** −0.6544 reduction lacks context (range, SD, standardized units)
- **Flag:** Magnitude uninterpretable to readers

```latex
\pdfcomment[author=Wes,subject={EFFECT SCALE NOT CONTEXTUALIZED}]{−0.6544 reduction magnitude is meaningless without scale...}
```

---

### 5️⃣ **Zero P/Q Values** — MEDIUM PRIORITY
- **Location:** Results H3, line 27
- **Type:** `\pdfcomment` (PDF metadata annotation)
- **Issue:** p≈0 and q=0 are numerical underflow, not true zeros
- **Flag:** Should report as p<0.0001, q<0.0001; affects BH calculations

```latex
\pdfcomment[author=Wes,subject={ZERO P/Q VALUES}]{q=0 is underflow, not a true zero. Report as q<0.0001 or similar...}
```

---

### 6️⃣ **Jackknife k=6 Non-Standard** — MEDIUM PRIORITY
- **Location:** Sensitivity section, line 31
- **Type:** `\todo[inline]` (Colored todo box)
- **Issue:** Six pseudo-replicates violates standard practice (#replicates ≈ #PSUs)
- **Flag:** Appears arbitrary; will be questioned in review

```latex
\todo[inline]{JACKKNIFE k=6: Six pseudo-replicates is non-standard...}
```

---

### 7️⃣ **NC1 Validity: Confounded by Design** — HIGH PRIORITY
- **Location:** Discussion section, line 33
- **Type:** `\todo[inline]` (Colored todo box)
- **Issue:** Sibling count NOT a clean null; confounded by parental religiosity
- **Flag:** True null requires independence by causal structure, not just "outside BH family"

```latex
\todo[inline]{NC1 VALIDITY & INTERPRETATION: NC1 (sibling count) shows a large effect...}
```

---

### 8️⃣ **Literature & Robustness Inconsistency** — HIGH PRIORITY
- **Location:** Discussion section, line 35
- **Type:** `\todo[inline]` (Colored todo box)
- **Issue:** Three problems:
  - [CLAIM:*] assertions lack mechanism integration (moderator vs mediator?)
  - CrossRef fallbacks should be demoted from primary evidence
  - `robustness_passed = N` in results.csv but text claims stability

```latex
\todo[inline]{LITERATURE & ROBUSTNESS: (1) [CLAIM:*] tags are asserted but do not integrate mechanisms...}
```

---

## How to View Annotations

### **Via VSCode LaTeX Workshop**
1. File is ready: `manuscript_annotated.tex` (40 lines)
2. Open in VSCode → LaTeX Workshop auto-detects
3. Press **Cmd+Alt+B** (macOS) to build
4. View compiled PDF with:
   - **Yellow/pink inline boxes** = `\todo` annotations
   - **Clickable comment icons** = `\pdfcomment` annotations

### **Via Terminal (Requires TeX Live installed)**
```bash
cd /Users/wessel/ai_scientist
pdflatex manuscript_annotated.tex
open manuscript_annotated.pdf
```

### **Via Overleaf (Online)**
Upload `manuscript_annotated.tex` to [Overleaf.com](https://www.overleaf.com)  
→ Compile automatically  
→ Annotations visible in PDF viewer

---

## LaTeX Packages Used

| Package | Purpose | Line |
|---------|---------|------|
| `todonotes` | Inline colored todo boxes | 9 |
| `pdfcomment` | Embedded PDF comment annotations | 10 |

Both packages are **standard** and included in all major TeX distributions:
- ✅ TeX Live 2024+
- ✅ MacTeX 2024+
- ✅ MikTeX 2024+
- ✅ Overleaf (built-in)

---

## Annotation Statistics

| Category | Count | Severity |
|----------|-------|----------|
| **PDF Comments** (metadata) | 4 | 2 CRITICAL, 2 MEDIUM |
| **Todo Notes** (visual) | 4 | 4 HIGH |
| **Total Issues Flagged** | 8 | All actionable |

---

## Next Actions for You

1. ✅ **File Created:** `manuscript_annotated.tex` ready to compile
2. ⏳ **To Compile:**
   - Install TeX Live: `brew install mactex-no-gui`
   - OR use VSCode LaTeX Workshop (auto-compile)
   - OR upload to Overleaf
3. 📋 **To Address Issues:**
   - Use annotations as checklist (see summary table)
   - Edit corresponding sections in source document
   - Recompile to verify changes

---

## Reference: Annotation Locations

```
Line 17:  Abstract → NC1 Contradiction (PDF comment)
Line 22:  Methods → Survey Design (Todo)
Line 25:  Results H1 → Ambiguous Estimand (PDF comment)
Line 27:  Results H3 → Effect Scale (PDF comment)
Line 27:  Results H3 → Zero P/Q Values (PDF comment)
Line 31:  Sensitivity → Jackknife k=6 (Todo)
Line 33:  Discussion → NC1 Validity (Todo)
Line 35:  Discussion → Literature & Robustness (Todo)
```

---

## Files Generated

✅ `manuscript_annotated.tex` (40 lines) — Ready to compile  
✅ `README_ANNOTATIONS.md` — This file  
✅ `ANNOTATIONS_SUMMARY.md` — Detailed reference  
✅ `COMPILATION_GUIDE.md` — Compilation instructions


