# Annotation Source Code Reference

All 8 annotations are embedded in `manuscript_annotated.tex`. Below is the exact LaTeX code for each.

---

## 1. NC1 Contradiction (Abstract) — PDF Comment

**Line:** 17  
**Type:** `\pdfcomment`  
**Severity:** 🔴 CRITICAL

```latex
\pdfcomment[author=Wes,subject={CRITICAL: NC1 Contradiction}]{NC1 abstract claim "stays near zero" contradicts Results table (+0.2388 [0.2209, 0.2568], p≈0). This is a large effect, not near-zero.}
```

**Placement:** Between effect results and NC1 discussion in abstract.

---

## 2. Survey Design Mismatch (Methods) — Todo Note

**Line:** 22  
**Type:** `\todo[inline]`  
**Severity:** 🟠 HIGH

```latex
\todo[inline]{SURVEY DESIGN: If survey\_design.yaml defines strata/PSUs/weights, confirmatory estimands must be design-based by default. Current SRS baseline + ad-hoc sensitivity risks bias. Clarify scope: are results sample-level descriptive or population-level design-adjusted?}
```

**Placement:** After SRS assumption mention in Methods section.

---

## 3. Ambiguous Estimand (Results H1) — PDF Comment

**Line:** 25  
**Type:** `\pdfcomment`  
**Severity:** 🟠 HIGH

```latex
\pdfcomment[author=Wes,subject={AMBIGUOUS ESTIMAND}]{Is −0.120 a latent log-odds parameter? Marginal effect on 5-level score? Probability difference for top category? Without explicit scale definition, uninterpretable. Also missing: Brant test or PO assumption check.}
```

**Placement:** At start of H1 result description.

---

## 4. Effect Scale Not Contextualized (Results H3) — PDF Comment

**Line:** 27  
**Type:** `\pdfcomment`  
**Severity:** 🟡 MEDIUM

```latex
\pdfcomment[author=Wes,subject={EFFECT SCALE NOT CONTEXTUALIZED}]{−0.6544 reduction magnitude is meaningless without scale (range, SD). How big is this? Report standardized effect or absolute range to aid interpretation.}
```

**Placement:** Before H3 effect size in Results section.

---

## 5. Zero P/Q Values (Results H3) — PDF Comment

**Line:** 27  
**Type:** `\pdfcomment`  
**Severity:** 🟡 MEDIUM

```latex
\pdfcomment[author=Wes,subject={ZERO P/Q VALUES}]{q=0 is underflow, not a true zero. Report as q<0.0001 or similar. Same for p≈0 in H2 and NC1. These affect downstream BH calculations.}
```

**Placement:** After H3 q-value in Results section.

---

## 6. Jackknife k=6 Non-Standard (Sensitivity) — Todo Note

**Line:** 31  
**Type:** `\todo[inline]`  
**Severity:** 🟡 MEDIUM

```latex
\todo[inline]{JACKKNIFE k=6: Six pseudo-replicates is non-standard. Accepted schemes use \#replicates≈\#PSUs or official replicate-weight scheme. k=6 appears arbitrary and will draw criticism. Justify or revert to standard bootstrap/BRR.}
```

**Placement:** Before k=6 replicate discussion in Sensitivity section.

**Note:** The `\#` escapes the `#` character in LaTeX.

---

## 7. NC1 Validity & Interpretation (Discussion) — Todo Note

**Line:** 33  
**Type:** `\todo[inline]`  
**Severity:** 🟠 HIGH

```latex
\todo[inline]{NC1 VALIDITY \& INTERPRETATION: NC1 (sibling count) shows a large effect (+0.2388). This is NOT a "clean null" because parental religiosity likely predicts both sibling count and the exposure. Sibling count is not independent of parental traits—it is confounded by design. A true null control should be unrelated by causal structure, not just "not in the BH family."}
```

**Placement:** Before NC1 conclusion in Discussion section.

**Note:** The `\&` escapes the `&` character in LaTeX.

---

## 8. Literature & Robustness (Discussion) — Todo Note

**Line:** 35  
**Type:** `\todo[inline]`  
**Severity:** 🟠 HIGH

```latex
\todo[inline]{LITERATURE \& ROBUSTNESS: (1) [CLAIM:*] tags are asserted but do not integrate mechanisms (resilience as moderator vs mediator?). (2) CrossRef fallbacks should be demoted from primary evidence. (3) In results.csv, robustness\_passed = N for H1–H3, yet text claims stability. This is inconsistent and should block celebratory language until prespecified checks pass or are transparently labeled exploratory.}
```

**Placement:** After CLAIM tags in Discussion section.

**Notes:** 
- The `\&` escapes the `&` character
- The `\_` escapes the underscore in `robustness\_passed`

---

## Package Declarations (Lines 9-10)

Both packages must be declared in the preamble:

```latex
\usepackage[colorinlistoftodos,textsize=footnotesize]{todonotes}
\usepackage{pdfcomment}
```

**Options explained:**
- `colorinlistoftodos` — Generates a colored list of todos
- `textsize=footnotesize` — Reduces todo text size for readability
- `pdfcomment` — No options required; standard PDF comment support

---

## Rendering Behavior

### PDF Comments (`\pdfcomment`)
- Appear as **clickable comment icons** in PDF viewer (top-right of text)
- Author, subject, and content visible on click
- Compatible with: Adobe Reader, Preview (macOS), most PDF viewers
- Won't render if pdfcomment package not installed

### Todo Notes (`\todo[inline]`)
- Appear as **colored boxes** (default: yellow)
- Positioned in right margin or inline
- Automatically collected in **List of Todos** at document start
- Can be toggled off with `\todo[disable]` globally

---

## LaTeX Syntax Rules Applied

| Rule | Example | Why |
|------|---------|-----|
| Escape `&` | `\&` | Special character in LaTeX |
| Escape `#` | `\#` | Special character in LaTeX |
| Escape `_` | `\_` | Special character in LaTeX |
| Nested braces | `{...{...}...}` | Proper nesting for macro arguments |
| Line breaks inside macros | Can span lines | LaTeX ignores extra whitespace |

---

## Validation Checklist

✅ All 8 annotations present  
✅ Proper LaTeX escaping applied  
✅ Nested braces balanced  
✅ Package declarations included  
✅ Author/subject tags formatted correctly  
✅ No syntax errors  
✅ Non-intrusive (don't alter original text)  

---

## Testing Compilation

To verify annotations compile correctly:

```bash
cd /Users/wessel/ai_scientist
pdflatex -draftmode manuscript_annotated.tex  # Draft mode (faster)
echo $?  # Exit code: 0 = success
```

---

## If Compilation Fails

Common issues and fixes:

| Error | Cause | Fix |
|-------|-------|-----|
| `Undefined control sequence \pdfcomment` | Package not installed | `tlmgr install pdfcomment` |
| `Undefined control sequence \todo` | Package not installed | `tlmgr install todonotes` |
| `Missing $ inserted` | Math mode error | Check escaped special chars |
| `Argument of \pdfcomment has an extra }` | Unmatched braces | Verify nesting in annotation |

---

## Reference: Full Annotated TeX File

File: `/Users/wessel/ai_scientist/manuscript_annotated.tex`  
Lines: 40 total  
Size: ~8.2 KB  
Encoding: UTF-8  

To view full content:
```bash
cat /Users/wessel/ai_scientist/manuscript_annotated.tex
```

---

Last Updated: 2025-11-10

