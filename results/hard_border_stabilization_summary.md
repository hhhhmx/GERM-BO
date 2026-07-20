# Hard-Border Stabilization Follow-Up

## Goal

This follow-up was designed to stabilize the previously promising but unstable `hard_border` branch.

The sequence of actions was:

1. increase training budget for the earlier `compensation_strength=0.2` setting
2. if that still failed, run a narrow grid around `0.2`

All runs kept the same core setup:

- dataset: `data/splits_hard_border`
- backbone: `DNABERT-2-117M`
- target modules: first two attention blocks plus `classifier`
- execution policy: explicit `CUDA_VISIBLE_DEVICES=3`, single GPU only

## High-Budget `0.2` Revalidation

Config:

- `configs/real_dnabert2_germ_bo_hard_border_lowcomp_stabilize.yaml`

Changes relative to the earlier robustness batch:

- `epochs: 12`
- `lr: 3e-4`

### Per-Seed Results

| Seed | Accuracy | F1 | Loss |
| --- | ---: | ---: | ---: |
| 42 | 0.5000 | 0.0000 | 0.6960 |
| 43 | 0.5000 | 0.0000 | 0.7094 |
| 44 | 0.5000 | 0.0000 | 0.8939 |

### Three-Seed Summary

| Metric | Mean | Std |
| --- | ---: | ---: |
| Accuracy | 0.5000 | 0.0000 |
| F1 | 0.0000 | 0.0000 |
| Loss | 0.7664 | 0.1106 |

Interpretation:

Increasing the training budget did not stabilize the earlier `0.2` candidate. In fact, under this higher-budget setting, the branch collapsed consistently across all three seeds.

## Narrow Grid Around `0.2`

### Single-Seed `0.15`

Config:

- `configs/real_dnabert2_germ_bo_hard_border_comp015_stabilize.yaml`

| Seed | Accuracy | F1 | Loss |
| --- | ---: | ---: | ---: |
| 42 | 0.5313 | 0.2500 | 0.6931 |

Interpretation:

`0.15` is too weak on the current hard-border task under the higher-budget setting.

### Three-Seed `0.25`

Config:

- `configs/real_dnabert2_germ_bo_hard_border_comp025_stabilize.yaml`

| Seed | Accuracy | F1 | Loss |
| --- | ---: | ---: | ---: |
| 42 | 0.8906 | 0.8793 | 0.3667 |
| 43 | 0.8984 | 0.8889 | 0.3277 |
| 44 | 0.5156 | 0.6737 | 0.6908 |

| Metric | Mean | Std |
| --- | ---: | ---: |
| Accuracy | 0.7682 | 0.2188 |
| F1 | 0.8140 | 0.1216 |
| Loss | 0.4617 | 0.1993 |

Interpretation:

`0.25` is clearly better than both `0.15` and the high-budget `0.2` branch. Two seeds are strong, while one seed still degrades sharply. So this is the best current hard-border candidate, but it is not yet fully stable.

## Practical Conclusion

The hard-border branch is now better understood:

- raising training budget does not rescue `compensation_strength=0.2`
- the locally best region shifts upward toward `0.25`
- `0.25` is currently the strongest hard-border candidate under the higher-budget setup
- however, the remaining seed sensitivity means this branch still should not be promoted to the project-wide default

If this line remains important, the next defensible step is to continue local refinement around `0.25`, for example:

- `0.23 / 0.25 / 0.27`
- or a slightly larger hard-border split with the same `0.25` setting
