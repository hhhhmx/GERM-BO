# Splice Sites All Boundary-Sensitive Pilot

Protocol: Hugging Face `InstaDeepAI/nucleotide_transformer_downstream_tasks/splice_sites_all`, 3-class splice-site classification, pilot subset `3000/600/1200`, seeds `42-44`, real DNABERT-2 backbone, validation-accuracy best checkpoint, and argmax test evaluation. Metadata-estimated GERM-BO uses a label-free center-window k-mer JSD score.

## Summary

| Method | Seeds | Test Acc Mean +/- Std | Test F1 Mean +/- Std | Per-Seed Acc |
|---|---:|---:|---:|---|
| Baseline LoRA | 3 | 0.3597 +/- 0.0245 | 0.2481 +/- 0.0705 | 0.3642 / 0.3333 / 0.3817 |
| Metadata-estimated GERM-BO center-JSD | 3 | 0.3975 +/- 0.0044 | 0.3467 +/- 0.0252 | 0.3958 / 0.3942 / 0.4025 |

## Paired Deltas

| Comparison | Metric | Delta Mean | Bootstrap 95% CI | Win Rate | Per-Seed Delta |
|---|---|---:|---:|---:|---|
| germ_bo_center_jsd_minus_baseline_lora | test_accuracy | +0.0378 | [+0.0208, +0.0608] | 100.0% | +0.0317 / +0.0608 / +0.0208 |
| germ_bo_center_jsd_minus_baseline_lora | test_f1 | +0.0987 | [+0.0615, +0.1526] | 100.0% | +0.0615 / +0.1526 / +0.0819 |
