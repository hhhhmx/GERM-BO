# Pooled Per-class and Confusion Analysis: strict 3-mer-balanced splice benchmark

Protocol: average over pooled held-out seeds `50-59` for the two main DNABERT-2-based methods.

## Per-class mean metrics

| Method | Class | Precision | Recall | F1 | Mean predicted count |
|---|---:|---:|---:|---:|---:|
| LoRA attention.output + classifier | 0 | 0.3652 | 0.0535 | 0.0842 | 91.5 |
| LoRA attention.output + classifier | 1 | 0.3978 | 0.1757 | 0.1684 | 293.1 |
| LoRA attention.output + classifier | 2 | 0.3104 | 0.8135 | 0.4492 | 1415.4 |
| GERM-BO quantile [0.8,1.2] comp0.27 | 0 | 0.3742 | 0.3577 | 0.3121 | 593.2 |
| GERM-BO quantile [0.8,1.2] comp0.27 | 1 | 0.3379 | 0.2108 | 0.2233 | 354.9 |
| GERM-BO quantile [0.8,1.2] comp0.27 | 2 | 0.4104 | 0.5488 | 0.4380 | 851.9 |

## GERM-BO minus LoRA per-class delta

| Class | Precision Delta | Recall Delta | F1 Delta | Predicted Count Delta |
|---:|---:|---:|---:|---:|
| 0 | +0.0090 | +0.3042 | +0.2280 | +501.7 |
| 1 | -0.0599 | +0.0352 | +0.0549 | +61.8 |
| 2 | +0.0999 | -0.2647 | -0.0112 | -563.5 |

## Mean confusion matrix over pooled seeds

### LoRA attention.output + classifier

| True \\ Pred | 0 | 1 | 2 |
|---:|---:|---:|---:|
| 0 | 32.1 | 99.7 | 468.2 |
| 1 | 35.5 | 105.4 | 459.1 |
| 2 | 23.9 | 88.0 | 488.1 |

### GERM-BO quantile [0.8,1.2] comp0.27

| True \\ Pred | 0 | 1 | 2 |
|---:|---:|---:|---:|
| 0 | 214.6 | 129.0 | 256.4 |
| 1 | 207.3 | 126.5 | 266.2 |
| 2 | 171.3 | 99.4 | 329.3 |

## Main interpretation

Pooled over seeds `50-59`, GERM-BO still improves class balance relative to the strong LoRA baseline, but the additional seed block weakens the stability of class-0/class-1 gains. The pooled confusion matrices should therefore be read as support for a positive but not perfectly stable external effect.
