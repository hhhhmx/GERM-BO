# Splice Strict 3-mer-Balanced Full Comparison Table

Protocol: strict `3-mer-balanced` split. DNABERT-2 runs use held-out seeds `50-54` on a single GPU with explicit `CUDA_VISIBLE_DEVICES=3`. Traditional 3-mer baselines come from the same split and are sequence-only comparison models.

## Main Table

| Rank | Method | Family | Seeds | Test Acc Mean +/- Std | Test Macro-F1 Mean +/- Std | Per-Seed Acc |
|---:|---|---|---:|---:|---:|---|
| 1 | 3-mer Linear SVM | traditional_kmer | 5 | 0.4137 +/- 0.0026 | 0.4128 +/- 0.0026 | 0.4172 / 0.4139 / 0.4133 / 0.4139 / 0.4100 |
| 2 | 3-mer Logistic Regression | traditional_kmer | 5 | 0.4094 +/- 0.0023 | 0.4052 +/- 0.0023 | 0.4128 / 0.4083 / 0.4089 / 0.4106 / 0.4067 |
| 3 | 3-mer Multinomial NB | traditional_kmer | 5 | 0.4033 +/- 0.0000 | 0.3994 +/- 0.0000 | 0.4033 / 0.4033 / 0.4033 / 0.4033 / 0.4033 |
| 4 | 3-mer Nearest Centroid | traditional_kmer | 5 | 0.4033 +/- 0.0000 | 0.3994 +/- 0.0000 | 0.4033 / 0.4033 / 0.4033 / 0.4033 / 0.4033 |
| 5 | GERM-BO quantile [0.8,1.2] comp0.27 | dnabert2_germ_bo | 5 | 0.3888 +/- 0.0233 | 0.3580 +/- 0.0545 | 0.3606 / 0.4189 / 0.3728 / 0.3883 / 0.4033 |
| 6 | GERM-BO activation-derived comp0.27 | direction_aware_peft | 5 | 0.3709 +/- 0.0144 | 0.3112 +/- 0.0492 | 0.3750 / 0.3578 / 0.3733 / 0.3917 / 0.3567 |
| 7 | GERM-BO shuffled metadata | mechanism_ablation | 5 | 0.3656 +/- 0.0273 | 0.2844 +/- 0.0842 | 0.3772 / 0.3706 / 0.3311 / 0.4017 / 0.3472 |
| 8 | Gated LoRA attention.output + classifier | direction_aware_peft | 5 | 0.3606 +/- 0.0254 | 0.2769 +/- 0.0873 | 0.3889 / 0.3350 / 0.3733 / 0.3322 / 0.3733 |
| 9 | LoRA attention.output + classifier | dnabert2_lora_baseline | 5 | 0.3489 +/- 0.0081 | 0.2405 +/- 0.0145 | 0.3383 / 0.3533 / 0.3539 / 0.3422 / 0.3567 |
| 10 | GERM-BO comp=0 | mechanism_ablation | 5 | 0.3489 +/- 0.0081 | 0.2405 +/- 0.0145 | 0.3383 / 0.3533 / 0.3539 / 0.3422 / 0.3567 |
| 11 | Baseline LoRA full target set | dnabert2_lora | 5 | 0.3578 +/- 0.0334 | 0.2344 +/- 0.0918 | 0.3822 / 0.4044 / 0.3333 / 0.3356 / 0.3333 |
| 12 | DNABERT-2 frozen linear probe | dnabert2_probe | 5 | 0.3334 +/- 0.0006 | 0.1688 +/- 0.0042 | 0.3344 / 0.3328 / 0.3333 / 0.3333 / 0.3333 |

## Paired Deltas vs GERM-BO quantile [0.8,1.2] comp0.27

| Method - Reference | Metric | Delta Mean | Bootstrap 95% CI | Win Rate | Per-Seed Delta |
|---|---|---:|---:|---:|---|
| Baseline LoRA full target set - GERM-BO quantile [0.8,1.2] comp0.27 | test_accuracy | -0.0310 | [-0.0570, -0.0004] | 20.0% | +0.0217 / -0.0144 / -0.0394 / -0.0528 / -0.0700 |
| Baseline LoRA full target set - GERM-BO quantile [0.8,1.2] comp0.27 | test_macro_f1 | -0.1236 | [-0.2138, -0.0292] | 20.0% | +0.0309 / -0.0245 / -0.1802 / -0.2145 / -0.2299 |
| DNABERT-2 frozen linear probe - GERM-BO quantile [0.8,1.2] comp0.27 | test_accuracy | -0.0553 | [-0.0736, -0.0372] | 0.0% | -0.0261 / -0.0861 / -0.0394 / -0.0550 / -0.0700 |
| DNABERT-2 frozen linear probe - GERM-BO quantile [0.8,1.2] comp0.27 | test_macro_f1 | -0.1893 | [-0.2257, -0.1366] | 0.0% | -0.0909 / -0.2219 / -0.1802 / -0.2234 / -0.2299 |
| GERM-BO activation-derived comp0.27 - GERM-BO quantile [0.8,1.2] comp0.27 | test_accuracy | -0.0179 | [-0.0453, +0.0072] | 60.0% | +0.0144 / -0.0611 / +0.0006 / +0.0033 / -0.0467 |
| GERM-BO activation-derived comp0.27 - GERM-BO quantile [0.8,1.2] comp0.27 | test_macro_f1 | -0.0469 | [-0.1170, +0.0311] | 20.0% | +0.0838 / -0.1392 / -0.0041 / -0.0432 / -0.1316 |
| GERM-BO comp=0 - GERM-BO quantile [0.8,1.2] comp0.27 | test_accuracy | -0.0399 | [-0.0541, -0.0251] | 0.0% | -0.0222 / -0.0656 / -0.0189 / -0.0461 / -0.0467 |
| GERM-BO comp=0 - GERM-BO quantile [0.8,1.2] comp0.27 | test_macro_f1 | -0.1176 | [-0.1618, -0.0604] | 0.0% | -0.0168 / -0.1542 / -0.0894 / -0.1703 / -0.1571 |
| GERM-BO shuffled metadata - GERM-BO quantile [0.8,1.2] comp0.27 | test_accuracy | -0.0232 | [-0.0501, +0.0037] | 40.0% | +0.0167 / -0.0483 / -0.0417 / +0.0133 / -0.0561 |
| GERM-BO shuffled metadata - GERM-BO quantile [0.8,1.2] comp0.27 | test_macro_f1 | -0.0736 | [-0.1548, +0.0130] | 20.0% | +0.0847 / -0.0946 / -0.1800 / -0.0184 / -0.1597 |
| Gated LoRA attention.output + classifier - GERM-BO quantile [0.8,1.2] comp0.27 | test_accuracy | -0.0282 | [-0.0620, +0.0059] | 40.0% | +0.0283 / -0.0839 / +0.0006 / -0.0561 / -0.0300 |
| Gated LoRA attention.output + classifier - GERM-BO quantile [0.8,1.2] comp0.27 | test_macro_f1 | -0.0811 | [-0.1753, +0.0080] | 20.0% | +0.0605 / -0.1855 / -0.0350 / -0.2227 / -0.0229 |
| LoRA attention.output + classifier - GERM-BO quantile [0.8,1.2] comp0.27 | test_accuracy | -0.0399 | [-0.0541, -0.0251] | 0.0% | -0.0222 / -0.0656 / -0.0189 / -0.0461 / -0.0467 |
| LoRA attention.output + classifier - GERM-BO quantile [0.8,1.2] comp0.27 | test_macro_f1 | -0.1176 | [-0.1618, -0.0604] | 0.0% | -0.0168 / -0.1542 / -0.0894 / -0.1703 / -0.1571 |
