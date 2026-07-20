# Splice Top-3 Estimator Confirmation Seeds 50-54

Protocol: estimator-only grid top candidates promoted to training on the same larger balanced split `9000/1800/3000`, held-out seeds `50-54`, single GPU `CUDA_VISIBLE_DEVICES=3`.

## Summary

| Method | Seeds | Test Acc Mean +/- Std | Test Macro-F1 Mean +/- Std | Per-Seed Acc |
|---|---:|---:|---:|---|
| GERM-BO quantile [0.8,1.2] comp0.27 | 5 | 0.4000 +/- 0.0258 | 0.3604 +/- 0.0411 | 0.4060 / 0.4243 / 0.3990 / 0.4137 / 0.3570 |
| GERM-BO w48 k2 top0.5 quantile [0.7,1.3] | 5 | 0.3950 +/- 0.0315 | 0.3268 +/- 0.0685 | 0.3910 / 0.3863 / 0.4390 / 0.3523 / 0.4063 |
| GERM-BO w64 k2 top0.25 quantile [0.7,1.3] | 5 | 0.3725 +/- 0.0203 | 0.3025 +/- 0.0446 | 0.3487 / 0.3527 / 0.3820 / 0.3897 / 0.3897 |
| LoRA attention.output + classifier | 5 | 0.3636 +/- 0.0242 | 0.2878 +/- 0.0588 | 0.3843 / 0.3377 / 0.3817 / 0.3777 / 0.3367 |
| GERM-BO w48 k2 top0.25 quantile [0.7,1.3] | 5 | 0.3763 +/- 0.0302 | 0.2810 +/- 0.0696 | 0.3653 / 0.4137 / 0.3357 / 0.3973 / 0.3697 |

## Paired Deltas

| Comparison | Metric | Delta Mean | Bootstrap 95% CI | Win Rate | Per-Seed Delta |
|---|---|---:|---:|---:|---|
| germ_bo_w48_k2_t025_train_quantile_r07_13_minus_lora_attention_output_classifier | test_accuracy | +0.0127 | [-0.0248, +0.0484] | 60.0% | -0.0190 / +0.0760 / -0.0460 / +0.0197 / +0.0330 |
| germ_bo_w48_k2_t025_train_quantile_r07_13_minus_lora_attention_output_classifier | test_macro_f1 | -0.0068 | [-0.1041, +0.0864] | 40.0% | -0.0565 / +0.1463 / -0.1711 / +0.0493 / -0.0022 |
| germ_bo_w48_k2_t05_train_quantile_r07_13_minus_lora_attention_output_classifier | test_accuracy | +0.0314 | [-0.0024, +0.0605] | 80.0% | +0.0067 / +0.0487 / +0.0573 / -0.0253 / +0.0697 |
| germ_bo_w48_k2_t05_train_quantile_r07_13_minus_lora_attention_output_classifier | test_macro_f1 | +0.0390 | [-0.0282, +0.0934] | 60.0% | -0.0019 / +0.1246 / +0.0694 / -0.0710 / +0.0740 |
| germ_bo_w64_k2_t025_train_quantile_r07_13_minus_lora_attention_output_classifier | test_accuracy | +0.0089 | [-0.0160, +0.0343] | 80.0% | -0.0357 / +0.0150 / +0.0003 / +0.0120 / +0.0530 |
| germ_bo_w64_k2_t025_train_quantile_r07_13_minus_lora_attention_output_classifier | test_macro_f1 | +0.0146 | [-0.0522, +0.0839] | 60.0% | -0.0958 / +0.1452 / -0.0231 / +0.0070 / +0.0398 |
| germ_bo_w48_k2_t025_train_quantile_r07_13_minus_germ_bo_quantile_q08_12_comp027 | test_accuracy | -0.0237 | [-0.0483, -0.0025] | 20.0% | -0.0407 / -0.0107 / -0.0633 / -0.0163 / +0.0127 |
| germ_bo_w48_k2_t025_train_quantile_r07_13_minus_germ_bo_quantile_q08_12_comp027 | test_macro_f1 | -0.0794 | [-0.1191, -0.0459] | 0.0% | -0.0925 / -0.0737 / -0.1527 / -0.0449 / -0.0331 |
| germ_bo_w48_k2_t05_train_quantile_r07_13_minus_germ_bo_quantile_q08_12_comp027 | test_accuracy | -0.0050 | [-0.0427, +0.0327] | 40.0% | -0.0150 / -0.0380 / +0.0400 / -0.0613 / +0.0493 |
| germ_bo_w48_k2_t05_train_quantile_r07_13_minus_germ_bo_quantile_q08_12_comp027 | test_macro_f1 | -0.0335 | [-0.1143, +0.0448] | 40.0% | -0.0380 / -0.0954 / +0.0878 / -0.1652 / +0.0432 |
| germ_bo_w64_k2_t025_train_quantile_r07_13_minus_germ_bo_quantile_q08_12_comp027 | test_accuracy | -0.0275 | [-0.0579, +0.0047] | 20.0% | -0.0573 / -0.0717 / -0.0170 / -0.0240 / +0.0327 |
| germ_bo_w64_k2_t025_train_quantile_r07_13_minus_germ_bo_quantile_q08_12_comp027 | test_macro_f1 | -0.0579 | [-0.1025, -0.0130] | 20.0% | -0.1318 / -0.0748 / -0.0047 / -0.0871 / +0.0089 |
