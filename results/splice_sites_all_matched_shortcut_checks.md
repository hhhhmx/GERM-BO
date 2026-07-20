# Splice Sites All Matched Split Shortcut Checks

Protocol: compare traditional 3-mer baselines on the original larger split, a `GC-matched` split, and a stricter `3-mer-balanced` split. Lower 3-mer accuracy on matched splits would indicate that the original split contains stronger short-range composition shortcuts.

## Summary Table

| Method | Original Larger Macro-F1 | GC-Matched Macro-F1 | 3-mer-Balanced Macro-F1 | Original Larger Acc | GC-Matched Acc | 3-mer-Balanced Acc |
|---|---:|---:|---:|---:|---:|---:|
| 3-mer Linear SVM | 0.4259 +/- 0.0019 | 0.4261 +/- 0.0033 | 0.4128 +/- 0.0026 | 0.4257 +/- 0.0019 | 0.4270 +/- 0.0033 | 0.4137 +/- 0.0026 |
| 3-mer Logistic Regression | 0.4293 +/- 0.0008 | 0.4249 +/- 0.0026 | 0.4052 +/- 0.0023 | 0.4318 +/- 0.0008 | 0.4296 +/- 0.0026 | 0.4094 +/- 0.0023 |
| 3-mer Multinomial NB | 0.3540 +/- 0.0000 | 0.4070 +/- 0.0000 | 0.3994 +/- 0.0000 | 0.3867 +/- 0.0000 | 0.4089 +/- 0.0000 | 0.4033 +/- 0.0000 |
| 3-mer Nearest Centroid | 0.3652 +/- 0.0000 | 0.4052 +/- 0.0000 | 0.3994 +/- 0.0000 | 0.3863 +/- 0.0000 | 0.4072 +/- 0.0000 | 0.4033 +/- 0.0000 |
