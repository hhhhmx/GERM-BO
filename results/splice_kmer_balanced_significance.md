# Statistical Significance: strict 3-mer-balanced splice benchmark

Protocol: paired comparison over held-out seeds `50-54` on the strict `3-mer-balanced` split. Metrics use validation-accuracy best checkpoint and argmax test evaluation. P-values are paired t-test normal approximation, exact Wilcoxon signed-rank test, and exact sign test. Bootstrap CIs use 20,000 paired bootstrap samples over mean deltas.

| Metric | Comparison | Mean A +/- Std | Mean B +/- Std | Delta | t-test p | Wilcoxon p | Sign p | Bootstrap 95% CI | Win Rate |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| test_accuracy | GERM-BO quantile [0.8,1.2] comp0.27_minus_LoRA attention.output + classifier | 0.3888 +/- 0.0233 | 0.3489 +/- 0.0081 | +0.0399 | 0.0000 | 0.0625 | 0.0625 | [+0.0251, +0.0541] | 100.0% |
| test_macro_f1 | GERM-BO quantile [0.8,1.2] comp0.27_minus_LoRA attention.output + classifier | 0.3580 +/- 0.0545 | 0.2405 +/- 0.0145 | +0.1176 | 0.0000 | 0.0625 | 0.0625 | [+0.0620, +0.1618] | 100.0% |
| test_accuracy | GERM-BO quantile [0.8,1.2] comp0.27_minus_GERM-BO comp=0 | 0.3888 +/- 0.0233 | 0.3489 +/- 0.0081 | +0.0399 | 0.0000 | 0.0625 | 0.0625 | [+0.0251, +0.0541] | 100.0% |
| test_macro_f1 | GERM-BO quantile [0.8,1.2] comp0.27_minus_GERM-BO comp=0 | 0.3580 +/- 0.0545 | 0.2405 +/- 0.0145 | +0.1176 | 0.0000 | 0.0625 | 0.0625 | [+0.0620, +0.1618] | 100.0% |
| test_accuracy | GERM-BO quantile [0.8,1.2] comp0.27_minus_Baseline LoRA full target set | 0.3888 +/- 0.0233 | 0.3578 +/- 0.0334 | +0.0310 | 0.0526 | 0.1875 | 0.3750 | [+0.0004, +0.0570] | 80.0% |
| test_macro_f1 | GERM-BO quantile [0.8,1.2] comp0.27_minus_Baseline LoRA full target set | 0.3580 +/- 0.0545 | 0.2344 +/- 0.0918 | +0.1236 | 0.0200 | 0.1875 | 0.3750 | [+0.0292, +0.2138] | 80.0% |
