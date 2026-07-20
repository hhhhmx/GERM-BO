# Splice Sites All Larger Split Traditional 3-mer Comparison Models

Protocol: same `9000/1800/3000` split, seeds `45-49`, sequence-only 3-mer baselines.

| Method | Seeds | Test Acc Mean +/- Std | Test Macro-F1 Mean +/- Std | Per-Seed Acc |
|---|---:|---:|---:|---|
| 3-mer Logistic Regression | 5 | 0.4094 +/- 0.0023 | 0.4052 +/- 0.0023 | 0.4128 / 0.4083 / 0.4089 / 0.4106 / 0.4067 |
| 3-mer Linear SVM | 5 | 0.4137 +/- 0.0026 | 0.4128 +/- 0.0026 | 0.4172 / 0.4139 / 0.4133 / 0.4139 / 0.4100 |
| 3-mer Multinomial NB | 5 | 0.4033 +/- 0.0000 | 0.3994 +/- 0.0000 | 0.4033 / 0.4033 / 0.4033 / 0.4033 / 0.4033 |
| 3-mer Nearest Centroid | 5 | 0.4033 +/- 0.0000 | 0.3994 +/- 0.0000 | 0.4033 / 0.4033 / 0.4033 / 0.4033 / 0.4033 |
