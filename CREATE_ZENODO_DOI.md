# Creating a Zenodo DOI from GitHub

Required for *Bioinformatics* software availability: archive the submitted version at Zenodo (or Figshare / Software Heritage) and put the DOI in the manuscript Availability section **before or at submission**.

## One-time Zenodo setup

1. Sign in to Zenodo with GitHub: https://zenodo.org
2. Open GitHub integration: https://zenodo.org/account/settings/github/
3. Find `hhhhmx/GERM-BO` and **enable** archiving.
4. Confirm the repository is **public** and contains `LICENSE` (MIT) and `.zenodo.json`.

## Create the archived release

1. Go to https://github.com/hhhhmx/GERM-BO/releases
2. Draft a new release with tag `v0.1.0-bioinformatics` (or the tag created by the submission prep script).
3. Title: `GERM-BO Bioinformatics submission package v0.1.0`
4. Release notes example:

```text
Reviewer/submission package for the Bioinformatics Original Paper.

Contains code, processed data splits, configuration files,
archived result summaries, manuscript materials, and reproduction entry points.
License: MIT.
```

5. Publish the release.
6. Wait for Zenodo to create the record (often a few minutes).
7. Copy the Concept DOI or Version DOI (prefer the version DOI for the submitted snapshot).

## After Zenodo creates the DOI

1. Replace the Zenodo URL placeholder in:
   - `latex/bioinformatics/main.tex` (Availability and Implementation)
   - `README.md`
   - `CITATION.cff` (`doi:` field, optional)
2. Rebuild `latex/bioinformatics/main.pdf`.
3. Optionally publish a tiny follow-up commit that only updates the DOI string.

## Fallback archive

If Zenodo GitHub integration is delayed, request a Software Heritage save of
`https://github.com/hhhhmx/GERM-BO` and temporarily cite the SWHID, then switch to the Zenodo DOI once available.
