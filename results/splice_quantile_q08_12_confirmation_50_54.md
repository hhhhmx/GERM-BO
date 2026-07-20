# Splice Quantile Q08-12 Confirmation Seeds 50-54

Protocol: same larger balanced split `9000/1800/3000`, held-out seeds `50-54`, single GPU `CUDA_VISIBLE_DEVICES=3`, argmax accuracy and macro-F1. This confirms the best quantile-normalized GERM-BO configuration against the strongest LoRA baseline.

## Summary

| Method | Seeds | Test Acc Mean +/- Std | Test Macro-F1 Mean +/- Std | Per-Seed Acc |
|---|---:|---:|---:|---|
| LoRA attention.output + classifier | 5 | 0.3636 +/- 0.0242 | 0.2878 +/- 0.0588 | 0.3843 / 0.3377 / 0.3817 / 0.3777 / 0.3367 |
| GERM-BO quantile [0.8,1.2] comp0.27 | 5 | 0.4000 +/- 0.0258 | 0.3604 +/- 0.0411 | 0.4060 / 0.4243 / 0.3990 / 0.4137 / 0.3570 |

## Paired Deltas

| Comparison | Metric | Delta Mean | Bootstrap 95% CI | Win Rate | Per-Seed Delta |
|---|---|---:|---:|---:|---|
| germ_bo_quantile_q08_12_comp027_minus_lora_attention_output_classifier | test_accuracy | +0.0364 | [+0.0194, +0.0627] | 100.0% | +0.0217 / +0.0867 / +0.0173 / +0.0360 / +0.0203 |
| germ_bo_quantile_q08_12_comp027_minus_lora_attention_output_classifier | test_macro_f1 | +0.0725 | [+0.0122, +0.1472] | 80.0% | +0.0360 / +0.2200 / -0.0184 / +0.0942 / +0.0309 |
