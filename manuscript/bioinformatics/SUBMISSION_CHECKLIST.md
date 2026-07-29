# Bioinformatics submission blockers — completion checklist

Use this after the local package is ready. *Bioinformatics* requires software to be freely reachable **at submission**, with an archived DOI in the abstract Availability section.

## Already done locally

- [x] MIT `LICENSE` in `reviewer_repository/` (and synced copies)
- [x] README / Zenodo metadata retargeted to *Bioinformatics* Original Paper
- [x] Structured abstract with Availability (MIT + GitHub + Zenodo placeholder)
- [x] Expanded Methods: train/val/test sizes + 3-mer-balanced homology/composition controls
- [x] `.zenodo.json` and `CITATION.cff` prepared
- [x] Cover letter for Bioinformatics

## You must finish (needs your GitHub/Zenodo login)

### 1. Make the GitHub repository public

```powershell
cd reviewer_repository
git add -A
git commit -m "Prepare Bioinformatics submission package with MIT license"
git push -u origin main
```

Then on GitHub: **Settings → General → Danger Zone → Change visibility → Public**.

Confirm in a private browser: https://github.com/hhhhmx/GERM-BO

### 2. Mint Zenodo DOI and paste into the manuscript

Follow `CREATE_ZENODO_DOI.md` (enable Zenodo↔GitHub, publish tag `v0.1.0-bioinformatics`).

Replace **every** `10.5281/zenodo.PENDING` occurrence in:

- `latex/bioinformatics/main.tex` (abstract + Data availability)
- `reviewer_repository/manuscript/bioinformatics/main.tex`
- `reviewer_repository/README.md` (if still placeholder)

Rebuild PDF:

```powershell
cd latex\bioinformatics
pdflatex main.tex
bibtex main
pdflatex main.tex
pdflatex main.tex
```

### 3. ScholarOne upload set

- `main.pdf` (≤7 pages)
- `supplementary.pdf`
- `cover_letter.docx`
- Category: Sequence analysis
- Article type: Original Paper
