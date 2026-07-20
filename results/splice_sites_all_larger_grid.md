# Splice Sites All Larger Split Estimator Grid

Protocol: `splice_sites_all`, larger balanced split `9000/1800/3000`, seeds `42-44`, real DNABERT-2 backbone, validation-accuracy best checkpoint, argmax test evaluation, single GPU `CUDA_VISIBLE_DEVICES=3`. All GERM-BO variants use label-free metadata-estimated border scores and the same compensation setting `compensation_strength=0.27`, `patience=2`.

## Summary

| Method | Seeds | Test Acc Mean +/- Std | Test Macro-F1 Mean +/- Std | Per-Seed Acc |
|---|---:|---:|---:|---|
| Baseline LoRA | 3 | 0.3803 +/- 0.0438 | 0.2920 +/- 0.1117 | 0.3877 / 0.4200 / 0.3333 |
| GERM-BO center-JSD w48 k2 top25 scale4 | 3 | 0.3609 +/- 0.0233 | 0.2739 +/- 0.0912 | 0.3737 / 0.3340 / 0.3750 |
| GERM-BO center-JSD w64 k2 top10 scale4 | 3 | 0.3716 +/- 0.0073 | 0.2777 +/- 0.0303 | 0.3680 / 0.3667 / 0.3800 |
| GERM-BO center-JSD w64 k3 top10 scale3 | 3 | 0.3859 +/- 0.0158 | 0.3090 +/- 0.0317 | 0.3990 / 0.3903 / 0.3683 |
| GERM-BO center-JSD+motif w64 k2 top10 scale3 m0.5 | 3 | 0.3722 +/- 0.0036 | 0.2779 +/- 0.0143 | 0.3683 / 0.3730 / 0.3753 |

## Paired Deltas vs Baseline

| Method | Metric | Delta Mean | Bootstrap 95% CI | Win Rate | Per-Seed Delta |
|---|---|---:|---:|---:|---|
| GERM-BO center-JSD w48 k2 top25 scale4 | test_accuracy | -0.0194 | [-0.0860, +0.0417] | 33.3% | -0.0140 / -0.0860 / +0.0417 |
| GERM-BO center-JSD w48 k2 top25 scale4 | test_macro_f1 | -0.0181 | [-0.2116, +0.1473] | 66.7% | +0.0101 / -0.2116 / +0.1473 |
| GERM-BO center-JSD w64 k2 top10 scale4 | test_accuracy | -0.0088 | [-0.0533, +0.0467] | 33.3% | -0.0197 / -0.0533 / +0.0467 |
| GERM-BO center-JSD w64 k2 top10 scale4 | test_macro_f1 | -0.0143 | [-0.1186, +0.1459] | 33.3% | -0.0703 / -0.1186 / +0.1459 |
| GERM-BO center-JSD w64 k3 top10 scale3 | test_accuracy | +0.0056 | [-0.0297, +0.0350] | 66.7% | +0.0113 / -0.0297 / +0.0350 |
| GERM-BO center-JSD w64 k3 top10 scale3 | test_macro_f1 | +0.0170 | [-0.0713, +0.1102] | 66.7% | +0.0120 / -0.0713 / +0.1102 |
| GERM-BO center-JSD+motif w64 k2 top10 scale3 m0.5 | test_accuracy | -0.0081 | [-0.0470, +0.0420] | 33.3% | -0.0193 / -0.0470 / +0.0420 |
| GERM-BO center-JSD+motif w64 k2 top10 scale3 m0.5 | test_macro_f1 | -0.0141 | [-0.0981, +0.1223] | 33.3% | -0.0664 / -0.0981 / +0.1223 |
