# Splice Estimator-Quality Grid Summary

Estimator-only grid. No model training was run. Ranking heuristic favors score variation and prediction-quality association, while penalizing score clipping and strong composition-proxy behavior.

## Top 20 Estimators

| Rank | Tag | Score Std | Clip Rate | Error r Base | Error r GERM | Margin r Base | Entropy r | GC r | Quality |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | w48_k2_t025_train_quantile_r07_13 | 0.1687 | 0.0% | +0.0594 | +0.0182 | +0.0182 | +0.0534 | -0.0156 | +0.2017 |
| 2 | w48_k2_t05_train_quantile_r07_13 | 0.1687 | 0.0% | +0.0606 | +0.0190 | +0.0141 | +0.0542 | -0.0156 | +0.2001 |
| 3 | w48_k2_t10_train_quantile_r07_13 | 0.1689 | 0.0% | +0.0598 | +0.0208 | +0.0076 | +0.0592 | -0.0163 | +0.1963 |
| 4 | w64_k2_t025_train_quantile_r07_13 | 0.1688 | 0.0% | +0.0423 | +0.0067 | +0.0270 | +0.0249 | +0.0132 | +0.1897 |
| 5 | w64_k2_t05_train_quantile_r07_13 | 0.1687 | 0.0% | +0.0446 | +0.0073 | +0.0247 | +0.0252 | +0.0109 | +0.1890 |
| 6 | w32_k2_t025_train_quantile_r07_13 | 0.1682 | 0.0% | +0.0876 | +0.0376 | +0.0075 | +0.1228 | -0.0588 | +0.1890 |
| 7 | w32_k2_t05_train_quantile_r07_13 | 0.1683 | 0.0% | +0.0856 | +0.0360 | +0.0078 | +0.1263 | -0.0627 | +0.1871 |
| 8 | w64_k2_t10_train_quantile_r07_13 | 0.1685 | 0.0% | +0.0461 | +0.0093 | +0.0168 | +0.0294 | +0.0088 | +0.1864 |
| 9 | w32_k2_t10_train_quantile_r07_13 | 0.1678 | 0.0% | +0.0839 | +0.0333 | +0.0052 | +0.1344 | -0.0614 | +0.1825 |
| 10 | w64_k3_t025_train_quantile_r07_13 | 0.1705 | 0.0% | +0.0337 | +0.0035 | +0.0497 | +0.2816 | -0.0382 | +0.1605 |
| 11 | w64_k3_t05_train_quantile_r07_13 | 0.1707 | 0.0% | +0.0375 | +0.0037 | +0.0465 | +0.3019 | -0.0429 | +0.1560 |
| 12 | w32_k3_t025_train_quantile_r07_13 | 0.1706 | 0.0% | +0.0824 | +0.0324 | +0.0085 | +0.2653 | -0.0723 | +0.1547 |
| 13 | w48_k3_t025_train_quantile_r07_13 | 0.1712 | 0.0% | +0.0534 | +0.0145 | +0.0249 | +0.2760 | -0.0562 | +0.1544 |
| 14 | w48_k3_t05_train_quantile_r07_13 | 0.1718 | 0.0% | +0.0584 | +0.0183 | +0.0244 | +0.2956 | -0.0622 | +0.1524 |
| 15 | w32_k3_t05_train_quantile_r07_13 | 0.1696 | 0.0% | +0.0830 | +0.0330 | +0.0098 | +0.2824 | -0.0811 | +0.1502 |
| 16 | w48_k2_t025_train_quantile_r08_12 | 0.1124 | 0.0% | +0.0594 | +0.0182 | +0.0182 | +0.0534 | -0.0156 | +0.1454 |
| 17 | w48_k2_t05_train_quantile_r08_12 | 0.1125 | 0.0% | +0.0606 | +0.0190 | +0.0141 | +0.0542 | -0.0156 | +0.1439 |
| 18 | w64_k3_t10_train_quantile_r07_13 | 0.1704 | 0.0% | +0.0406 | +0.0082 | +0.0351 | +0.3328 | -0.0457 | +0.1435 |
| 19 | w48_k3_t10_train_quantile_r07_13 | 0.1712 | 0.0% | +0.0622 | +0.0257 | +0.0199 | +0.3313 | -0.0665 | +0.1425 |
| 20 | w32_k3_t10_train_quantile_r07_13 | 0.1694 | 0.0% | +0.0834 | +0.0370 | +0.0061 | +0.3069 | -0.0884 | +0.1412 |

## Recommended Candidates

- `w48_k2_t025_train_quantile_r07_13`: std=0.1687, clip=0.0%, baseline error r=+0.0594, entropy r=+0.0534.
- `w48_k2_t05_train_quantile_r07_13`: std=0.1687, clip=0.0%, baseline error r=+0.0606, entropy r=+0.0542.
- `w48_k2_t10_train_quantile_r07_13`: std=0.1689, clip=0.0%, baseline error r=+0.0598, entropy r=+0.0592.
- `w64_k2_t025_train_quantile_r07_13`: std=0.1688, clip=0.0%, baseline error r=+0.0423, entropy r=+0.0249.
- `w64_k2_t05_train_quantile_r07_13`: std=0.1687, clip=0.0%, baseline error r=+0.0446, entropy r=+0.0252.
