# Border-Medium GERM-BO Seed 46 Failure Analysis

Scope: `border_medium`, final GERM-BO `attention.output + classifier`, seed `46`, compared against successful GERM-BO seed `45` and baseline LoRA seed `46`.

## Key Finding

The seed-46 failure is a training/representation failure, not a threshold-tuning artifact.

Evidence:

| Run | Best epoch | Best val acc before threshold | Tuned val acc | Tuned test acc | Test F1 | Threshold |
|---|---:|---:|---:|---:|---:|---:|
| GERM-BO seed 46 | 0 | 0.6133 | 0.7031 | 0.6523 | 0.6642 | 0.4657 |
| GERM-BO seed 45 | 3 | 0.8906 | 0.9023 | 0.8945 | 0.8989 | 0.4741 |
| Baseline seed 46 | 2 | 0.8750 | 0.8984 | 0.8984 | 0.8984 | 0.4694 |

Seed 46's best checkpoint is already epoch `0`, with weak validation accuracy. Later epochs did not improve enough before early stopping. Threshold tuning raises validation accuracy from `0.6133` to `0.7031`, but cannot recover test performance because the model has not learned a separated decision boundary.

## Prediction Distribution

| Run | Label 0 prob mean +/- std | Label 1 prob mean +/- std | Probability range | Predicted labels | Test errors |
|---|---:|---:|---:|---:|---:|
| GERM-BO seed 46 | 0.4554 +/- 0.0266 | 0.4749 +/- 0.0281 | 0.3646-0.5209 | 119 zero / 137 one | 89 |
| GERM-BO seed 45 | 0.3200 +/- 0.1114 | 0.6566 +/- 0.1129 | 0.1037-0.8935 | 117 zero / 139 one | 27 |
| Baseline seed 46 | 0.3543 +/- 0.0843 | 0.5895 +/- 0.1018 | 0.1287-0.8885 | 128 zero / 128 one | 26 |

The failed run is not predicting a single class. Instead, it outputs poorly separated probabilities clustered near the threshold. The gap between class means is only `0.0195` for failed GERM-BO seed 46, compared with `0.3366` for successful GERM-BO seed 45 and `0.2353` for baseline seed 46.

## Subgroup Behavior

GERM-BO seed 46 accuracy by motif:

| Motif | n | Accuracy | Mean prob_1 |
|---|---:|---:|---:|
| AATAAT | 46 | 0.7174 | 0.4737 |
| ACGTGA | 44 | 0.6364 | 0.4567 |
| ATATAT | 39 | 0.6410 | 0.4750 |
| CGTACC | 42 | 0.6667 | 0.4491 |
| GACTTC | 42 | 0.5476 | 0.4603 |
| TATATA | 43 | 0.6977 | 0.4760 |

GERM-BO seed 46 accuracy by border score:

| Border score | n | Accuracy | Mean prob_1 |
|---|---:|---:|---:|
| 0.0 | 42 | 0.5476 | 0.4603 |
| 0.2 | 86 | 0.6512 | 0.4530 |
| 0.6 | 46 | 0.7174 | 0.4737 |
| 0.8 | 82 | 0.6707 | 0.4755 |

The failure is broad rather than restricted to a single high-border motif. The weakest subgroup is `GACTTC` / border score `0.0`, but high-border motifs are also poorly separated. This points to a bad optimization trajectory rather than a clean biological subgroup failure.

## Interpretation

The medium split exposes a stability issue in final GERM-BO under this seed. The adapter does not form a useful class-separating probability distribution before early stopping. Because baseline seed 46 trains normally and GERM-BO seed 45 trains normally, this is most likely an interaction between GERM-BO compensation, random initialization/optimization trajectory, and the medium task structure.

This should not be written as "GERM-BO fails on medium" yet. The correct statement is: the current final GERM-BO config has a seed-specific optimization failure on `border_medium`, and that failure dominates the 5-seed mean.

## Recommended Follow-Up

Run a targeted stabilization check on `border_medium` before drawing a conclusion:

1. Repeat final GERM-BO on `border_medium` with seeds `47-51` to see whether seed 46 is isolated.
2. Rerun seed `46` with `early_stopping_patience=4` to test whether the run can recover after a weak early trajectory.
3. Test a milder compensation strength on `border_medium`, e.g. `0.15` or `0.20`, for seeds `42-46`.
4. If the failure persists, report `border_medium` as a limitation/stability case and keep enlarged hard-border as the main result.
