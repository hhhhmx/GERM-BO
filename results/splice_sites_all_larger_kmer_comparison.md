# Splice Sites All Larger Split Traditional 3-mer Comparison Models

Protocol: same `9000/1800/3000` split, seeds `45-49`, sequence-only 3-mer baselines.

| Method | Seeds | Test Acc Mean +/- Std | Test Macro-F1 Mean +/- Std | Per-Seed Acc |
|---|---:|---:|---:|---|
| 3-mer Logistic Regression | 5 | 0.4318 +/- 0.0008 | 0.4293 +/- 0.0008 | 0.4310 / 0.4327 / 0.4320 / 0.4323 / 0.4310 |
| 3-mer Linear SVM | 5 | 0.4257 +/- 0.0019 | 0.4259 +/- 0.0019 | 0.4263 / 0.4283 / 0.4233 / 0.4243 / 0.4263 |
| 3-mer Multinomial NB | 5 | 0.3867 +/- 0.0000 | 0.3540 +/- 0.0000 | 0.3867 / 0.3867 / 0.3867 / 0.3867 / 0.3867 |
| 3-mer Nearest Centroid | 5 | 0.3863 +/- 0.0000 | 0.3652 +/- 0.0000 | 0.3863 / 0.3863 / 0.3863 / 0.3863 / 0.3863 |
