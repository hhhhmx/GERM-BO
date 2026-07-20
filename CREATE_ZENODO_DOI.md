# Creating a Zenodo DOI from GitHub

Use this workflow after the GitHub repository is ready.

## One-time Zenodo setup

1. Sign in to Zenodo with GitHub.
2. Open the Zenodo GitHub integration page: https://zenodo.org/account/settings/github/
3. Find `hhhhmx/GERM-BO`.
4. Turn on archiving for the repository.

## Create the archived release

1. Go to the GitHub repository: https://github.com/hhhhmx/GERM-BO
2. Open `Releases`.
3. Select `Draft a new release`.
4. Use a tag such as `v0.1.0-review`.
5. Use a title such as `GERM-BO reviewer package v0.1.0`.
6. In the release notes, write:

```text
Reviewer package for the Cell Reports Methods submission.

This release contains code, processed data splits, configuration files,
archived result summaries, manuscript files, and reproduction entry points.
```

7. Publish the release.
8. Wait for Zenodo to archive the release.
9. Copy the Zenodo DOI URL.

## After Zenodo creates the DOI

Replace the pending Zenodo DOI note in:

- `manuscript/main.tex`
- `README.md`
- the working manuscript at `cell-press-latex-template/main.tex`

Then rebuild the manuscript PDF and push one final GitHub release if needed.
