# One remaining step after GitHub public release

GitHub is already public with MIT and release tag `v0.1.0-bioinformatics`:
https://github.com/hhhhmx/GERM-BO/releases/tag/v0.1.0-bioinformatics

## Mint Zenodo DOI (required before ScholarOne)

1. Sign in at https://zenodo.org with GitHub.
2. Open https://zenodo.org/account/settings/github/
3. Flip **ON** for repository `hhhhmx/GERM-BO`.
4. If the release was published before enabling the toggle, either:
   - click **Sync now** / wait for the webhook, or
   - edit the release notes on GitHub and save (retriggers), or
   - create a tiny follow-up tag `v0.1.0-bioinformatics.1`.
5. Open the new Zenodo record and copy the **Version DOI**
   (looks like `https://doi.org/10.5281/zenodo.########`).

## Paste DOI into the manuscript

Replace `10.5281/zenodo.PENDING` in:

- `latex/bioinformatics/main.tex` (abstract + Data availability)
- `reviewer_repository/manuscript/bioinformatics/main.tex`
- `reviewer_repository/README.md`

Then rebuild:

```powershell
cd latex\bioinformatics
pdflatex main.tex
bibtex main
pdflatex main.tex
pdflatex main.tex
```

Optional: set `$env:ZENODO_TOKEN` and run `.\tools\wait_zenodo_and_patch.ps1` if you prefer automation after enabling the integration.
