# Uploading the Reviewer Repository

The local reviewer package has two forms:

- Directory: `reviewer_repository/`
- Zip archive: `reviewer_repository.zip`

Use the directory when uploading to GitHub. Use the zip when uploading to OSF, Zenodo, or the journal submission system.

## Option A: Private GitHub Repository

This is the easiest option if the journal or editor can access a private review link or if you can invite specific reviewers/editors.

1. Create a new private repository on GitHub.
2. Do not initialize it with a README, license, or `.gitignore`.
3. From `reviewer_repository/`, initialize git and push:

```powershell
cd reviewer_repository
git init
git add .
git commit -m "Add reviewer package"
git branch -M main
git remote add origin https://github.com/YOUR_ACCOUNT/YOUR_PRIVATE_REPO.git
git push -u origin main
```

4. Add editor/reviewer access if the journal provides GitHub usernames, or use the private repository link in the submission notes if allowed.

Pros: best for code review and version updates.

Risk: a normal private GitHub URL is not automatically accessible to anonymous reviewers unless access is granted.

## Option B: OSF Private Project With View-Only Link

This is a good option for anonymous peer review because OSF supports private projects and view-only links.

1. Create a private OSF project.
2. Upload `reviewer_repository.zip`.
3. Generate a view-only link for peer review.
4. Put that view-only link in the manuscript's Data and code availability statement.

Pros: easy anonymous access.

Risk: less convenient for browsing code than GitHub.

## Option C: Zenodo Restricted or Draft Record

Use Zenodo when you want a citable archive and DOI.

1. Create a Zenodo upload record.
2. Upload `reviewer_repository.zip`.
3. Keep the record as a draft or restricted/private until publication policy is clear.
4. Reserve or create the DOI before publication.
5. Replace `[ARCHIVE_DOI_URL_TO_BE_ADDED]` in the manuscript and reviewer README.

Pros: DOI and long-term archive.

Risk: not always the smoothest anonymous review workflow before acceptance.

## What to Put in the Manuscript

In `cell-press-latex-template/main.tex`, replace:

```text
[REVIEWER_REPOSITORY_URL_TO_BE_ADDED]
[ARCHIVE_DOI_URL_TO_BE_ADDED]
```

Use the OSF view-only link or private review link for the first placeholder. Use the Zenodo/OSF/Figshare DOI URL for the second placeholder when available.

## Pre-Upload Checks

Run:

```powershell
powershell -ExecutionPolicy Bypass -File .\build_reviewer_repository.ps1
powershell -ExecutionPolicy Bypass -File .\compile_cell_press.ps1
```

Then verify:

- `reviewer_repository/README.md` opens correctly.
- `reviewer_repository/reproduce/00_smoke_debug.ps1` exists.
- `reviewer_repository/data/splits_hard_border_large/train.csv` exists.
- `reviewer_repository/data/benchmarks/splice_sites_all_kmer_balanced/train.csv` exists.
- `reviewer_repository/manuscript/main.pdf` exists.
- `reviewer_repository.zip` is under the upload limit for the selected platform.

