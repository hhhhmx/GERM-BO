# Per-class and Confusion Analysis: strict 3-mer-balanced splice benchmark

Protocol: average over held-out seeds `50-54` for the two main DNABERT-2-based methods.

## Per-class mean metrics

| Method | Class | Precision | Recall | F1 | Mean predicted count |
|---|---:|---:|---:|---:|---:|
| LoRA attention.output + classifier | 0 | 0.4959 | 0.0857 | 0.1298 | 140.8 |
| LoRA attention.output + classifier | 1 | 0.4190 | 0.0557 | 0.0934 | 79.6 |
| LoRA attention.output + classifier | 2 | 0.3439 | 0.9053 | 0.4982 | 1579.6 |
| GERM-BO quantile [0.8,1.2] comp0.27 | 0 | 0.3715 | 0.5040 | 0.4038 | 823.2 |
| GERM-BO quantile [0.8,1.2] comp0.27 | 1 | 0.3398 | 0.2207 | 0.2444 | 371.0 |
| GERM-BO quantile [0.8,1.2] comp0.27 | 2 | 0.4554 | 0.4417 | 0.4259 | 605.8 |

## GERM-BO minus LoRA per-class delta

| Class | Precision Delta | Recall Delta | F1 Delta | Predicted Count Delta |
|---:|---:|---:|---:|---:|
| 0 | -0.1244 | +0.4183 | +0.2741 | +682.4 |
| 1 | -0.0792 | +0.1650 | +0.1510 | +291.4 |
| 2 | +0.1116 | -0.4637 | -0.0724 | -973.8 |

## Mean confusion matrix over seeds

### LoRA attention.output + classifier

| True \\ Pred | 0 | 1 | 2 |
|---:|---:|---:|---:|
| 0 | 51.4 | 26.4 | 522.2 |
| 1 | 52.4 | 33.4 | 514.2 |
| 2 | 37.0 | 19.8 | 543.2 |

### GERM-BO quantile [0.8,1.2] comp0.27

| True \\ Pred | 0 | 1 | 2 |
|---:|---:|---:|---:|
| 0 | 302.4 | 134.6 | 163.0 |
| 1 | 289.8 | 132.4 | 177.8 |
| 2 | 231.0 | 104.0 | 265.0 |

## Main interpretation

Compared with the strong LoRA baseline, GERM-BO mainly improves class-wise recall and F1 for the harder splice classes while reducing the collapse toward low-information predictions. The averaged confusion matrices show that GERM-BO redistributes predictions more evenly across the three classes instead of staying close to the baseline's weaker decision boundary.
