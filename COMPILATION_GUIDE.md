# Compilation Guide for Annotated Manuscript

## Status
✅ **Annotated TeX file created:** `manuscript_annotated.tex` (40 lines)  
❌ **PDF compilation:** Requires LaTeX installation (not currently available in sandbox)

## What Was Added to the TeX File

The manuscript has been annotated with **8 critical scientific issues** using:

1. **`\usepackage{pdfcomment}`** – For embedded PDF comments  
2. **`\usepackage[colorinlistoftodos]{todonotes}`** – For inline todo boxes

All annotations are **non-intrusive** (placed inline without altering original text flow).

---

## How to Compile

### Option 1: VSCode LaTeX Workshop Extension (Recommended)
Since you have VSCode LaTeX Workshop installed:

1. Open VSCode and open `manuscript_annotated.tex`
2. Ensure LaTeX Workshop is enabled
3. Build will auto-trigger, OR manually:
   - Press **Cmd+Alt+B** (macOS) or **Ctrl+Alt+B** (Linux/Windows)
   - Or use Command Palette: `LaTeX Workshop: Build LaTeX project`

4. PDF will be generated at: `manuscript_annotated.pdf`

**Note:** LaTeX Workshop requires a TeX distribution (TeX Live, MacTeX, MikTeX) to be installed on your system first.

---

### Option 2: Install TeX Live via Homebrew
If LaTeX is not installed, install it first:

```bash
# For macOS - install MacTeX (BasicTeX is lighter)
brew install mactex-no-gui
# or for full distribution:
# brew install mactex

# Then compile:
cd /Users/wessel/ai_scientist
pdflatex manuscript_annotated.tex
```

Then reopen in VSCode LaTeX Workshop to see the formatted annotations.

---

### Option 3: Use Online LaTeX Compiler (Overleaf)
1. Go to [Overleaf.com](https://www.overleaf.com)
2. Create a new project
3. Upload `manuscript_annotated.tex`
4. Add any required `.bib` files (if needed for references)
5. Compile and view with annotations in the PDF

---

## Viewing Annotations in the PDF

Once compiled, you'll see:

### **Inline Todo Boxes** (Colored highlighted text)
Appears as **colored boxes** in the margins with the annotation text:
- **Methods section:** Survey design scope issue
- **Sensitivity section:** Jackknife k=6 justification
- **Discussion section:** NC1 validity and mechanism integration

Click on todo items in the **"TODO List"** panel in VSCode LaTeX Workshop.

### **PDF Comments** (Metadata annotations)
Appears as **clickable comment icons** in the PDF viewer:
- **Abstract:** NC1 contradiction (near zero vs +0.2388)
- **Results H1:** Ordered logit estimand ambiguity
- **Results H3:** Effect scale and zero p-values

Click the comment icons to see:
- **Author:** Wes
- **Subject:** Issue title
- **Content:** Full explanation

---

## Annotations Checklist

- [ ] **NC1 Contradiction** – Abstract vs Results table discrepancy
- [ ] **Survey Design** – SRS assumption vs design-based estimands
- [ ] **Ambiguous Estimand** – Ordered logit scale not defined
- [ ] **Effect Scale** – H3 magnitude without contextual reference
- [ ] **Zero P/Q Values** – Underflow reporting vs p<1e-k
- [ ] **Jackknife k=6** – Non-standard replicate scheme
- [ ] **NC1 Validity** – Not a clean null (confounded by parental traits)
- [ ] **Literature & Robustness** – Mechanism integration and consistency

---

## Quick Reference: Annotation Locations

| Annotation | Section | Type | Line |
|-----------|---------|------|------|
| NC1 Contradiction | Abstract | PDF Comment | 17 |
| Survey Design | Methods | Todo | 22 |
| Ambiguous Estimand | Results H1 | PDF Comment | 25 |
| Effect Scale | Results H3 | PDF Comment | 27 |
| Zero P/Q Values | Results H3 | PDF Comment | 27 |
| Jackknife k=6 | Sensitivity | Todo | 31 |
| NC1 Validity | Discussion | Todo | 33 |
| Literature & Robustness | Discussion | Todo | 35 |

---

## Next Steps

1. **Install TeX Live** (if not already installed)
2. **Open in VSCode** → Auto-compile or press **Cmd+Alt+B**
3. **View PDF** → Click comments and check todo list
4. **Address each annotation** in the source document or manuscript content

---

## Files Generated

- ✅ `manuscript_annotated.tex` – Annotated source (40 lines)
- 📋 `ANNOTATIONS_SUMMARY.md` – Detailed annotation guide
- 📋 `COMPILATION_GUIDE.md` – This file
- (Pending) `manuscript_annotated.pdf` – Compiled output with visible annotations


