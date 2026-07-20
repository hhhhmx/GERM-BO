# border_medium Stabilized GERM-BO Check

Configuration: GERM-BO final `attention.output + classifier`, `compensation_strength=0.27`, `early_stopping_patience=4`, real DNABERT-2 backbone, same `border_medium` split, seeds `42-46`. All train/eval commands used `CUDA_VISIBLE_DEVICES=3`.

## Main Result

| Method | Seeds | Test Accuracy Mean +/- Std | Test F1 Mean +/- Std | Min Acc | Max Acc |
|---|---:|---:|---:|---:|---:|
| Baseline LoRA | 5 | 0.8859 +/- 0.0271 | 0.8889 +/- 0.0258 | 0.8555 | 0.9258 |
| GERM-BO final, patience=2 original | 5 | 0.8227 +/- 0.0987 | 0.8318 +/- 0.0964 | 0.6523 | 0.8945 |
| GERM-BO final, patience=4 | 5 | 0.8930 +/- 0.0557 | 0.8989 +/- 0.0497 | 0.8242 | 0.9609 |

## Per-Seed Results

| Seed | Threshold | Val Acc | Test Acc | Test F1 | Pred 0 | Pred 1 | GPU |
|---:|---:|---:|---:|---:|---:|---:|---|
| 42 | 0.4851 | 0.8750 | 0.8242 | 0.8375 | 107 | 149 | CUDA_VISIBLE_DEVICES=3, visible=1 |
| 43 | 0.5129 | 0.8789 | 0.8789 | 0.8848 | 115 | 141 | CUDA_VISIBLE_DEVICES=3, visible=1 |
| 44 | 0.4517 | 0.8867 | 0.8633 | 0.8736 | 107 | 149 | CUDA_VISIBLE_DEVICES=3, visible=1 |
| 45 | 0.4310 | 0.9297 | 0.9375 | 0.9389 | 122 | 134 | CUDA_VISIBLE_DEVICES=3, visible=1 |
| 46 | 0.3852 | 0.9336 | 0.9609 | 0.9597 | 136 | 120 | CUDA_VISIBLE_DEVICES=3, visible=1 |

## Interpretation

Increasing patience from 2 to 4 removes the seed-46 collapse: accuracy improves from 0.6523 to 0.9609. The stabilized 5-seed mean accuracy is 0.8930, which is +0.0070 versus Baseline LoRA on the same five seeds. This supports treating the earlier medium-task failure as an optimization/early-stopping instability rather than a structural negative result for the adapter.
