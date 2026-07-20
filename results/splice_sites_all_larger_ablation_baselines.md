# Splice Sites All Larger Split Ablations and Stronger Baselines

Protocol: `splice_sites_all`, larger balanced split `9000/1800/3000`, held-out seeds `45-49`, real DNABERT-2 backbone, validation-accuracy best checkpoint, multiclass argmax evaluation, single GPU `CUDA_VISIBLE_DEVICES=3`. This table supplements the selected w64/k3 estimator with additional LoRA baselines and GERM-BO mechanism ablations.

## Summary

| Method | Family | Seeds | Test Acc Mean +/- Std | Test Macro-F1 Mean +/- Std | Per-Seed Acc |
|---|---|---:|---:|---:|---|
| Baseline LoRA full target set | reference | 5 | 0.3853 +/- 0.0370 | 0.3016 +/- 0.0901 | 0.3740 / 0.3333 / 0.4287 / 0.3783 / 0.4123 |
| GERM-BO w64/k3/top10/scale3 | reference | 5 | 0.3995 +/- 0.0372 | 0.3531 +/- 0.0741 | 0.3867 / 0.4610 / 0.3850 / 0.3627 / 0.4023 |
| LoRA classifier only | baseline | 5 | 0.3369 +/- 0.0016 | 0.1858 +/- 0.0064 | 0.3397 / 0.3363 / 0.3363 / 0.3367 / 0.3353 |
| LoRA attention.output + classifier | baseline | 5 | 0.4002 +/- 0.0056 | 0.3419 +/- 0.0214 | 0.4070 / 0.3963 / 0.4033 / 0.3930 / 0.4013 |
| LoRA Wqkv + classifier | baseline | 5 | 0.3714 +/- 0.0373 | 0.2834 +/- 0.1077 | 0.4100 / 0.3337 / 0.3330 / 0.3750 / 0.4053 |
| GERM-BO w64/k3 comp=0 | ablation | 5 | 0.4002 +/- 0.0056 | 0.3419 +/- 0.0214 | 0.4070 / 0.3963 / 0.4033 / 0.3930 / 0.4013 |
| GERM-BO w64/k3 shuffled metadata | ablation | 5 | 0.3772 +/- 0.0180 | 0.3022 +/- 0.0458 | 0.3560 / 0.3680 / 0.3737 / 0.4037 / 0.3847 |

## Key Paired Deltas

| Comparison | Metric | Delta Mean | Bootstrap 95% CI | Win Rate | Per-Seed Delta |
|---|---|---:|---:|---:|---|
| germ_bo_center_w64_k3_t10_s3_minus_baseline_lora | test_accuracy | +0.0142 | [-0.0268, +0.0726] | 40.0% | +0.0127 / +0.1277 / -0.0437 / -0.0157 / -0.0100 |
| germ_bo_center_w64_k3_t10_s3_minus_baseline_lora | test_macro_f1 | +0.0515 | [-0.0505, +0.1797] | 40.0% | +0.1006 / +0.2945 / -0.0858 / -0.0231 / -0.0290 |
| germ_bo_center_w64_k3_t10_s3_minus_lora_attention_output_classifier | test_accuracy | -0.0007 | [-0.0239, +0.0329] | 40.0% | -0.0203 / +0.0647 / -0.0183 / -0.0303 / +0.0010 |
| germ_bo_center_w64_k3_t10_s3_minus_lora_attention_output_classifier | test_macro_f1 | +0.0112 | [-0.0325, +0.0678] | 40.0% | +0.0285 / +0.1184 / -0.0192 / -0.0444 / -0.0272 |
| germ_bo_center_w64_k3_t10_s3_minus_germ_bo_w64k3_comp0 | test_accuracy | -0.0007 | [-0.0239, +0.0329] | 40.0% | -0.0203 / +0.0647 / -0.0183 / -0.0303 / +0.0010 |
| germ_bo_center_w64_k3_t10_s3_minus_germ_bo_w64k3_comp0 | test_macro_f1 | +0.0112 | [-0.0325, +0.0678] | 40.0% | +0.0285 / +0.1184 / -0.0192 / -0.0444 / -0.0272 |
| germ_bo_center_w64_k3_t10_s3_minus_germ_bo_w64k3_shuffled | test_accuracy | +0.0223 | [-0.0149, +0.0616] | 80.0% | +0.0307 / +0.0930 / +0.0113 / -0.0410 / +0.0177 |
| germ_bo_center_w64_k3_t10_s3_minus_germ_bo_w64k3_shuffled | test_macro_f1 | +0.0508 | [-0.0194, +0.1211] | 80.0% | +0.1495 / +0.1335 / +0.0393 / -0.0784 / +0.0101 |
