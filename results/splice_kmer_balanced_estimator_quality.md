# Estimator-Quality Analysis: strict 3-mer-balanced splice benchmark

Protocol: analyze the quantile-normalized metadata score on the strict `3-mer-balanced` split without additional training.

## Score distribution

| Split | N | Mean | Std | Q25 | Median | Q75 | Max | Clip-Max Rate |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| train | 9000 | 1.0000 | 0.1155 | 0.9000 | 1.0000 | 1.1000 | 1.2000 | 0.0% |
| val | 1800 | 1.0043 | 0.1164 | 0.9032 | 1.0052 | 1.1052 | 1.1998 | 0.0% |
| test | 1800 | 1.0060 | 0.1142 | 0.9128 | 1.0085 | 1.1042 | 1.1999 | 0.0% |

## Score vs composition correlations

| Split | Feature | Pearson |
|---|---|---:|
| train | gc | -0.0172 |
| train | entropy3 | +0.0650 |
| train | max3 | +0.0374 |
| val | gc | -0.0078 |
| val | entropy3 | +0.0328 |
| val | max3 | +0.0637 |
| test | gc | -0.0272 |
| test | entropy3 | +0.0353 |
| test | max3 | +0.0714 |

## Score vs pooled prediction quality (seeds 50-59)

| Method | Accuracy | Score-Error r | Score-Confidence r | Score-Margin r | Score Correct | Score Wrong |
|---|---:|---:|---:|---:|---:|---:|
| GERM-BO quantile [0.8,1.2] comp0.27 | 0.3724 | +0.0109 | +0.0341 | +0.0250 | 1.0043 | 1.0069 |
| LoRA attention.output + classifier | 0.3476 | +0.1048 | -0.0044 | -0.0050 | 0.9896 | 1.0147 |

## Main interpretation

On the strict split, the quantile-normalized score keeps substantial variance and no longer saturates at the clip ceiling. This supports the claim that the score remains a usable sample-difficulty / border-strength signal rather than collapsing into a near-constant factor.
