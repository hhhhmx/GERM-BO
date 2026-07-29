# GERM-BO

Border-aware adapter framework for resource-efficient genomic foundation model adaptation.

This repository contains code, processed data splits, configuration files, archived result summaries, manuscript files, and reproduction entry points for the *Bioinformatics* Original Paper submission.

## Manuscript

- Title: GERM-BO: a reproducible border-aware adapter framework for genomic foundation models
- Article type: Original Paper (*Bioinformatics*)
- Suggested category: Sequence analysis
- Repository: https://github.com/hhhhmx/GERM-BO
- License: MIT (`LICENSE`)
- Permanent archive: https://doi.org/10.5281/zenodo.PENDING (replace after minting; see CREATE_ZENODO_DOI.md)

## Repository contents

```text
configs/      YAML files for all reported experiments
data/         processed train/validation/test splits or download/build scripts
figures/      manuscript figures and regeneration outputs
results/      summary tables and statistical outputs
src/          GERM-BO adapter, data loaders, models, and utilities
tools/        split preparation, evaluation, plotting, and summary scripts
reproduce/    reviewer-facing smoke, summary, and optional full-run scripts
manuscript/   submission manuscript materials
train.py      training entry point
eval.py       evaluation entry point
requirements.txt
```

## Environment

Use Python 3.10+ and install dependencies with:

```powershell
pip install -r requirements.txt
```

All reported training and evaluation commands are single-GPU. The manuscript policy is:

```powershell
$env:CUDA_VISIBLE_DEVICES="3"
```

No DDP, DataParallel, DeepSpeed, or FSDP is used.

## Smoke test

```powershell
$env:CUDA_VISIBLE_DEVICES="3"
python train.py --config configs/default.yaml --debug
python eval.py --config configs/default.yaml --checkpoint outputs/debug/checkpoints/debug_last.pt --debug
```

Or:

```powershell
powershell -ExecutionPolicy Bypass -File reproduce/00_smoke_debug.ps1
```

## Main controlled result

```powershell
$env:CUDA_VISIBLE_DEVICES="3"
bash tools/run_hard_border_large_metadata_13seed.sh
python tools/summarize_hard_border_large_metadata.py
```

Primary config:

```text
configs/real_dnabert2_germ_bo_hard_border_large_comp027_final_attn_output_classifier.yaml
```

Split sizes: `data/splits_hard_border_large` is 1024/256/256 train/validation/test.

## Strict splice benchmark

The strict external splice benchmark uses a 3-mer-balanced split and label-free center-window k-mer JSD scores:

```powershell
$env:CUDA_VISIBLE_DEVICES="3"
bash tools/run_splice_kmer_balanced_confirmation_50_54.sh
python tools/summarize_splice_kmer_balanced_confirmation_50_54.py
python tools/statistics_splice_kmer_balanced.py
```

Released balanced split sizes: `data/benchmarks/splice_sites_all_kmer_balanced` is 9000/1800/1800 train/validation/test.

Relevant config:

```text
configs/real_dnabert2_germ_bo_quantile_q08_12_comp027_splice_sites_all_kmer_balanced.yaml
```

## Ablations and scope checks

```powershell
$env:CUDA_VISIBLE_DEVICES="3"
bash tools/run_direction_aware_baselines_splice.sh
python tools/summarize_direction_aware_baselines_splice.py

bash tools/run_cross_backbone_border_hard.sh
python tools/summarize_cross_backbone_border_hard.py

bash tools/run_retention_tau_calibration_trained.sh
python tools/summarize_retention_tau_calibration.py
```

## Figures and tables

```powershell
python tools/plot_experiment_figures.py
powershell -ExecutionPolicy Bypass -File reproduce/03_tables_and_figures.ps1
```

## Notes for reviewers

- GERM-BO is expected to help when border-associated sequence structure is task-informative.
- The strongest external evidence is DNABERT-2 on the strict 3-mer-balanced splice split.
- NT v2 50M and HyenaDNA tiny experiments define scope, not universal gains.
- Promoter, chromatin, and enhancer pilots are scope analyses for label-free score estimation.
- Code and data in this repository are released under the MIT license for non-commercial and commercial use without request.
