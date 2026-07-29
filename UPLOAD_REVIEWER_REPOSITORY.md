# Uploading the Reviewer Repository (Bioinformatics)

*Bioinformatics* requires source code to be **freely available without request at submission**, plus an archived DOI (Zenodo/Figshare/Software Heritage) in the abstract Availability section. Do **not** use a private GitHub-only review link for this journal.

Local package forms:

- Directory: `reviewer_repository/`
- Zip archive: `reviewer_repository.zip` (optional mirror)

## Required path: Public GitHub + Zenodo DOI

1. Ensure `LICENSE` (MIT), `README.md`, `.zenodo.json`, and processed splits are present in `reviewer_repository/`.
2. Push to https://github.com/hhhhmx/GERM-BO and set the repository to **Public**.
3. Enable Zenodo GitHub integration and publish release tag `v0.1.0-bioinformatics` (see `CREATE_ZENODO_DOI.md`).
4. Paste the minted DOI into `latex/bioinformatics/main.tex` Availability / Data availability (replace `zenodo.PENDING`).
5. Rebuild `main.pdf` and upload to ScholarOne with `supplementary.pdf` and `cover_letter.docx`.

## Optional mirrors

- OSF or Figshare can host `reviewer_repository.zip` as an additional archive, but they do not replace the GitHub URL stated in the abstract.
- Software Heritage save can be used if Zenodo is delayed; switch to the Zenodo DOI once available.

## Pre-upload checks

```powershell
powershell -ExecutionPolicy Bypass -File .\build_reviewer_repository.ps1
```

Verify:

- `reviewer_repository/LICENSE` exists (MIT)
- `reviewer_repository/README.md` names *Bioinformatics*
- `reviewer_repository/data/splits_hard_border_large/train.csv` exists
- `reviewer_repository/data/benchmarks/splice_sites_all_kmer_balanced/train.csv` exists
- `latex/bioinformatics/main.pdf` is ≤7 pages and has no `zenodo.PENDING` left
