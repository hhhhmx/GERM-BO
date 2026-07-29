# Bioinformatics Original Paper package

Retarget of GERM-BO for *Bioinformatics* (Oxford University Press) as an **Original Paper**.

## Files

| File | Role |
|------|------|
| `main.tex` / `main.pdf` | Main manuscript (OUP template; target ≤7 pages) |
| `supplementary.tex` / `supplementary.pdf` | Supplementary Data (proofs + extra results) |
| `references.bib` | Bibliography |
| `figs/` | Figure PDFs |
| `cover_letter.docx` | Cover letter |
| `make_cover_letter.js` | Regenerates the cover letter |

## Compile

Requires TeX Live / MiKTeX with `oup-authoring-template` (CTAN).

```bash
cd latex/bioinformatics
pdflatex main.tex
bibtex main
pdflatex main.tex
pdflatex main.tex

pdflatex supplementary.tex
pdflatex supplementary.tex
```

Cover letter:

```bash
npm install
node make_cover_letter.js
```

## Submission settings (ScholarOne)

- **Article type:** Original Paper
- **Category:** Sequence analysis
- **Page limit:** ≤7 journal-template pages (current `main.pdf` is within limit)
- Upload compiled **PDF** (ScholarOne does not compile LaTeX); include source if requested
- Upload `supplementary.pdf` as Supplementary Data
- Upload `cover_letter.docx`
- Software must remain public at submission: https://github.com/hhhhmx/GERM-BO.git

## Notes

- Document class: `\documentclass[numsec,webpdf,modern,large]{oup-authoring-template}`
- Bibliography style: `abbrvnat`
- `\pdfminorversion=5` is set for ScholarOne PDF compatibility
- Prior KBS draft is preserved under `latex/kbs/` and is not modified by this package
