# Mechanism Ablation and Failure Analysis

This report separates mechanism evidence from tuning evidence. The no-compensation control uses the same GERM-BO wrapper, target modules, rank, dropout, patience, and held-out seeds, but sets `compensation_strength=0` and clamps compensation to 1.0.

## Compensation Mechanism: Held-Out Seeds 47-54

| Task | Variant | Test Acc Mean +/- Std | Test F1 Mean +/- Std | Min Acc | Collapse Count Acc<0.75 |
|---|---|---:|---:|---:|---:|
| border_medium | no compensation: comp=0.00, clip=[1.00,1.00], p4 | 0.9077 +/- 0.0153 | 0.9092 +/- 0.0142 | 0.8867 | 0 |
| border_medium | medium-stabilized: comp=0.15, clip=[0.85,1.30], p4 | 0.9116 +/- 0.0451 | 0.9138 +/- 0.0415 | 0.8164 | 0 |
| border_medium | combined main: comp=0.27, clip=[0.73,1.42], p4 | 0.9175 +/- 0.0168 | 0.9161 +/- 0.0180 | 0.8945 | 0 |
| border_hard | no compensation: comp=0.00, clip=[1.00,1.00], p4 | 0.8335 +/- 0.0816 | 0.8390 +/- 0.0687 | 0.6367 | 1 |
| border_hard | medium-stabilized: comp=0.15, clip=[0.85,1.30], p4 | 0.8379 +/- 0.0614 | 0.8409 +/- 0.0563 | 0.7031 | 1 |
| border_hard | combined main: comp=0.27, clip=[0.73,1.42], p4 | 0.8340 +/- 0.0453 | 0.8376 +/- 0.0471 | 0.7461 | 1 |

## Combined Medium+Hard

| Variant | Runs | Test Acc Mean +/- Std | Test F1 Mean +/- Std | Min Acc | Collapse Count Acc<0.75 |
|---|---:|---:|---:|---:|---:|
| no compensation: comp=0.00, clip=[1.00,1.00], p4 | 16 | 0.8706 +/- 0.0685 | 0.8741 +/- 0.0601 | 0.6367 | 1 |
| medium-stabilized: comp=0.15, clip=[0.85,1.30], p4 | 16 | 0.8748 +/- 0.0645 | 0.8774 +/- 0.0608 | 0.7031 | 1 |
| combined main: comp=0.27, clip=[0.73,1.42], p4 | 16 | 0.8757 +/- 0.0543 | 0.8768 +/- 0.0532 | 0.7461 | 1 |

## Failure-Analysis Conclusion

On `border_medium`, compensation improves held-out mean accuracy from 0.9077 without compensation to 0.9175 with the main `comp=0.27/p4` setting. On `border_hard`, the no-compensation control reaches 0.8335, while `comp=0.27/p4` reaches 0.8340. This indicates that the compensation mechanism is most useful for the medium setting, while hard-task robustness is more sensitive and does not monotonically benefit from stronger compensation.

## Practical Failure Solution

The observed collapse is best handled by a conservative training protocol: monitor validation accuracy, save `best.pt`, use `early_stopping_patience=4`, and flag runs with weak validation accuracy or test-time probability collapse for rerun/diagnosis. The main config remains `comp=0.27/p4`; `comp=0.15/p4` is retained as a stability ablation.

## Current Main Recommendation

Keep `comp=0.27/p4` as the combined main configuration because it has the best tuning-stage validation score and the highest held-out combined accuracy among the compensation candidates (0.8757). Report `comp=0.15/p4` as a medium-stabilized robustness ablation rather than replacing the main configuration.
