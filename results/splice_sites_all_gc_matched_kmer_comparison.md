# Splice Sites All Larger Split Traditional 3-mer Comparison Models

Protocol: same `9000/1800/3000` split, seeds `45-49`, sequence-only 3-mer baselines.

| Method | Seeds | Test Acc Mean +/- Std | Test Macro-F1 Mean +/- Std | Per-Seed Acc |
|---|---:|---:|---:|---|
| 3-mer Logistic Regression | 5 | 0.4296 +/- 0.0026 | 0.4249 +/- 0.0026 | 0.4294 / 0.4317 / 0.4322 / 0.4289 / 0.4256 |
| 3-mer Linear SVM | 5 | 0.4270 +/- 0.0033 | 0.4261 +/- 0.0033 | 0.4272 / 0.4289 / 0.4306 / 0.4267 / 0.4217 |
| 3-mer Multinomial NB | 5 | 0.4089 +/- 0.0000 | 0.4070 +/- 0.0000 | 0.4089 / 0.4089 / 0.4089 / 0.4089 / 0.4089 |
| 3-mer Nearest Centroid | 5 | 0.4072 +/- 0.0000 | 0.4052 +/- 0.0000 | 0.4072 / 0.4072 / 0.4072 / 0.4072 / 0.4072 |
