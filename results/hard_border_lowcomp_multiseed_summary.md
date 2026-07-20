# Hard-Border Lowcomp Multi-Seed Revalidation

## Setting

- config: `configs/real_dnabert2_germ_bo_hard_border_lowcomp_robust.yaml`
- task: `data/splits_hard_border`
- backbone: `DNABERT-2-117M`
- execution policy: explicit `CUDA_VISIBLE_DEVICES=3`, single GPU only
- seeds: `42`, `43`, `44`

## Per-Seed Test Results

| Seed | Accuracy | F1 | Loss |
| --- | ---: | ---: | ---: |
| 42 | 0.8984 | 0.8926 | 0.5179 |
| 43 | 0.5000 | 0.0000 | 0.7042 |
| 44 | 0.5000 | 0.0000 | 0.6946 |

## Three-Seed Summary

| Metric | Mean | Std |
| --- | ---: | ---: |
| Accuracy | 0.6328 | 0.2300 |
| F1 | 0.2975 | 0.5153 |
| Loss | 0.6389 | 0.1049 |

## Interpretation

The single best hard-border lowcomp run does not hold up cleanly under even a small three-seed check. The `seed=42` result is strong, but `seed=43` and `seed=44` both fall back to chance-level behavior. This means the current `lowcomp=0.2` setting is promising but still unstable on the present hard-border task.

The practical implication is that the hard-border branch should not yet be promoted to a formal default. If this branch remains important, the next most defensible step is to stabilize it before drawing method-level conclusions. The most direct options are:

- increase training budget on the hard-border split
- slightly widen the data split again
- run a tighter local sweep around `compensation_strength=0.2`
