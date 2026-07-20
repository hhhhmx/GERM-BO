# Seed-42 Failure Analysis on Enlarged Hard-Border Formal Run

## Scope

Analyzed the enlarged hard-border formal revalidation for:

- config: `configs/real_dnabert2_germ_bo_hard_border_large_comp027_formal.yaml`
- split: `data/splits_hard_border_large`
- seeds compared: `42`, `43`, `44`

The goal was to inspect:

- the train/validation curve for the failing `seed=42`
- the prediction distribution on the test set
- how the failing seed differs from the stronger seeds

## Main Finding

`seed=42` does not fail because it learns the wrong pattern family in a nuanced way. It fails because the final checkpoint collapses into an almost constant classifier.

On the test set:

- `seed=42` predicts class `1` for all `256` samples
- the mean predicted probability for class `1` is effectively identical for both true classes:
  - true label `0`: `mean(prob_1)=0.5085`
  - true label `1`: `mean(prob_1)=0.5085`

So the final model is nearly indifferent to the input and emits a weak constant bias toward class `1`.

By contrast:

- `seed=43` prediction counts are balanced: `0:131`, `1:125`
- `seed=44` prediction counts are balanced: `0:135`, `1:121`
- their class-conditional mean probabilities are well separated:
  - `seed=43`: true `0` -> `prob_1=0.0333`, true `1` -> `prob_1=0.9514`
  - `seed=44`: true `0` -> `prob_1=0.0958`, true `1` -> `prob_1=0.8484`

## Validation-Curve Diagnosis

The validation history for `seed=42` is the clearest clue:

| Epoch | Accuracy | F1 | Loss |
| --- | ---: | ---: | ---: |
| 0 | 0.5156 | 0.0606 | 0.6785 |
| 1 | 0.6719 | 0.7273 | 0.6349 |
| 2 | 0.8516 | 0.8403 | 0.5529 |
| 3 | 0.5000 | 0.0000 | 0.7989 |
| 4 | 0.5000 | 0.0000 | 0.6949 |
| 5 | 0.5000 | 0.0000 | 0.6998 |
| 6 | 0.5000 | 0.0000 | 0.6942 |
| 7 | 0.5000 | 0.0000 | 0.6932 |
| 8 | 0.5000 | 0.6667 | 0.6933 |
| 9 | 0.5000 | 0.6667 | 0.6938 |
| 10 | 0.5000 | 0.6667 | 0.6937 |
| 11 | 0.5000 | 0.6667 | 0.6933 |

This means:

- the run was healthy through epoch `2`
- the model then collapsed sharply at epoch `3`
- it never recovered meaningful separation afterward
- the final checkpoint is much worse than the best validation point inside the same run

## Practical Diagnosis

The biggest engineering issue is not only seed sensitivity. It is also checkpoint policy.

The current training loop overwrites a single `debug_last.pt` checkpoint and does not preserve the best validation epoch. For `seed=42`, this means the repository kept only the collapsed final model, even though the same run had a strong intermediate validation point at epoch `2`.

So the failure has two layers:

- optimization instability can push some seeds into late-training collapse
- the current checkpoint policy guarantees that such collapse is retained if it happens near the end

## Actionable Implication

The next most justified stabilization step is:

1. save the best-validation checkpoint instead of only the final checkpoint
2. optionally add early stopping based on validation loss or validation F1

That change is more justified now than another compensation sweep, because the failing seed already showed a good intermediate solution before the final model deteriorated.
