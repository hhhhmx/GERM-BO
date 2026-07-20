# Enlarged Hard-Border Matched Baseline Comparison

## Setting

This comparison uses the same enlarged hard-border split and the same accuracy-focused checkpoint policy for both methods.

- split: `data/splits_hard_border_large`
- checkpoint policy: validation `accuracy` with `mode=max`
- evaluated checkpoint: `checkpoints/best.pt`
- seeds: `42`, `43`, `44`
- baseline config: `configs/real_dnabert2_baseline_hard_border_large_formal.yaml`
- GERM-BO config: `configs/real_dnabert2_germ_bo_hard_border_large_comp027_formal.yaml`

## Per-Seed Results

| Method | Seed | Accuracy | F1 | Loss |
| --- | ---: | ---: | ---: | ---: |
| baseline LoRA | 42 | 0.8047 | 0.8201 | 0.6073 |
| baseline LoRA | 43 | 0.8477 | 0.8395 | 0.5009 |
| baseline LoRA | 44 | 0.8438 | 0.8291 | 0.5024 |
| GERM-BO 0.27 | 42 | 0.8555 | 0.8477 | 0.5404 |
| GERM-BO 0.27 | 43 | 0.8438 | 0.8276 | 0.4963 |
| GERM-BO 0.27 | 44 | 0.8320 | 0.8054 | 0.4575 |

## Three-Seed Summary

| Method | Accuracy Mean | Accuracy Std | F1 Mean | F1 Std | Loss Mean | Loss Std |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| baseline LoRA | 0.8320 | 0.0238 | 0.8296 | 0.0097 | 0.5369 | 0.0610 |
| GERM-BO 0.27 | 0.8438 | 0.0117 | 0.8269 | 0.0212 | 0.4981 | 0.0415 |

## Interpretation

The matched comparison does not show a clear accuracy win for GERM-BO. The average accuracy is higher by only `+0.0117`, and the per-seed pattern is mixed:

- seed `42`: GERM-BO is better by `+0.0508`
- seed `43`: GERM-BO is lower by `-0.0039`
- seed `44`: GERM-BO is lower by `-0.0117`

GERM-BO does improve mean loss and reduce accuracy variance, but the accuracy gain is too small to call a meaningful improvement over the matched baseline.

## What To Fix Next

The next changes should target accuracy directly rather than continuing broad compensation sweeps:

- tune threshold on the validation split instead of using fixed argmax
- reduce learning rate or add a scheduler to improve late-epoch stability
- test whether GERM-BO should be applied only to `classifier` or only to `Wqkv`, because current attention-output compensation may be hurting some seeds
- add a small accuracy-oriented grid around rank and alpha, not only compensation strength
- compare against baseline with the same threshold-tuning protocol before claiming improvement
