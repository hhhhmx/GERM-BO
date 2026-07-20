# Reviewer README for GERM-BO

This repository contains the code, processed data splits, configuration files, archived result summaries, and reproduction entry points for the Cell Reports Methods submission.

## Manuscript

- Title: GERM-BO: a reproducible border-aware adapter framework for genomic foundation models
- Article type framing: computational method / analytical framework
- Contact during review: through the journal editorial system
- Repository URL: https://github.com/hhhhmx/GERM-BO.git
- Permanent archive: Zenodo DOI to be added after the first archived GitHub release.

## Repository contents

```text
configs/      YAML files for all reported experiments
data/         processed train/validation/test splits or download/build scripts
figures/      manuscript figures and regeneration outputs
results/      summary tables and statistical outputs
src/          GERM-BO adapter, data loaders, models, and utilities
tools/        split preparation, evaluation, plotting, and summary scripts
reproduce/   reviewer-facing smoke, summary, and optional full-run scripts
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

Run this first to verify the environment and checkpoint path:

```powershell
$env:CUDA_VISIBLE_DEVICES="3"
python train.py --config configs/default.yaml --debug
python eval.py --config configs/default.yaml --checkpoint outputs/debug/checkpoints/debug_last.pt --debug
```

Equivalent scripted entry point:

```powershell
powershell -ExecutionPolicy Bypass -File reproduce/00_smoke_debug.ps1
```

Expected behavior: a short mock-data training run completes and writes `outputs/debug/checkpoints/debug_last.pt`.

## Main controlled result

The main controlled result uses the enlarged hard-border split with metadata-driven GERM-BO:

```powershell
$env:CUDA_VISIBLE_DEVICES="3"
bash tools/run_hard_border_large_metadata_13seed.sh
python tools/summarize_hard_border_large_metadata.py
```

Reviewer-facing PowerShell entry points:

```powershell
powershell -ExecutionPolicy Bypass -File reproduce/01_controlled_main.ps1
powershell -ExecutionPolicy Bypass -File reproduce/01_controlled_main.ps1 -RunTraining
```

Primary config:

```text
configs/real_dnabert2_germ_bo_hard_border_large_comp027_final_attn_output_classifier.yaml
```

Baseline and activation-derived comparison configs are listed in the manuscript tables and in `tools/run_hard_border_large_metadata_13seed.sh`.

## Strict splice benchmark

The strict external splice benchmark uses a 3-mer-balanced split and label-free center-window k-mer JSD scores:

```powershell
$env:CUDA_VISIBLE_DEVICES="3"
bash tools/run_splice_kmer_balanced_confirmation_50_54.sh
python tools/summarize_splice_kmer_balanced_confirmation_50_54.py
python tools/statistics_splice_kmer_balanced.py
```

Reviewer-facing PowerShell entry points:

```powershell
powershell -ExecutionPolicy Bypass -File reproduce/02_strict_splice.ps1
powershell -ExecutionPolicy Bypass -File reproduce/02_strict_splice.ps1 -RunTraining
```

Relevant configs include:

```text
configs/real_dnabert2_baseline_splice_sites_all_pilot.yaml
configs/real_dnabert2_germ_bo_quantile_q08_12_comp027_splice_sites_all_kmer_balanced.yaml
```

## Ablations and scope checks

Run only after the smoke test and main controlled result complete:

```powershell
$env:CUDA_VISIBLE_DEVICES="3"
bash tools/run_direction_aware_baselines_splice.sh
python tools/summarize_direction_aware_baselines_splice.py

bash tools/run_cross_backbone_border_hard.sh
python tools/summarize_cross_backbone_border_hard.py

bash tools/run_retention_tau_calibration_trained.sh
python tools/summarize_retention_tau_calibration.py
```

These runs support the manuscript claims about direction-aware baselines, cross-backbone scope, and activation-level retention calibration.

## Figures and tables

Regenerate manuscript figures and summary artifacts with:

```powershell
python tools/plot_experiment_figures.py
powershell -ExecutionPolicy Bypass -File reproduce/03_tables_and_figures.ps1
```

Table-specific summary scripts are stored under `tools/summarize_*.py` and `tools/statistics_*.py`.

## Notes for reviewers

- GERM-BO is expected to help when border-associated sequence structure is task-informative.
- The strongest external evidence is DNABERT-2 on the strict 3-mer-balanced splice split.
- NT v2 50M and HyenaDNA tiny experiments are included to define scope, not to claim universal gains.
- Promoter, chromatin, and enhancer pilots are scope analyses for label-free score estimation.
