# Splice Sites All Larger Split W64K3 Held-Out Confirmation

Protocol: `splice_sites_all`, larger balanced split `9000/1800/3000`, held-out seeds `45-49`, real DNABERT-2 backbone, validation-accuracy best checkpoint, argmax test evaluation, single GPU `CUDA_VISIBLE_DEVICES=3`. This run stops the full 4-estimator grid and confirms only the best first-stage estimator: center-JSD `w64/k3/top10/scale3`.

## Summary

| Method | Seeds | Test Acc Mean +/- Std | Test Macro-F1 Mean +/- Std | Per-Seed Acc |
|---|---:|---:|---:|---|
| Baseline LoRA | 5 | 0.3853 +/- 0.0370 | 0.3016 +/- 0.0901 | 0.3740 / 0.3333 / 0.4287 / 0.3783 / 0.4123 |
| GERM-BO center-JSD w64 k3 top10 scale3 | 5 | 0.3995 +/- 0.0372 | 0.3531 +/- 0.0741 | 0.3867 / 0.4610 / 0.3850 / 0.3627 / 0.4023 |

## Paired Deltas

| Comparison | Metric | Delta Mean | Bootstrap 95% CI | Win Rate | Per-Seed Delta |
|---|---|---:|---:|---:|---|
| germ_bo_center_w64_k3_t10_s3_minus_baseline_lora | test_accuracy | +0.0142 | [-0.0268, +0.0726] | 40.0% | +0.0127 / +0.1277 / -0.0437 / -0.0157 / -0.0100 |
| germ_bo_center_w64_k3_t10_s3_minus_baseline_lora | test_macro_f1 | +0.0515 | [-0.0505, +0.1797] | 40.0% | +0.1006 / +0.2945 / -0.0858 / -0.0231 / -0.0290 |
