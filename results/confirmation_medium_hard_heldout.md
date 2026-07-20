# Held-Out Confirmation: medium/hard Candidate Comparison

Protocol: held-out seeds `47-54`, real DNABERT-2 backbone, GERM-BO final `attention.output + classifier`, `early_stopping_patience=4`, validation-accuracy best checkpoint, validation-threshold tuned test evaluation. All train/eval commands used `CUDA_VISIBLE_DEVICES=3`.

## Summary

| Task | Candidate | Test Acc Mean +/- Std | Test F1 Mean +/- Std | Min Acc | Max Acc |
|---|---|---:|---:|---:|---:|
| border_medium | combined main candidate: comp=0.27, clip=[0.73,1.42], patience=4 | 0.9175 +/- 0.0168 | 0.9161 +/- 0.0180 | 0.8945 | 0.9375 |
| border_medium | medium-stabilized candidate: comp=0.15, clip=[0.85,1.30], patience=4 | 0.9116 +/- 0.0451 | 0.9138 +/- 0.0415 | 0.8164 | 0.9531 |
| border_hard | combined main candidate: comp=0.27, clip=[0.73,1.42], patience=4 | 0.8340 +/- 0.0453 | 0.8376 +/- 0.0471 | 0.7461 | 0.8828 |
| border_hard | medium-stabilized candidate: comp=0.15, clip=[0.85,1.30], patience=4 | 0.8379 +/- 0.0614 | 0.8409 +/- 0.0563 | 0.7031 | 0.8867 |

## Combined Across Medium+Hard

| Candidate | Runs | Test Acc Mean +/- Std | Test F1 Mean +/- Std | Min Acc | Max Acc |
|---|---:|---:|---:|---:|---:|
| combined main candidate: comp=0.27, clip=[0.73,1.42], patience=4 | 16 | 0.8757 +/- 0.0543 | 0.8768 +/- 0.0532 | 0.7461 | 0.9375 |
| medium-stabilized candidate: comp=0.15, clip=[0.85,1.30], patience=4 | 16 | 0.8748 +/- 0.0645 | 0.8774 +/- 0.0608 | 0.7031 | 0.9531 |

## Paired Delta: comp027 - comp015

| Task | Metric | Mean Delta | 95% CI | Win Rate comp027 | Per-Seed Delta |
|---|---|---:|---:|---:|---:|
| border_medium | test_accuracy | +0.0059 | [-0.0322, +0.0439] | 50.0% | -0.0273 / +0.0391 / +0.0781 / -0.0469 / -0.0312 / +0.0469 / +0.0156 / -0.0273 |
| border_medium | test_f1 | +0.0023 | [-0.0354, +0.0400] | 50.0% | -0.0262 / +0.0381 / +0.0675 / -0.0543 / -0.0379 / +0.0467 / +0.0131 / -0.0285 |
| border_hard | test_accuracy | -0.0039 | [-0.0775, +0.0697] | 37.5% | +0.0312 / -0.1055 / -0.0117 / -0.0781 / -0.0312 / +0.1758 / +0.0391 / -0.0508 |
| border_hard | test_f1 | -0.0033 | [-0.0751, +0.0685] | 37.5% | +0.0582 / -0.1065 / -0.0055 / -0.0835 / -0.0270 / +0.1579 / +0.0352 / -0.0554 |

## Interpretation

On held-out seeds, the higher combined mean test accuracy is from `combined main candidate: comp=0.27, clip=[0.73,1.42], patience=4` with mean `0.8757`. Because these are held-out confirmation seeds, this comparison is stronger evidence than the tuning grid, but it should still be reported as a candidate confirmation rather than a fully independent benchmark result.
