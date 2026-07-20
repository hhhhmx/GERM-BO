# Splice Sites All Larger Estimator-Quality Analysis

Goal: diagnose why the non-oracle metadata estimator `center-JSD w64/k3/top10/scale3` does not produce stable GERM-BO gains on the external splice-site benchmark. This analysis uses no additional training.

## Score Distribution by Raw Class

| Split | Label | N | Mean | Std | Q25 | Median | Q75 | Max-Clip Rate |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| train | 0 | 3000 | 1.4999 | 0.0028 | 1.5000 | 1.5000 | 1.5000 | 100.0% |
| train | 1 | 3000 | 1.4999 | 0.0044 | 1.5000 | 1.5000 | 1.5000 | 100.0% |
| train | 2 | 3000 | 1.4990 | 0.0208 | 1.5000 | 1.5000 | 1.5000 | 99.6% |
| val | 0 | 600 | 1.5000 | 0.0000 | 1.5000 | 1.5000 | 1.5000 | 100.0% |
| val | 1 | 600 | 1.5000 | 0.0000 | 1.5000 | 1.5000 | 1.5000 | 100.0% |
| val | 2 | 600 | 1.4993 | 0.0125 | 1.5000 | 1.5000 | 1.5000 | 99.7% |
| test | 0 | 1000 | 1.5000 | 0.0000 | 1.5000 | 1.5000 | 1.5000 | 100.0% |
| test | 1 | 1000 | 1.5000 | 0.0000 | 1.5000 | 1.5000 | 1.5000 | 100.0% |
| test | 2 | 1000 | 1.4997 | 0.0078 | 1.5000 | 1.5000 | 1.5000 | 99.8% |

## Score vs Sequence-Composition Correlations

| Split | Feature | Pearson | Spearman |
|---|---|---:|---:|
| train | gc | -0.0396 | -0.0278 |
| train | entropy3 | +0.2266 | +0.0633 |
| train | max3 | -0.1260 | -0.0604 |
| train | cpg | -0.0178 | -0.0118 |
| train | gt_ag_center | -0.0083 | +0.0306 |
| val | gc | -0.0185 | +0.0027 |
| val | entropy3 | +0.1414 | +0.0574 |
| val | max3 | -0.0725 | -0.0540 |
| val | cpg | +0.0093 | +0.0129 |
| val | gt_ag_center | -0.0443 | -0.0489 |
| test | gc | -0.0322 | -0.0298 |
| test | entropy3 | +0.1281 | +0.0445 |
| test | max3 | -0.0731 | -0.0431 |
| test | cpg | -0.0199 | -0.0120 |
| test | gt_ag_center | +0.0579 | +0.0445 |

## Score vs Prediction Quality

| Method | Accuracy | Score-Error r | Score-Error rho | Score-Confidence r | Score-Margin r | Score Correct | Score Wrong |
|---|---:|---:|---:|---:|---:|---:|---:|
| baseline_lora | 0.3853 | +0.0068 | +0.0061 | -0.0047 | -0.0055 | 1.4998 | 1.4999 |
| germ_bo_w64k3 | 0.3995 | +0.0105 | +0.0106 | -0.0044 | -0.0059 | 1.4998 | 1.4999 |

## Accuracy by Score Quantile Bin

| Method | Score Bin | N Predictions | Score Range | Accuracy | Confidence | Margin |
|---|---|---:|---|---:|---:|---:|
| baseline_lora | low | 5 | 1.3022-1.3022 | 0.6000 | 0.4700 | 0.1790 |
| baseline_lora | mid_low | 5 | 1.3521-1.3521 | 0.4000 | 0.4086 | 0.0846 |
| baseline_lora | mid_high | 14990 | 1.5000-1.5000 | 0.3853 | 0.4291 | 0.1114 |
| baseline_lora | high | 0 | 0.0000-0.0000 | 0.0000 | 0.0000 | 0.0000 |
| germ_bo_w64k3 | low | 5 | 1.3022-1.3022 | 0.6000 | 0.4554 | 0.1566 |
| germ_bo_w64k3 | mid_low | 5 | 1.3521-1.3521 | 0.6000 | 0.4262 | 0.1279 |
| germ_bo_w64k3 | mid_high | 14990 | 1.5000-1.5000 | 0.3994 | 0.4263 | 0.1089 |
| germ_bo_w64k3 | high | 0 | 0.0000-0.0000 | 0.0000 | 0.0000 | 0.0000 |

## Interpretation

- If score is useful as a border-difficulty estimator, it should show a meaningful relationship with error rate, confidence/margin, or class-specific difficulty.
- If score is mostly saturated at the clip maximum or highly correlated with simple k-mer composition, it is likely acting as a weak composition proxy rather than a precise boundary-quality signal.
- This analysis should be read together with the full comparison table, where simple 3-mer Logistic Regression and Linear SVM outperform DNABERT-2 LoRA/GERM-BO on this split.
