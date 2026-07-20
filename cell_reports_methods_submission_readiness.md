# Cell Reports Methods Submission Readiness

This checklist tracks the changes needed to submit the GERM-BO manuscript as a Cell Reports Methods-style article rather than a Cell Reports-style biological discovery article.

## Current framing

- Main manuscript: `cell-press-latex-template/main.tex`
- Current title: `GERM-BO: a reproducible border-aware adapter framework for genomic foundation models`
- Target article identity: reusable computational method and analytical framework for genomic foundation model adaptation
- Core claim: GERM-BO improves LoRA-style adaptation when border-rich genomic sequence structure is informative, and the benchmark suite defines where label-free scoring is not yet sufficient

## Already revised

- Reframed the title toward a reproducible methods article.
- Rewrote the Summary to foreground the reusable adapter framework, score channel, and benchmark protocol.
- Rewrote the Introduction opening around a method gap rather than a primarily biological insight.
- Added Highlights and an eTOC blurb for Cell Press-style editorial triage.
- Added a Results paragraph that frames the paper around method use, validation, and scope.
- Added a `Reproducibility package and intended use` subsection.
- Updated Data and code availability to require reviewer-accessible code and processed data at submission.

## Must complete before submission

- Replace `[REVIEWER_REPOSITORY_URL_TO_BE_ADDED]` with an anonymous reviewer-accessible repository or private review link.
- Replace the pending archive note with a Zenodo, OSF, Figshare, or institutional archive DOI before publication.
- Add a top-level `README.md` section or separate reviewer README with exact reproduction commands.
- Include processed train/validation/test splits for controlled border-aware tasks and the strict `3-mer-balanced` splice split.
- Include table and figure regeneration scripts for the main manuscript.
- Include a pinned environment file, such as `requirements.txt`, `environment.yml`, or a container recipe.
- Verify that every figure in the manuscript can be regenerated from archived scripts and data.
- Fill in missing author affiliations and lead-contact email in the manuscript.
- Verify the Key Resources Table contains software versions, dataset accessions, and model checkpoint identifiers.
- Compile the LaTeX manuscript after installing or locating `pdflatex`, `xelatex`, or `latexmk`.

## Recommended reviewer package layout

```text
reviewer_package/
  README.md
  requirements.txt
  configs/
  data_splits/
  src/
  tools/
  results/
  figures/
  reproduce/
    00_smoke_debug.ps1
    01_controlled_main.ps1
    02_strict_splice.ps1
    03_tables_and_figures.ps1
```

## Commands to expose in the reviewer README

```powershell
pip install -r requirements.txt
CUDA_VISIBLE_DEVICES=3 python train.py --config configs/default.yaml --debug
CUDA_VISIBLE_DEVICES=3 python eval.py --config configs/default.yaml --checkpoint outputs/debug/checkpoints/debug_last.pt --debug
```

For real-data validation, list the exact `real_*` configs used for the reported controlled, splice, ablation, and cross-backbone results.

Reviewer-facing PowerShell entry points now exist under `reproduce/`. Keep those scripts in the reviewer repository and verify them after copying data/model assets.

## Editorial risk checklist

- Do not present the paper as a direct Cell Reports transfer; the manuscript should read as a method with validation.
- Do not overclaim biological discovery from splice, promoter, chromatin, or enhancer pilots.
- Keep limitations explicit: DNABERT-2 strict splice is the strongest external result; NT v2 50M and HyenaDNA tiny are scope-defining pilots, not universal wins.
- Keep the phrase "label-free scoring remains insufficient" visible in Summary or Discussion.
- Make code and processed data available to reviewers at submission, not only after acceptance.
