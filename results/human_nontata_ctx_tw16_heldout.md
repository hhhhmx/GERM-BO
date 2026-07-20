# Human Non-TATA Promoters Contextual TW16 Held-Out Confirmation

Protocol: held-out seeds `45-49` on Genomic Benchmarks `human_nontata_promoters`, pilot subset `2000/500/1000`, real DNABERT-2 backbone, validation-accuracy best checkpoint, and validation-threshold tuned test evaluation. The candidate estimator is frozen contextual DNABERT-2 representation shift with `token_window=16`, `top_ratio=0.10`, `score_scale=0.15`.

## Summary

| Method | Seeds | Test Acc Mean +/- Std | Test F1 Mean +/- Std | Per-Seed Acc |
|---|---:|---:|---:|---|
| Baseline LoRA | 5 | 0.8178 +/- 0.0034 | 0.8360 +/- 0.0055 | 0.8220 / 0.8150 / 0.8160 / 0.8150 / 0.8210 |
| Contextual DNABERT-2 shift ctx_tw16_t10_s015 | 5 | 0.8136 +/- 0.0064 | 0.8299 +/- 0.0071 | 0.8090 / 0.8220 / 0.8190 / 0.8100 / 0.8080 |

## Paired Deltas

| Comparison | Metric | Delta Mean | Bootstrap 95% CI | Win Rate | Per-Seed Delta |
|---|---|---:|---:|---:|---|
| ctx_tw16_t10_s015_minus_baseline_lora | test_accuracy | -0.0042 | [-0.0114, +0.0030] | 40.0% | -0.0130 / +0.0070 / +0.0030 / -0.0050 / -0.0130 |
| ctx_tw16_t10_s015_minus_baseline_lora | test_f1 | -0.0061 | [-0.0145, +0.0034] | 40.0% | -0.0164 / +0.0110 / +0.0005 / -0.0116 / -0.0139 |
