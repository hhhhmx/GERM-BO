# Enlarged Hard-Border Formal Revalidation

## Setting

- config: `configs/real_dnabert2_germ_bo_hard_border_large_comp027_formal.yaml`
- split: `data/splits_hard_border_large`
- split size: `1024 / 256 / 256`
- backbone: `DNABERT-2-117M`
- compensation strength: `0.27`
- execution policy: explicit `CUDA_VISIBLE_DEVICES=3`, single GPU only

This stage keeps the current best hard-border setting fixed and increases only the split size, so the effect being tested is data scale rather than a new hyperparameter search.

## Per-Seed Test Results

| Seed | Accuracy | F1 | Loss |
| --- | ---: | ---: | ---: |
| 42 | 0.5000 | 0.6667 | 0.6933 |
| 43 | 0.9805 | 0.9802 | 0.0623 |
| 44 | 0.9102 | 0.9076 | 0.2632 |

## Three-Seed Summary

| Metric | Mean | Std |
| --- | ---: | ---: |
| Accuracy | 0.7969 | 0.2595 |
| F1 | 0.8515 | 0.1641 |
| Loss | 0.3396 | 0.3224 |

## Interpretation

The enlarged hard-border split improves the upside of the branch substantially: two of the three seeds are now very strong, and the mean F1 remains high. However, the branch is still not fully stable because `seed=42` collapses to chance-level behavior even on the larger split.

So the larger split helps, but it does not fully eliminate seed sensitivity. This is a stronger task-specific result than before, yet it still falls short of a project-wide "fully robust" conclusion.

## Practical Conclusion

At this checkpoint:

- `0.27` remains the best hard-border configuration tested so far
- enlarging the split improved the branch's ceiling and average performance
- but a single catastrophic seed still exists, so the branch remains conditionally robust rather than universally stable

If this branch is carried further, the next most defensible step is not another compensation sweep. The bigger question now is why one seed still fails. The cleanest follow-ups would be:

- inspect train/val histories for the failing seed
- compare prediction distributions across seeds
- or add light stabilization such as early stopping or a smaller learning rate
