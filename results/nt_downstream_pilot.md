# NT Downstream Pilot: Chromatin and Regulatory Tasks

Protocol: Hugging Face `InstaDeepAI/nucleotide_transformer_downstream_tasks`, binary classification on `H3K4me3` (histone ChIP-seq peak) and `enhancers`, pilot subset `2000/500/1000`, seeds `42-44`, real DNABERT-2 backbone, validation-accuracy best checkpoint, argmax test evaluation. Metadata-estimated GERM-BO uses label-free center-window k-mer JSD with train-quantile normalization.

## H3K4me3 chromatin mark (`H3K4me3`)

| Method | Seeds | Test Acc Mean +/- Std | Test F1 Mean +/- Std | Per-Seed Acc |
|---|---:|---:|---:|---|
| Baseline LoRA | 3 | 0.5410 +/- 0.0599 | 0.4691 +/- 0.1156 | 0.5100 / 0.5030 / 0.6100 |
| Metadata-estimated GERM-BO center-JSD | 3 | 0.5527 +/- 0.0269 | 0.5095 +/- 0.0588 | 0.5720 / 0.5640 / 0.5220 |

## Enhancers (regulatory elements) (`enhancers`)

| Method | Seeds | Test Acc Mean +/- Std | Test F1 Mean +/- Std | Per-Seed Acc |
|---|---:|---:|---:|---|
| Baseline LoRA | 3 | 0.7217 +/- 0.0274 | 0.7164 +/- 0.0341 | 0.7375 / 0.7375 / 0.6900 |
| Metadata-estimated GERM-BO center-JSD | 3 | 0.7292 +/- 0.0052 | 0.7265 +/- 0.0050 | 0.7250 / 0.7275 / 0.7350 |

## Paired Deltas (GERM-BO minus LoRA)

| Task | Metric | Delta Mean | Bootstrap 95% CI | Win Rate | Per-Seed Delta |
|---|---|---:|---:|---:|---|
| H3K4me3 | test_accuracy | +0.0117 | [-0.0880, +0.0620] | 66.7% | +0.0620 / +0.0610 / -0.0880 |
| H3K4me3 | test_f1 | +0.0404 | [-0.1539, +0.1830] | 66.7% | +0.1830 / +0.0921 / -0.1539 |
| enhancers | test_accuracy | +0.0075 | [-0.0125, +0.0450] | 33.3% | -0.0125 / -0.0100 / +0.0450 |
| enhancers | test_f1 | +0.0100 | [-0.0143, +0.0550] | 33.3% | -0.0143 / -0.0106 / +0.0550 |
