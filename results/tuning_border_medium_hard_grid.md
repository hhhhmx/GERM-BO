# Failure-Driven Tuning Grid: border_medium and border_hard

Protocol: real DNABERT-2 backbone, GERM-BO final `attention.output + classifier`, `early_stopping_patience=4`, seeds `42-46`, validation-accuracy best checkpoint, validation-threshold tuned test evaluation. All train/eval commands used `CUDA_VISIBLE_DEVICES=3`.

## Per-Task Summary

| Task | Config | Selection Score | Val Acc Mean +/- Std | Test Acc Mean +/- Std | Test F1 Mean +/- Std | Min Acc | Max Acc |
|---|---|---:|---:|---:|---:|---:|---:|
| border_medium | comp=0.15, clip=[0.85,1.30], patience=4 | 0.8964 | 0.9055 +/- 0.0182 | 0.9070 +/- 0.0218 | 0.9077 +/- 0.0203 | 0.8750 | 0.9336 |
| border_medium | comp=0.20, clip=[0.80,1.35], patience=4 | 0.8798 | 0.8953 +/- 0.0309 | 0.8992 +/- 0.0476 | 0.9023 +/- 0.0423 | 0.8203 | 0.9492 |
| border_medium | comp=0.25, clip=[0.75,1.40], patience=4 | 0.8252 | 0.8531 +/- 0.0559 | 0.8484 +/- 0.0829 | 0.8445 +/- 0.0931 | 0.7305 | 0.9219 |
| border_medium | comp=0.27, clip=[0.73,1.42], patience=4 | 0.8865 | 0.9008 +/- 0.0285 | 0.8930 +/- 0.0557 | 0.8989 +/- 0.0497 | 0.8242 | 0.9609 |
| border_hard | comp=0.15, clip=[0.85,1.30], patience=4 | 0.8598 | 0.8727 +/- 0.0257 | 0.8469 +/- 0.0173 | 0.8505 +/- 0.0196 | 0.8281 | 0.8633 |
| border_hard | comp=0.20, clip=[0.80,1.35], patience=4 | 0.8916 | 0.8938 +/- 0.0043 | 0.8609 +/- 0.0278 | 0.8566 +/- 0.0308 | 0.8242 | 0.8945 |
| border_hard | comp=0.25, clip=[0.75,1.40], patience=4 | 0.8641 | 0.8828 +/- 0.0375 | 0.8516 +/- 0.0390 | 0.8491 +/- 0.0428 | 0.7969 | 0.8945 |
| border_hard | comp=0.27, clip=[0.73,1.42], patience=4 | 0.8903 | 0.9000 +/- 0.0195 | 0.8695 +/- 0.0202 | 0.8736 +/- 0.0188 | 0.8477 | 0.9023 |

## Combined Medium+Hard Summary

| Config | Runs | Selection Score | Val Acc Mean +/- Std | Test Acc Mean +/- Std | Test F1 Mean +/- Std | Min Acc | Max Acc |
|---|---:|---:|---:|---:|---:|---:|---:|
| comp=0.15, clip=[0.85,1.30], patience=4 | 10 | 0.8755 | 0.8891 +/- 0.0272 | 0.8770 +/- 0.0367 | 0.8791 +/- 0.0355 | 0.8281 | 0.9336 |
| comp=0.20, clip=[0.80,1.35], patience=4 | 10 | 0.8841 | 0.8945 +/- 0.0208 | 0.8801 +/- 0.0420 | 0.8794 +/- 0.0424 | 0.8203 | 0.9492 |
| comp=0.25, clip=[0.75,1.40], patience=4 | 10 | 0.8442 | 0.8680 +/- 0.0475 | 0.8500 +/- 0.0611 | 0.8468 +/- 0.0684 | 0.7305 | 0.9219 |
| comp=0.27, clip=[0.73,1.42], patience=4 | 10 | 0.8889 | 0.9004 +/- 0.0230 | 0.8812 +/- 0.0414 | 0.8863 +/- 0.0379 | 0.8242 | 0.9609 |

## Provisional Selection

Using the pre-specified validation score `val_accuracy_mean - 0.5 * val_accuracy_std`, the provisional best combined configuration is `comp=0.27, clip=[0.73,1.42], patience=4` with score `0.8889`. This should be treated as tuning-stage evidence only; a final claim should use held-out seeds.
