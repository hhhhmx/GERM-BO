# Splice Strict 3-mer-Balanced Confirmation Seeds 50-54

Protocol: strict `3-mer-balanced` split, seeds `50-54`, same single-GPU training budget, explicit `CUDA_VISIBLE_DEVICES=3`, comparing the strongest LoRA baseline against the current best external GERM-BO configuration.

## Summary

| Method | Seeds | Test Acc Mean +/- Std | Test Macro-F1 Mean +/- Std | Per-Seed Acc |
|---|---:|---:|---:|---|
| LoRA attention.output + classifier | 5 | 0.3489 +/- 0.0081 | 0.2405 +/- 0.0145 | 0.3383 / 0.3533 / 0.3539 / 0.3422 / 0.3567 |
| GERM-BO quantile [0.8,1.2] comp0.27 | 5 | 0.3888 +/- 0.0233 | 0.3580 +/- 0.0545 | 0.3606 / 0.4189 / 0.3728 / 0.3883 / 0.4033 |

## Paired Deltas

| Comparison | Metric | Delta Mean | Bootstrap 95% CI | Win Rate | Per-Seed Delta |
|---|---|---:|---:|---:|---|
| germ_bo_quantile_q08_12_comp027_minus_lora_attention_output_classifier | test_accuracy | +0.0399 | [+0.0257, +0.0541] | 100.0% | +0.0222 / +0.0656 / +0.0189 / +0.0461 / +0.0467 |
| germ_bo_quantile_q08_12_comp027_minus_lora_attention_output_classifier | test_macro_f1 | +0.1176 | [+0.0620, +0.1618] | 100.0% | +0.0168 / +0.1542 / +0.0894 / +0.1703 / +0.1571 |
