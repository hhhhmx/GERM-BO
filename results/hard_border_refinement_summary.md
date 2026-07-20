# Hard-Border Local Refinement Around 0.25

## Goal

After the earlier stabilization sweep, the best local region had moved from `0.2` to around `0.25`. This refinement stage tested whether a narrower neighborhood around `0.25` would produce a better and more stable point.

All runs kept the same higher-budget setup:

- dataset: `data/splits_hard_border`
- backbone: `DNABERT-2-117M`
- target modules: first two attention blocks plus `classifier`
- `epochs: 12`
- `lr: 3e-4`
- explicit `CUDA_VISIBLE_DEVICES=3`
- single GPU only

## Seed-42 Local Comparison

| Compensation | Accuracy | F1 | Loss |
| --- | ---: | ---: | ---: |
| 0.23 | 0.7656 | 0.6939 | 0.5813 |
| 0.25 | 0.8906 | 0.8793 | 0.3667 |
| 0.27 | 0.8828 | 0.8819 | 0.3084 |

Interpretation:

`0.23` is clearly below the local optimum region. `0.25` and `0.27` are both strong, but `0.27` improves loss and slightly improves F1 relative to `0.25`, while accuracy is only marginally lower on the initial seed.

## Three-Seed Check for `0.27`

Config:

- `configs/real_dnabert2_germ_bo_hard_border_comp027_stabilize.yaml`

| Seed | Accuracy | F1 | Loss |
| --- | ---: | ---: | ---: |
| 42 | 0.8828 | 0.8819 | 0.3084 |
| 43 | 0.9063 | 0.9063 | 0.4364 |
| 44 | 0.8359 | 0.8037 | 0.4126 |

| Metric | Mean | Std |
| --- | ---: | ---: |
| Accuracy | 0.8750 | 0.0358 |
| F1 | 0.8640 | 0.0536 |
| Loss | 0.3858 | 0.0681 |

## Comparison Against `0.25`

Earlier `0.25` three-seed summary:

| Metric | Mean | Std |
| --- | ---: | ---: |
| Accuracy | 0.7682 | 0.2188 |
| F1 | 0.8140 | 0.1216 |
| Loss | 0.4617 | 0.1993 |

Interpretation:

The local refinement stage identifies `0.27` as a stronger hard-border setting than `0.25` under the current higher-budget setup. It improves the mean metrics and sharply reduces variance across seeds.

## Practical Conclusion

The hard-border branch is now much cleaner than before:

- `0.2` should be discarded for the higher-budget hard-border setting
- `0.25` was a useful stepping stone but is no longer the best local point
- `0.27` is the current best hard-border candidate and is substantially more stable than `0.25`

This is still a task-specific branch result rather than a project-wide default. But if the hard-border task is kept as a serious ablation or auxiliary benchmark, `0.27` is now the right setting to carry forward.
