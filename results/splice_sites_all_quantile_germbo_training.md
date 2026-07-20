# Splice Sites All Quantile-Normalized GERM-BO Training

Protocol: same larger balanced split `9000/1800/3000`, held-out seeds `45-49`, real DNABERT-2 backbone, argmax evaluation, single GPU `CUDA_VISIBLE_DEVICES=3`. This experiment tests whether fixing estimator saturation via train-quantile normalization improves GERM-BO.

## Summary

| Method | Seeds | Test Acc Mean +/- Std | Test Macro-F1 Mean +/- Std | Per-Seed Acc |
|---|---:|---:|---:|---|
| GERM-BO quantile [0.8,1.2] comp0.27 | 5 | 0.4147 +/- 0.0447 | 0.3716 +/- 0.0804 | 0.4797 / 0.4380 / 0.4030 / 0.3857 / 0.3673 |
| GERM-BO raw-clipped w64/k3 | 5 | 0.3995 +/- 0.0372 | 0.3531 +/- 0.0741 | 0.3867 / 0.4610 / 0.3850 / 0.3627 / 0.4023 |
| LoRA attention.output + classifier | 5 | 0.4002 +/- 0.0056 | 0.3419 +/- 0.0214 | 0.4070 / 0.3963 / 0.4033 / 0.3930 / 0.4013 |
| GERM-BO quantile [0.75,1.25] comp1.0 | 5 | 0.3837 +/- 0.0368 | 0.3219 +/- 0.0919 | 0.3573 / 0.4253 / 0.3440 / 0.3723 / 0.4193 |
| GERM-BO quantile [0.75,1.25] comp0.27 | 5 | 0.3898 +/- 0.0302 | 0.3172 +/- 0.0693 | 0.3743 / 0.4207 / 0.3620 / 0.3677 / 0.4243 |
| Baseline LoRA full target set | 5 | 0.3853 +/- 0.0370 | 0.3016 +/- 0.0901 | 0.3740 / 0.3333 / 0.4287 / 0.3783 / 0.4123 |

## Paired Deltas

| Comparison | Metric | Delta Mean | Bootstrap 95% CI | Win Rate | Per-Seed Delta |
|---|---|---:|---:|---:|---|
| germ_bo_quantile_q08_12_comp027_minus_germ_bo_raw_w64k3 | test_accuracy | +0.0152 | [-0.0210, +0.0548] | 60.0% | +0.0930 / -0.0230 / +0.0180 / +0.0230 / -0.0350 |
| germ_bo_quantile_q08_12_comp027_minus_germ_bo_raw_w64k3 | test_macro_f1 | +0.0185 | [-0.0421, +0.0791] | 60.0% | +0.0827 / -0.0379 / +0.0247 / +0.1028 / -0.0797 |
| germ_bo_quantile_q075_125_comp027_minus_germ_bo_raw_w64k3 | test_accuracy | -0.0097 | [-0.0278, +0.0084] | 40.0% | -0.0123 / -0.0403 / -0.0230 / +0.0050 / +0.0220 |
| germ_bo_quantile_q075_125_comp027_minus_germ_bo_raw_w64k3 | test_macro_f1 | -0.0358 | [-0.0790, +0.0149] | 40.0% | -0.1074 / -0.0606 / -0.0589 / +0.0024 / +0.0455 |
| germ_bo_quantile_q075_125_comp100_minus_germ_bo_raw_w64k3 | test_accuracy | -0.0159 | [-0.0365, +0.0050] | 40.0% | -0.0293 / -0.0357 / -0.0410 / +0.0097 / +0.0170 |
| germ_bo_quantile_q075_125_comp100_minus_germ_bo_raw_w64k3 | test_macro_f1 | -0.0312 | [-0.1072, +0.0449] | 40.0% | -0.1412 / -0.0571 / -0.0983 / +0.0599 / +0.0808 |
| germ_bo_quantile_q075_125_comp027_minus_lora_attention_output_classifier | test_accuracy | -0.0104 | [-0.0347, +0.0139] | 40.0% | -0.0327 / +0.0243 / -0.0413 / -0.0253 / +0.0230 |
| germ_bo_quantile_q075_125_comp027_minus_lora_attention_output_classifier | test_macro_f1 | -0.0246 | [-0.0712, +0.0227] | 40.0% | -0.0790 / +0.0577 / -0.0781 / -0.0420 / +0.0182 |
| germ_bo_quantile_q075_125_comp100_minus_lora_attention_output_classifier | test_accuracy | -0.0165 | [-0.0477, +0.0147] | 40.0% | -0.0497 / +0.0290 / -0.0593 / -0.0207 / +0.0180 |
| germ_bo_quantile_q075_125_comp100_minus_lora_attention_output_classifier | test_macro_f1 | -0.0200 | [-0.0890, +0.0491] | 60.0% | -0.1127 / +0.0613 / -0.1175 / +0.0155 / +0.0536 |
