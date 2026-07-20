# Target-Module Ablation on Enlarged Hard-Border Split

Protocol: DNABERT-2-117M backbone, enlarged hard-border file split, GERM-BO compensation strength 0.27, validation accuracy best checkpoint, early stopping patience 2, and validation-threshold tuned test evaluation. All remote runs used `CUDA_VISIBLE_DEVICES=3` with one visible GPU.

| Variant | Target modules | Test accuracy mean +/- std | Test F1 mean +/- std | Per-seed test accuracy | Per-seed test F1 | Mean threshold |
|---|---|---:|---:|---:|---:|---:|
| attention.output + classifier | layer0/1 attention.output.dense + classifier | 0.8932 +/- 0.0399 | 0.8935 +/- 0.0369 | 0.9102 / 0.9219 / 0.8477 | 0.9076 / 0.9213 / 0.8517 | 0.3693 |
| Wqkv + classifier | layer0/1 Wqkv + classifier | 0.8854 +/- 0.0197 | 0.8881 +/- 0.0155 | 0.8672 / 0.8828 / 0.9063 | 0.8741 / 0.8855 / 0.9048 | 0.5092 |
| Classifier only | classifier | 0.8737 +/- 0.0098 | 0.8735 +/- 0.0149 | 0.8750 / 0.8828 / 0.8633 | 0.8740 / 0.8881 / 0.8583 | 0.4340 |
| Wqkv + attention.output + classifier | layer0/1 Wqkv + layer0/1 attention.output.dense + classifier | 0.8620 +/- 0.0148 | 0.8600 +/- 0.0081 | 0.8555 / 0.8516 / 0.8789 | 0.8538 / 0.8571 / 0.8692 | 0.4584 |

Reference threshold-tuned baseline LoRA over seeds 42/43/44: test accuracy mean `0.8398 +/- 0.0103`, test F1 mean `0.8495 +/- 0.0152`.

Updated decision after 13-seed confirmation: `attention.output + classifier` is promoted to the final main configuration because it has both higher mean accuracy and lower variance than `Wqkv + classifier` across seeds 42-54. `Wqkv + classifier` is retained as a secondary ablation result. The previous full target-module choice is not optimal on this split; combining Wqkv and attention.output appears to interfere rather than add.
