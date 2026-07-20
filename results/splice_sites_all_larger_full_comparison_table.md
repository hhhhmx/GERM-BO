# Splice Sites All Larger Split Full Comparison Table

Protocol: same balanced `9000/1800/3000` split, held-out seeds `45-49`, argmax accuracy and macro-F1. DNABERT-2 runs use single GPU `CUDA_VISIBLE_DEVICES=3`; traditional k-mer baselines are sequence-only comparison models.

## Main Table

| Rank | Method | Family | Seeds | Test Acc Mean +/- Std | Test Macro-F1 Mean +/- Std | Per-Seed Acc |
|---:|---|---|---:|---:|---:|---|
| 1 | 3-mer Logistic Regression | traditional_kmer | 5 | 0.4318 +/- 0.0008 | 0.4293 +/- 0.0008 | 0.4310 / 0.4327 / 0.4320 / 0.4323 / 0.4310 |
| 2 | 3-mer Linear SVM | traditional_kmer | 5 | 0.4257 +/- 0.0019 | 0.4259 +/- 0.0019 | 0.4263 / 0.4283 / 0.4233 / 0.4243 / 0.4263 |
| 3 | GERM-BO quantile [0.8,1.2] comp0.27 | dnabert2_germ_bo | 5 | 0.4147 +/- 0.0447 | 0.3716 +/- 0.0804 | 0.4797 / 0.4380 / 0.4030 / 0.3857 / 0.3673 |
| 4 | 3-mer Nearest Centroid | traditional_kmer | 5 | 0.3863 +/- 0.0000 | 0.3652 +/- 0.0000 | 0.3863 / 0.3863 / 0.3863 / 0.3863 / 0.3863 |
| 5 | 3-mer Multinomial NB | traditional_kmer | 5 | 0.3867 +/- 0.0000 | 0.3540 +/- 0.0000 | 0.3867 / 0.3867 / 0.3867 / 0.3867 / 0.3867 |
| 6 | GERM-BO w64/k3/top10/scale3 | dnabert2_germ_bo | 5 | 0.3995 +/- 0.0372 | 0.3531 +/- 0.0741 | 0.3867 / 0.4610 / 0.3850 / 0.3627 / 0.4023 |
| 7 | LoRA attention.output + classifier | dnabert2_lora_baseline | 5 | 0.4002 +/- 0.0056 | 0.3419 +/- 0.0214 | 0.4070 / 0.3963 / 0.4033 / 0.3930 / 0.4013 |
| 8 | GERM-BO w64/k3 comp=0 | mechanism_ablation | 5 | 0.4002 +/- 0.0056 | 0.3419 +/- 0.0214 | 0.4070 / 0.3963 / 0.4033 / 0.3930 / 0.4013 |
| 9 | GERM-BO w64/k3 shuffled metadata | mechanism_ablation | 5 | 0.3772 +/- 0.0180 | 0.3022 +/- 0.0458 | 0.3560 / 0.3680 / 0.3737 / 0.4037 / 0.3847 |
| 10 | Baseline LoRA full target set | dnabert2_lora | 5 | 0.3853 +/- 0.0370 | 0.3016 +/- 0.0901 | 0.3740 / 0.3333 / 0.4287 / 0.3783 / 0.4123 |
| 11 | LoRA Wqkv + classifier | dnabert2_lora_baseline | 5 | 0.3714 +/- 0.0373 | 0.2834 +/- 0.1077 | 0.4100 / 0.3337 / 0.3330 / 0.3750 / 0.4053 |
| 12 | DNABERT-2 frozen linear probe | dnabert2_probe | 5 | 0.3433 +/- 0.0041 | 0.2035 +/- 0.0099 | 0.3493 / 0.3387 / 0.3417 / 0.3417 / 0.3450 |
| 13 | LoRA classifier only | dnabert2_lora_baseline | 5 | 0.3369 +/- 0.0016 | 0.1858 +/- 0.0064 | 0.3397 / 0.3363 / 0.3363 / 0.3367 / 0.3353 |

## Paired Deltas vs GERM-BO w64/k3/top10/scale3

| Method - Reference | Metric | Delta Mean | Bootstrap 95% CI | Win Rate | Per-Seed Delta |
|---|---|---:|---:|---:|---|
| 3-mer Linear SVM - GERM-BO w64/k3/top10/scale3 | test_accuracy | +0.0262 | [-0.0040, +0.0495] | 80.0% | +0.0397 / -0.0327 / +0.0383 / +0.0617 / +0.0240 |
| 3-mer Linear SVM - GERM-BO w64/k3/top10/scale3 | test_macro_f1 | +0.0729 | [+0.0155, +0.1249] | 80.0% | +0.0411 / -0.0328 / +0.1103 / +0.1578 / +0.0879 |
| 3-mer Logistic Regression - GERM-BO w64/k3/top10/scale3 | test_accuracy | +0.0323 | [+0.0013, +0.0564] | 80.0% | +0.0443 / -0.0283 / +0.0470 / +0.0697 / +0.0287 |
| 3-mer Logistic Regression - GERM-BO w64/k3/top10/scale3 | test_macro_f1 | +0.0762 | [+0.0173, +0.1297] | 80.0% | +0.0430 / -0.0310 / +0.1164 / +0.1630 / +0.0899 |
| 3-mer Multinomial NB - GERM-BO w64/k3/top10/scale3 | test_accuracy | -0.0129 | [-0.0443, +0.0113] | 40.0% | -0.0000 / -0.0743 / +0.0017 / +0.0240 / -0.0157 |
| 3-mer Multinomial NB - GERM-BO w64/k3/top10/scale3 | test_macro_f1 | +0.0009 | [-0.0582, +0.0543] | 60.0% | -0.0315 / -0.1072 / +0.0409 / +0.0871 / +0.0153 |
| 3-mer Nearest Centroid - GERM-BO w64/k3/top10/scale3 | test_accuracy | -0.0132 | [-0.0446, +0.0109] | 40.0% | -0.0003 / -0.0747 / +0.0013 / +0.0237 / -0.0160 |
| 3-mer Nearest Centroid - GERM-BO w64/k3/top10/scale3 | test_macro_f1 | +0.0121 | [-0.0470, +0.0654] | 60.0% | -0.0203 / -0.0960 / +0.0520 / +0.0983 / +0.0265 |
| Baseline LoRA full target set - GERM-BO w64/k3/top10/scale3 | test_accuracy | -0.0142 | [-0.0726, +0.0268] | 60.0% | -0.0127 / -0.1277 / +0.0437 / +0.0157 / +0.0100 |
| Baseline LoRA full target set - GERM-BO w64/k3/top10/scale3 | test_macro_f1 | -0.0515 | [-0.1797, +0.0505] | 60.0% | -0.1006 / -0.2945 / +0.0858 / +0.0231 / +0.0290 |
| DNABERT-2 frozen linear probe - GERM-BO w64/k3/top10/scale3 | test_accuracy | -0.0563 | [-0.0895, -0.0315] | 0.0% | -0.0373 / -0.1223 / -0.0433 / -0.0210 / -0.0573 |
| DNABERT-2 frozen linear probe - GERM-BO w64/k3/top10/scale3 | test_macro_f1 | -0.1496 | [-0.2096, -0.0972] | 0.0% | -0.1674 / -0.2678 / -0.1147 / -0.0680 / -0.1300 |
| GERM-BO quantile [0.8,1.2] comp0.27 - GERM-BO w64/k3/top10/scale3 | test_accuracy | +0.0152 | [-0.0210, +0.0548] | 60.0% | +0.0930 / -0.0230 / +0.0180 / +0.0230 / -0.0350 |
| GERM-BO quantile [0.8,1.2] comp0.27 - GERM-BO w64/k3/top10/scale3 | test_macro_f1 | +0.0185 | [-0.0421, +0.0791] | 60.0% | +0.0827 / -0.0379 / +0.0247 / +0.1028 / -0.0797 |
| GERM-BO w64/k3 comp=0 - GERM-BO w64/k3/top10/scale3 | test_accuracy | +0.0007 | [-0.0329, +0.0239] | 60.0% | +0.0203 / -0.0647 / +0.0183 / +0.0303 / -0.0010 |
| GERM-BO w64/k3 comp=0 - GERM-BO w64/k3/top10/scale3 | test_macro_f1 | -0.0112 | [-0.0678, +0.0325] | 60.0% | -0.0285 / -0.1184 / +0.0192 / +0.0444 / +0.0272 |
| GERM-BO w64/k3 shuffled metadata - GERM-BO w64/k3/top10/scale3 | test_accuracy | -0.0223 | [-0.0616, +0.0149] | 20.0% | -0.0307 / -0.0930 / -0.0113 / +0.0410 / -0.0177 |
| GERM-BO w64/k3 shuffled metadata - GERM-BO w64/k3/top10/scale3 | test_macro_f1 | -0.0508 | [-0.1211, +0.0194] | 20.0% | -0.1495 / -0.1335 / -0.0393 / +0.0784 / -0.0101 |
| LoRA Wqkv + classifier - GERM-BO w64/k3/top10/scale3 | test_accuracy | -0.0281 | [-0.0821, +0.0149] | 60.0% | +0.0233 / -0.1273 / -0.0520 / +0.0123 / +0.0030 |
| LoRA Wqkv + classifier - GERM-BO w64/k3/top10/scale3 | test_macro_f1 | -0.0697 | [-0.1848, +0.0333] | 40.0% | -0.0120 / -0.2815 / -0.1441 / +0.0245 / +0.0647 |
| LoRA attention.output + classifier - GERM-BO w64/k3/top10/scale3 | test_accuracy | +0.0007 | [-0.0329, +0.0239] | 60.0% | +0.0203 / -0.0647 / +0.0183 / +0.0303 / -0.0010 |
| LoRA attention.output + classifier - GERM-BO w64/k3/top10/scale3 | test_macro_f1 | -0.0112 | [-0.0678, +0.0325] | 60.0% | -0.0285 / -0.1184 / +0.0192 / +0.0444 / +0.0272 |
| LoRA classifier only - GERM-BO w64/k3/top10/scale3 | test_accuracy | -0.0627 | [-0.0939, -0.0386] | 0.0% | -0.0470 / -0.1247 / -0.0487 / -0.0260 / -0.0670 |
| LoRA classifier only - GERM-BO w64/k3/top10/scale3 | test_macro_f1 | -0.1673 | [-0.2252, -0.1110] | 0.0% | -0.1902 / -0.2778 / -0.1302 / -0.0783 / -0.1599 |
