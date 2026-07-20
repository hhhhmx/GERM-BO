# Statistical Significance: hard_border_large Metadata-Driven GERM-BO

Protocol: paired comparison over seeds `42-54` on the enlarged hard-border split. Metrics use validation-accuracy best checkpoint and validation-threshold tuned test evaluation. P-values are paired t-test normal approximation and exact Wilcoxon signed-rank test. Bootstrap CIs use 20,000 paired bootstrap samples over mean deltas.

| Metric | Comparison | Mean A +/- Std | Mean B +/- Std | Delta | t-test p | Wilcoxon p | Bootstrap 95% CI | Win Rate |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| test_accuracy | metadata_germ_bo_minus_baseline_lora | 0.9519 +/- 0.0443 | 0.8377 +/- 0.0544 | +0.1142 | 0.0000 | 0.0005 | [+0.0703, +0.1593] | 92.3% |
| test_f1 | metadata_germ_bo_minus_baseline_lora | 0.9493 +/- 0.0483 | 0.8300 +/- 0.0725 | +0.1192 | 0.0000 | 0.0005 | [+0.0676, +0.1746] | 92.3% |
| test_precision | metadata_germ_bo_minus_baseline_lora | 0.9770 +/- 0.0268 | 0.8617 +/- 0.0650 | +0.1153 | 0.0000 | 0.0005 | [+0.0747, +0.1568] | 92.3% |
| test_recall | metadata_germ_bo_minus_baseline_lora | 0.9255 +/- 0.0759 | 0.8143 +/- 0.1203 | +0.1112 | 0.0113 | 0.0132 | [+0.0319, +0.1965] | 84.6% |
| test_accuracy | metadata_germ_bo_minus_germ_bo_final_attn_output_classifier | 0.9519 +/- 0.0443 | 0.8918 +/- 0.0255 | +0.0601 | 0.0000 | 0.0015 | [+0.0361, +0.0835] | 92.3% |
| test_f1 | metadata_germ_bo_minus_germ_bo_final_attn_output_classifier | 0.9493 +/- 0.0483 | 0.8896 +/- 0.0276 | +0.0596 | 0.0000 | 0.0024 | [+0.0323, +0.0860] | 92.3% |
| test_precision | metadata_germ_bo_minus_germ_bo_final_attn_output_classifier | 0.9770 +/- 0.0268 | 0.9062 +/- 0.0303 | +0.0708 | 0.0000 | 0.0005 | [+0.0506, +0.0890] | 92.3% |
| test_recall | metadata_germ_bo_minus_germ_bo_final_attn_output_classifier | 0.9255 +/- 0.0759 | 0.8756 +/- 0.0489 | +0.0499 | 0.0558 | 0.0730 | [+0.0000, +0.0980] | 69.2% |
| test_accuracy | germ_bo_final_attn_output_classifier_minus_baseline_lora | 0.8918 +/- 0.0255 | 0.8377 +/- 0.0544 | +0.0541 | 0.0021 | 0.0015 | [+0.0240, +0.0892] | 84.6% |
| test_f1 | germ_bo_final_attn_output_classifier_minus_baseline_lora | 0.8896 +/- 0.0276 | 0.8300 +/- 0.0725 | +0.0596 | 0.0086 | 0.0034 | [+0.0217, +0.1059] | 76.9% |
| test_precision | germ_bo_final_attn_output_classifier_minus_baseline_lora | 0.9062 +/- 0.0303 | 0.8617 +/- 0.0650 | +0.0445 | 0.0260 | 0.0479 | [+0.0084, +0.0830] | 76.9% |
| test_recall | germ_bo_final_attn_output_classifier_minus_baseline_lora | 0.8756 +/- 0.0489 | 0.8143 +/- 0.1203 | +0.0613 | 0.1159 | 0.2500 | [-0.0024, +0.1406] | 61.5% |

## Main Interpretation

Metadata-driven GERM-BO improves accuracy over Baseline LoRA by `+0.1142` and over activation-derived GERM-BO by `+0.0601`. Both bootstrap intervals are strictly positive, supporting metadata-driven GERM-BO as the strongest current main configuration.
