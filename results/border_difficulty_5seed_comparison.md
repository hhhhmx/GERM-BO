# Border Difficulty Extension: 5-Seed Results

Protocol: real DNABERT-2-117M backbone, task-specific synthetic file splits with 1024/256/256 train/val/test samples, seeds `42-46`, validation-accuracy best checkpoint, early stopping patience 2, and validation-threshold tuned test evaluation. All remote training and threshold-tuning commands used explicit `CUDA_VISIBLE_DEVICES=3`; every result JSON reports one visible GPU.

| Task | Method | Test accuracy mean +/- std | Test F1 mean +/- std | Per-seed test accuracy |
|---|---|---:|---:|---:|
| border_easy | Baseline LoRA | 0.9922 +/- 0.0062 | 0.9921 +/- 0.0063 | 0.9922 / 0.9883 / 1.0000 / 0.9961 / 0.9844 |
| border_easy | GERM-BO final | 0.9883 +/- 0.0092 | 0.9881 +/- 0.0094 | 0.9961 / 0.9805 / 0.9961 / 0.9766 / 0.9922 |
| border_medium | Baseline LoRA | 0.8859 +/- 0.0271 | 0.8889 +/- 0.0258 | 0.9258 / 0.8555 / 0.8789 / 0.8711 / 0.8984 |
| border_medium | GERM-BO final | 0.8227 +/- 0.0987 | 0.8318 +/- 0.0964 | 0.8242 / 0.8789 / 0.8633 / 0.8945 / 0.6523 |
| border_hard | Baseline LoRA | 0.8359 +/- 0.0279 | 0.8365 +/- 0.0356 | 0.8477 / 0.8555 / 0.8320 / 0.8555 / 0.7891 |
| border_hard | GERM-BO final | 0.8398 +/- 0.0309 | 0.8461 +/- 0.0307 | 0.8477 / 0.7969 / 0.8711 / 0.8203 / 0.8633 |

| Task | Accuracy delta mean | Accuracy bootstrap 95% CI | Accuracy win rate | F1 delta mean | F1 bootstrap 95% CI |
|---|---:|---:|---:|---:|---:|
| border_easy | -0.0039 | [-0.0125, +0.0039] | 40.0% | -0.0040 | [-0.0127, +0.0040] |
| border_medium | -0.0633 | [-0.1633, +0.0156] | 40.0% | -0.0571 | [-0.1540, +0.0173] |
| border_hard | +0.0039 | [-0.0375, +0.0453] | 40.0% | +0.0096 | [-0.0360, +0.0557] |

Interpretation: the easy task saturates both methods and is not discriminative. The medium task currently disfavors GERM-BO final because seed 46 collapses to `0.6523`, so this task needs failure analysis before being used as a claim. The hard task is the most relevant extension: GERM-BO final is slightly above baseline on mean accuracy and F1, but the 5-seed confidence interval crosses zero. This supports reporting the original enlarged hard-border result as the main evidence, with the new hard task as a neutral-to-slight-positive robustness check rather than a decisive second win.
