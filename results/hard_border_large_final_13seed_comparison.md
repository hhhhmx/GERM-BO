# Final 13-Seed Comparison on Enlarged Hard-Border Split

Protocol: real DNABERT-2-117M backbone, enlarged hard-border split, seeds `42-54`, validation-accuracy best checkpoint, early stopping patience 2, and validation-threshold tuned test evaluation. New baseline runs for seeds `50-54` used explicit `CUDA_VISIBLE_DEVICES=3` and reported one visible GPU.

| Method | Target modules | Test accuracy mean +/- std | Test F1 mean +/- std | Per-seed test accuracy |
|---|---|---:|---:|---:|
| Baseline LoRA | matched LoRA targets | 0.8377 +/- 0.0544 | 0.8300 +/- 0.0725 | 0.8281 / 0.8477 / 0.8438 / 0.8828 / 0.7344 / 0.7305 / 0.8867 / 0.8516 / 0.8711 / 0.9102 / 0.7969 / 0.8555 / 0.8516 |
| GERM-BO final | attention.output.dense layer 0/1 + classifier | 0.8918 +/- 0.0255 | 0.8896 +/- 0.0276 | 0.9102 / 0.9219 / 0.8477 / 0.8984 / 0.9297 / 0.8906 / 0.9102 / 0.8633 / 0.9062 / 0.9023 / 0.8828 / 0.8555 / 0.8750 |

Paired statistics for GERM-BO final vs baseline:

| Metric | Value |
|---|---:|
| Mean accuracy delta | +0.0541 |
| Delta std | 0.0634 |
| Paired t-statistic | 3.0776 |
| Bootstrap 95% CI for mean delta | [+0.0240, +0.0898] |
| Win rate | 84.6% |
| Per-seed accuracy delta | +0.0820 / +0.0742 / +0.0039 / +0.0156 / +0.1953 / +0.1602 / +0.0234 / +0.0117 / +0.0352 / -0.0078 / +0.0859 / +0.0000 / +0.0234 |

Conclusion: with both methods evaluated on the same 13 seeds, GERM-BO final improves mean test accuracy by `+0.0541` over baseline LoRA and has lower variance (`0.0255` vs `0.0544`). The bootstrap confidence interval for the paired accuracy delta remains positive, supporting a robust improvement on this split.
