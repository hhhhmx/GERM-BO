# Splice Strict 3-mer-Balanced Pooled Summary Seeds 50-59

Protocol: pooled held-out analysis on the strict `3-mer-balanced` split, combining seeds `50-54` and `55-59` for the two main methods under the same single-GPU training budget with explicit `CUDA_VISIBLE_DEVICES=3`.

## Summary

| Method | Seeds | Test Acc Mean +/- Std | Test Macro-F1 Mean +/- Std | Per-Seed Acc |
|---|---:|---:|---:|---|
| LoRA attention.output + classifier | 10 | 0.3476 +/- 0.0081 | 0.2339 +/- 0.0282 | 0.3383 / 0.3533 / 0.3539 / 0.3422 / 0.3567 / 0.3572 / 0.3333 / 0.3439 / 0.3500 / 0.3467 |
| GERM-BO quantile [0.8,1.2] comp0.27 | 10 | 0.3724 +/- 0.0302 | 0.3245 +/- 0.0715 | 0.3606 / 0.4189 / 0.3728 / 0.3883 / 0.4033 / 0.3567 / 0.4061 / 0.3361 / 0.3422 / 0.3394 |

## Paired Deltas

| Metric | Delta Mean | t-test p | Wilcoxon p | Sign p | Bootstrap 95% CI | Win Rate | Per-Seed Delta |
|---|---:|---:|---:|---:|---:|---:|---|
| test_accuracy | +0.0249 | 0.0115 | 0.0781 | 0.7539 | [+0.0072, +0.0434] | 60.0% | +0.0222 / +0.0656 / +0.0189 / +0.0461 / +0.0467 / -0.0006 / +0.0728 / -0.0078 / -0.0078 / -0.0072 |
| test_macro_f1 | +0.0906 | 0.0008 | 0.0137 | 0.1094 | [+0.0396, +0.1392] | 80.0% | +0.0168 / +0.1542 / +0.0894 / +0.1703 / +0.1571 / +0.0563 / +0.2075 / +0.1124 / -0.0083 / -0.0501 |

## Main interpretation

Pooled over seeds `50-59`, GERM-BO remains better in mean than the strong LoRA baseline: accuracy delta `+0.0249` and macro-F1 delta `+0.0906`. Bootstrap intervals stay positive for both metrics, but the exact non-parametric tests are now more conservative because the second held-out block contains several weaker seeds. The most accurate claim is therefore that the strict-split external result is positive in pooled mean and bootstrap CI, but only partially stable across held-out seed blocks.
