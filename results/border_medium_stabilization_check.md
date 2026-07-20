# Border-Medium Stabilization Check

Purpose: determine whether the original `border_medium` GERM-BO seed `46` failure is an isolated optimization failure or evidence of systematic instability.

Protocol: real DNABERT-2-117M backbone, `border_medium` split, validation-accuracy best checkpoint, validation-threshold tuned test evaluation, explicit `CUDA_VISIBLE_DEVICES=3`, one visible GPU.

## Additional Seeds

| Run group | Seeds | Accuracy mean +/- std | F1 mean +/- std | Per-seed accuracy |
|---|---|---:|---:|---:|
| Original final GERM-BO | 42/43/44/45/46 | 0.8227 +/- 0.0987 | 0.8318 +/- 0.0964 | 0.8242 / 0.8789 / 0.8633 / 0.8945 / 0.6523 |
| Additional final GERM-BO | 47/48/49/50/51 | 0.8961 +/- 0.0165 | 0.8943 +/- 0.0165 | 0.9141 / 0.8711 / 0.8906 / 0.9062 / 0.8984 |
| Final GERM-BO combined | 42-51 | 0.8594 +/- 0.0771 | 0.8630 +/- 0.0731 | 0.8242 / 0.8789 / 0.8633 / 0.8945 / 0.6523 / 0.9141 / 0.8711 / 0.8906 / 0.9062 / 0.8984 |

The additional seeds do not reproduce the seed-46 collapse. Seeds `47-51` are all between `0.8711` and `0.9141`, with low variance.

## Seed-46 Recovery Tests

| Seed-46 variant | Test accuracy | Test F1 | Validation accuracy | Threshold |
|---|---:|---:|---:|---:|
| Original final config | 0.6523 | 0.6642 | 0.7031 | 0.4657 |
| Same config, early stopping patience 4 | 0.9609 | 0.9597 | 0.9336 | 0.3852 |
| compensation_strength 0.15 | 0.9141 | 0.9098 | 0.9023 | 0.4796 |
| compensation_strength 0.20 | 0.9141 | 0.9160 | 0.8750 | 0.4415 |

Both stabilization strategies recover seed 46. Longer patience gives the strongest single-seed recovery, suggesting that the original seed-46 failure was caused by a weak early trajectory and overly aggressive early stopping rather than an inherent inability of GERM-BO to solve `border_medium`.

## Interpretation

The evidence favors "isolated optimization / early-stopping failure" over "systematic configuration failure":

- Seeds `47-51` with the original final config are stable and high-performing.
- Rerunning seed `46` with patience `4` recovers to `0.9609`.
- Rerunning seed `46` with milder compensation strengths `0.15` or `0.20` recovers to `0.9141`.
- The original seed-46 failure should be treated as a stability caveat, not as a definitive negative result for GERM-BO on `border_medium`.

Recommended reporting: keep the original 5-seed medium result in the appendix, but accompany it with this stabilization check. If `border_medium` is used in a main robustness table, either use a patience-4 protocol consistently or report that seed-sensitive early stopping can distort medium-task results.
