# Enlarged Hard-Border Validation Threshold Tuning

## Setting

This analysis tunes the binary decision threshold on the validation split and applies that threshold to the test split.

- split: `data/splits_hard_border_large`
- checkpoint policy: validation `accuracy` with `mode=max`
- evaluated checkpoint: `checkpoints/best.pt`
- threshold selection: maximize validation accuracy, then validation F1, then closeness to `0.5`
- seeds: `42`, `43`, `44`

## Per-Seed Results

| Method | Seed | Threshold | Val Accuracy | Test Accuracy | Test F1 |
| --- | ---: | ---: | ---: | ---: | ---: |
| baseline LoRA | 42 | 0.5064 | 0.7813 | 0.8281 | 0.8321 |
| baseline LoRA | 43 | 0.4234 | 0.8438 | 0.8477 | 0.8602 |
| baseline LoRA | 44 | 0.4354 | 0.8125 | 0.8438 | 0.8561 |
| GERM-BO 0.27 | 42 | 0.4911 | 0.8711 | 0.8555 | 0.8538 |
| GERM-BO 0.27 | 43 | 0.4322 | 0.8242 | 0.8516 | 0.8571 |
| GERM-BO 0.27 | 44 | 0.4520 | 0.8594 | 0.8789 | 0.8692 |

## Three-Seed Summary

| Method | Accuracy Mean | Accuracy Std | F1 Mean | F1 Std |
| --- | ---: | ---: | ---: | ---: |
| baseline LoRA | 0.8398 | 0.0103 | 0.8495 | 0.0152 |
| GERM-BO 0.27 | 0.8620 | 0.0148 | 0.8600 | 0.0081 |

## Comparison

Validation threshold tuning improves both methods, but it helps GERM-BO more.

The matched fixed-threshold comparison was:

| Method | Accuracy Mean | Accuracy Std |
| --- | ---: | ---: |
| baseline LoRA | 0.8320 | 0.0238 |
| GERM-BO 0.27 | 0.8438 | 0.0117 |

After threshold tuning:

- baseline improves by `+0.0078` accuracy
- GERM-BO improves by `+0.0182` accuracy
- GERM-BO's mean accuracy advantage over baseline increases from `+0.0117` to `+0.0221`

## Interpretation

The threshold-tuned result is better for GERM-BO, but the accuracy gain over baseline is still moderate rather than decisive. It is now a consistent positive accuracy difference across all three seeds:

- seed `42`: `+0.0273`
- seed `43`: `+0.0039`
- seed `44`: `+0.0352`

This supports the hypothesis that part of GERM-BO's accuracy weakness came from fixed-threshold calibration. It does not fully solve the problem, but it makes the comparison more favorable.

## Next Accuracy-Oriented Fix

The next highest-value change is target-module ablation. Threshold tuning improves calibration, but the remaining accuracy gap is likely controlled by where GERM-BO is applied. The most useful variants are:

- `classifier` only
- `Wqkv + classifier`
- `attention.output + classifier`
- current full attention setting
