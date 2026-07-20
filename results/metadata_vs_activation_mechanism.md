# Metadata-Driven vs Activation-Derived Compensation

Protocol: held-out seeds `47-54`, real DNABERT-2 backbone, same target modules, `compensation_strength=0.27`, `early_stopping_patience=4`, validation-accuracy best checkpoint, and validation-threshold tuned test evaluation. All train/eval commands must use `CUDA_VISIBLE_DEVICES=3`.

## Per-Task Summary

| Task | Variant | Test Acc Mean +/- Std | Test F1 Mean +/- Std | Min Acc | Max Acc |
|---|---|---:|---:|---:|---:|
| border_medium | metadata-driven comp=0.27/p4 | 0.9258 +/- 0.0652 | 0.9238 +/- 0.0675 | 0.7891 | 0.9961 |
| border_medium | activation-derived comp=0.27/p4 | 0.9175 +/- 0.0168 | 0.9161 +/- 0.0180 | 0.8945 | 0.9375 |
| border_medium | no compensation comp=0.00/p4 | 0.9077 +/- 0.0153 | 0.9092 +/- 0.0142 | 0.8867 | 0.9336 |
| border_hard | metadata-driven comp=0.27/p4 | 0.9287 +/- 0.0550 | 0.9264 +/- 0.0590 | 0.8359 | 0.9883 |
| border_hard | activation-derived comp=0.27/p4 | 0.8340 +/- 0.0453 | 0.8376 +/- 0.0471 | 0.7461 | 0.8828 |
| border_hard | no compensation comp=0.00/p4 | 0.8335 +/- 0.0816 | 0.8390 +/- 0.0687 | 0.6367 | 0.8945 |

## Combined Medium+Hard

| Variant | Runs | Test Acc Mean +/- Std | Test F1 Mean +/- Std | Min Acc | Max Acc |
|---|---:|---:|---:|---:|---:|
| metadata-driven comp=0.27/p4 | 16 | 0.9272 +/- 0.0583 | 0.9251 +/- 0.0613 | 0.7891 | 0.9961 |
| activation-derived comp=0.27/p4 | 16 | 0.8757 +/- 0.0543 | 0.8768 +/- 0.0532 | 0.7461 | 0.9375 |
| no compensation comp=0.00/p4 | 16 | 0.8706 +/- 0.0685 | 0.8741 +/- 0.0601 | 0.6367 | 0.9336 |
