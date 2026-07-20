# Enlarged Hard-Border Accuracy-Max Best-Checkpoint Rerun

## Setting

- config: `configs/real_dnabert2_germ_bo_hard_border_large_comp027_formal.yaml`
- split: `data/splits_hard_border_large`
- split size: `1024 / 256 / 256`
- backbone: `DNABERT-2-117M`
- compensation strength: `0.27`
- checkpoint policy: validation `accuracy` with `mode=max`
- evaluated checkpoint: `checkpoints/best.pt`
- execution policy: explicit `CUDA_VISIBLE_DEVICES=3`, single GPU only

## Per-Seed Results

| Seed | Best Epoch | Test Accuracy | Test F1 | Test Loss |
| --- | ---: | ---: | ---: | ---: |
| 42 | 2 | 0.8555 | 0.8477 | 0.5404 |
| 43 | 2 | 0.8438 | 0.8276 | 0.4963 |
| 44 | 3 | 0.8320 | 0.8054 | 0.4575 |

## Three-Seed Summary

| Metric | Mean | Std |
| --- | ---: | ---: |
| Accuracy | 0.8438 | 0.0117 |
| F1 | 0.8269 | 0.0212 |
| Loss | 0.4981 | 0.0415 |

## Comparison Against Previous Last-Checkpoint Run

Previous enlarged hard-border formal run used the final checkpoint and selected by validation loss. Its three-seed summary was:

| Metric | Mean | Std |
| --- | ---: | ---: |
| Accuracy | 0.7969 | 0.2595 |
| F1 | 0.8515 | 0.1641 |
| Loss | 0.3396 | 0.3224 |

The accuracy-focused best-checkpoint policy removes the catastrophic seed-42 collapse and sharply reduces accuracy variance.

## Conclusion

Using validation accuracy to select `best.pt` is the right policy when the target metric is reported accuracy. It converts the enlarged hard-border branch from a high-variance result into a stable accuracy result across the three checked seeds.
