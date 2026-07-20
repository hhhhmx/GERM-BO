# Statistical Significance: Final GERM-BO vs Baseline LoRA

Protocol: paired comparison over the same 13 seeds (`42-54`) on the enlarged hard-border split. Metrics are computed after validation-accuracy best-checkpoint selection and validation-threshold tuned test evaluation.

| Metric | Baseline mean +/- std | GERM-BO final mean +/- std | Mean delta | Paired t-test p | Wilcoxon p | Bootstrap 95% CI | Effect size dz | Win rate |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Accuracy | 0.8377 +/- 0.0544 | 0.8918 +/- 0.0255 | +0.0541 | 0.0096 | 0.0015 | [+0.0240, +0.0895] | 0.8536 | 84.6% |
| F1 | 0.8300 +/- 0.0725 | 0.8896 +/- 0.0276 | +0.0596 | 0.0221 | 0.0034 | [+0.0221, +0.1063] | 0.7286 | 76.9% |
| Precision | 0.8617 +/- 0.0650 | 0.9062 +/- 0.0303 | +0.0445 | 0.0459 | 0.0479 | [+0.0081, +0.0834] | 0.6174 | 76.9% |
| Recall | 0.8143 +/- 0.1203 | 0.8756 +/- 0.0489 | +0.0613 | 0.1419 | 0.2500 | [-0.0030, +0.1418] | 0.4360 | 61.5% |

Per-seed accuracy deltas:

| Seeds | 42 | 43 | 44 | 45 | 46 | 47 | 48 | 49 | 50 | 51 | 52 | 53 | 54 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Accuracy delta | +0.0820 | +0.0742 | +0.0039 | +0.0156 | +0.1953 | +0.1602 | +0.0234 | +0.0117 | +0.0352 | -0.0078 | +0.0859 | +0.0000 | +0.0234 |

Conclusion: the final GERM-BO configuration shows statistically supported gains over baseline LoRA on the primary metric. Accuracy improves by `+0.0541` with a paired t-test p-value of `0.0096`, Wilcoxon p-value of `0.0015`, and a positive bootstrap 95% confidence interval. F1 and precision also show positive significant paired effects. Recall improves on average but is not significant at the 0.05 level.
