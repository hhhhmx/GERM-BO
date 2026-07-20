# Cross-Backbone Strict Splice (Label-Free Estimator, Seeds 50--54)

Protocol: strict `3-mer-balanced` splice split, train-quantile center-window k-mer JSD metadata, quantile clip `[0.8,1.2]`, compensation `0.27`, seeds `50-54`. Tests whether GERM-BO gains transfer beyond DNABERT-2 under label-free border estimation.

## DNABERT-2

| Method | Seeds | Test Acc Mean +/- Std | Test Macro-F1 Mean +/- Std | Per-Seed Acc |
|---|---:|---:|---:|---|
| LoRA | 5 | 0.3489 +/- 0.0081 | 0.2405 +/- 0.0145 | 0.3383 / 0.3533 / 0.3539 / 0.3422 / 0.3567 |
| GERM-BO quantile | 5 | 0.3888 +/- 0.0233 | 0.3580 +/- 0.0545 | 0.3606 / 0.4189 / 0.3728 / 0.3883 / 0.4033 |

## NT v2 50M

| Method | Seeds | Test Acc Mean +/- Std | Test Macro-F1 Mean +/- Std | Per-Seed Acc |
|---|---:|---:|---:|---|
| LoRA | 5 | 0.6447 +/- 0.0865 | 0.6393 +/- 0.0859 | 0.7006 / 0.7383 / 0.5272 / 0.6717 / 0.5856 |
| GERM-BO quantile | 5 | 0.6737 +/- 0.0837 | 0.6700 +/- 0.0857 | 0.6894 / 0.7467 / 0.5333 / 0.6728 / 0.7261 |

## HyenaDNA tiny

| Method | Seeds | Test Acc Mean +/- Std | Test Macro-F1 Mean +/- Std | Per-Seed Acc |
|---|---:|---:|---:|---|
| LoRA | 5 | 0.6088 +/- 0.0249 | 0.6031 +/- 0.0277 | 0.6006 / 0.5750 / 0.6039 / 0.6406 / 0.6239 |
| GERM-BO quantile | 5 | 0.6063 +/- 0.0214 | 0.6007 +/- 0.0248 | 0.5928 / 0.5778 / 0.6078 / 0.6289 / 0.6244 |

## Paired Deltas (GERM-BO minus LoRA)

| Backbone | Metric | Delta Mean | Bootstrap 95% CI | Win Rate | Per-Seed Delta |
|---|---|---:|---:|---:|---|
| DNABERT-2 | test_accuracy | +0.0399 | [+0.0257, +0.0541] | 100% | +0.0222 / +0.0656 / +0.0189 / +0.0461 / +0.0467 |
| DNABERT-2 | test_macro_f1 | +0.1176 | [+0.0620, +0.1618] | 100% | +0.0168 / +0.1542 / +0.0894 / +0.1703 / +0.1571 |
| NT v2 50M | test_accuracy | +0.0290 | [-0.0038, +0.0862] | 80% | -0.0111 / +0.0083 / +0.0061 / +0.0011 / +0.1406 |
| NT v2 50M | test_macro_f1 | +0.0307 | [-0.0065, +0.0948] | 80% | -0.0140 / +0.0076 / +0.0019 / +0.0013 / +0.1568 |
| HyenaDNA tiny | test_accuracy | -0.0024 | [-0.0078, +0.0028] | 60% | -0.0078 / +0.0028 / +0.0039 / -0.0117 / +0.0006 |
| HyenaDNA tiny | test_macro_f1 | -0.0024 | [-0.0085, +0.0036] | 60% | -0.0100 / +0.0051 / +0.0035 / -0.0118 / +0.0010 |
