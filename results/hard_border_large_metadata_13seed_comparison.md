# Hard-Border-Large 13-Seed Metadata-Driven Confirmation

Protocol: enlarged hard-border split, real DNABERT-2 backbone, seeds `42-54`, validation-accuracy best checkpoint, validation-threshold tuned test evaluation. Metadata-driven GERM-BO uses `border_score_type=metadata_border_score`, `compensation_strength=0.27`, and `early_stopping_patience=4`.

## Summary

| Method | Test Acc Mean +/- Std | Test F1 Mean +/- Std | Min Acc | Max Acc |
|---|---:|---:|---:|---:|
| Baseline LoRA | 0.8377 +/- 0.0544 | 0.8300 +/- 0.0725 | 0.7305 | 0.9102 |
| GERM-BO final: attention.output + classifier | 0.8918 +/- 0.0255 | 0.8896 +/- 0.0276 | 0.8477 | 0.9297 |
| Metadata-driven GERM-BO comp=0.27/p4 | 0.9519 +/- 0.0443 | 0.9493 +/- 0.0483 | 0.8828 | 0.9961 |

## Paired Deltas

| Metric | Comparison | Delta Mean | Bootstrap 95% CI | Win Rate | Per-Seed Delta |
|---|---|---:|---:|---:|---:|
| test_accuracy | metadata_germ_bo_minus_baseline_lora | +0.1142 | [+0.0703, +0.1593] | 92.3% | +0.1602 / +0.1172 / +0.0469 / +0.0312 / +0.2500 / +0.2461 / -0.0039 / +0.0352 / +0.1133 / +0.0195 / +0.1992 / +0.1367 / +0.1328 |
| test_f1 | metadata_germ_bo_minus_baseline_lora | +0.1192 | [+0.0676, +0.1746] | 92.3% | +0.1561 / +0.1039 / +0.0262 / +0.0317 / +0.2723 / +0.3298 / -0.0160 / +0.0334 / +0.1191 / +0.0228 / +0.1845 / +0.1407 / +0.1455 |
| test_precision | metadata_germ_bo_minus_baseline_lora | +0.1153 | [+0.0747, +0.1568] | 92.3% | +0.1866 / +0.1890 / +0.1612 / +0.0323 / +0.2222 / +0.0597 / +0.0876 / +0.0662 / +0.0784 / -0.0115 / +0.2432 / +0.1240 / +0.0603 |
| test_recall | metadata_germ_bo_minus_baseline_lora | +0.1112 | [+0.0319, +0.1965] | 84.6% | +0.1250 / +0.0078 / -0.1094 / +0.0312 / +0.3125 / +0.4609 / -0.0938 / +0.0078 / +0.1562 / +0.0547 / +0.1172 / +0.1562 / +0.2188 |
| test_accuracy | metadata_germ_bo_minus_germ_bo_final_attn_output_classifier | +0.0601 | [+0.0361, +0.0835] | 92.3% | +0.0781 / +0.0430 / +0.0430 / +0.0156 / +0.0547 / +0.0859 / -0.0273 / +0.0234 / +0.0781 / +0.0273 / +0.1133 / +0.1367 / +0.1094 |
| test_f1 | metadata_germ_bo_minus_germ_bo_final_attn_output_classifier | +0.0596 | [+0.0323, +0.0860] | 92.3% | +0.0805 / +0.0429 / +0.0306 / +0.0135 / +0.0528 / +0.0837 / -0.0421 / +0.0205 / +0.0781 / +0.0326 / +0.1200 / +0.1496 / +0.1125 |
| test_precision | metadata_germ_bo_minus_germ_bo_final_attn_output_classifier | +0.0708 | [+0.0506, +0.0890] | 92.3% | +0.0661 / +0.0552 / +0.1249 / +0.0351 / +0.0896 / +0.1212 / +0.0830 / +0.0567 / +0.0781 / -0.0181 / +0.0702 / +0.0748 / +0.0835 |
| test_recall | metadata_germ_bo_minus_germ_bo_final_attn_output_classifier | +0.0499 | [+0.0000, +0.0980] | 69.2% | +0.0938 / +0.0312 / -0.0547 / -0.0078 / +0.0156 / +0.0469 / -0.1406 / -0.0078 / +0.0781 / +0.0781 / +0.1641 / +0.2109 / +0.1406 |
| test_accuracy | germ_bo_final_attn_output_classifier_minus_baseline_lora | +0.0541 | [+0.0240, +0.0892] | 84.6% | +0.0820 / +0.0742 / +0.0039 / +0.0156 / +0.1953 / +0.1602 / +0.0234 / +0.0117 / +0.0352 / -0.0078 / +0.0859 / +0.0000 / +0.0234 |
| test_f1 | germ_bo_final_attn_output_classifier_minus_baseline_lora | +0.0596 | [+0.0217, +0.1059] | 76.9% | +0.0756 / +0.0610 / -0.0044 / +0.0183 / +0.2194 / +0.2462 / +0.0260 / +0.0129 / +0.0409 / -0.0098 / +0.0644 / -0.0089 / +0.0330 |
| test_precision | germ_bo_final_attn_output_classifier_minus_baseline_lora | +0.0445 | [+0.0084, +0.0830] | 76.9% | +0.1205 / +0.1339 / +0.0363 / -0.0029 / +0.1327 / -0.0615 / +0.0045 / +0.0095 / +0.0003 / +0.0066 / +0.1731 / +0.0492 / -0.0232 |
| test_recall | germ_bo_final_attn_output_classifier_minus_baseline_lora | +0.0613 | [-0.0024, +0.1406] | 61.5% | +0.0312 / -0.0234 / -0.0547 / +0.0391 / +0.2969 / +0.4141 / +0.0469 / +0.0156 / +0.0781 / -0.0234 / -0.0469 / -0.0547 / +0.0781 |
