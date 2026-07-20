# Splice Strict 3-mer-Balanced Confirmation Seeds 55-59

Protocol: strict `3-mer-balanced` split, seeds `55-59`, same single-GPU training budget, explicit `CUDA_VISIBLE_DEVICES=3`, comparing the strongest LoRA baseline against the current best external GERM-BO configuration.

## Summary

| Method | Seeds | Test Acc Mean +/- Std | Test Macro-F1 Mean +/- Std | Per-Seed Acc |
|---|---:|---:|---:|---|
| LoRA attention.output + classifier | 5 | 0.3462 +/- 0.0088 | 0.2274 +/- 0.0384 | 0.3572 / 0.3333 / 0.3439 / 0.3500 / 0.3467 |
| GERM-BO quantile [0.8,1.2] comp0.27 | 5 | 0.3561 +/- 0.0290 | 0.2909 +/- 0.0757 | 0.3567 / 0.4061 / 0.3361 / 0.3422 / 0.3394 |

## Paired Deltas

| Comparison | Metric | Delta Mean | Bootstrap 95% CI | Win Rate | Per-Seed Delta |
|---|---|---:|---:|---:|---|
| germ_bo_quantile_q08_12_comp027_minus_lora_attention_output_classifier | test_accuracy | +0.0099 | [-0.0077, +0.0420] | 20.0% | -0.0006 / +0.0728 / -0.0078 / -0.0078 / -0.0072 |
| germ_bo_quantile_q08_12_comp027_minus_lora_attention_output_classifier | test_macro_f1 | +0.0636 | [-0.0121, +0.1453] | 60.0% | +0.0563 / +0.2075 / +0.1124 / -0.0083 / -0.0501 |
