# Human Non-TATA Promoters W64 Held-Out Confirmation

Protocol: held-out seeds `45-49` on Genomic Benchmarks `human_nontata_promoters`, pilot subset `2000/500/1000`, real DNABERT-2 backbone, validation-accuracy best checkpoint, and validation-threshold tuned test evaluation. The candidate estimator is label-free `window=64`, `kmer=2`, `top_ratio=0.10`, `score_scale=3.0`.

## Summary

| Method | Seeds | Test Acc Mean +/- Std | Test F1 Mean +/- Std | Per-Seed Acc |
|---|---:|---:|---:|---|
| Baseline LoRA | 5 | 0.8178 +/- 0.0034 | 0.8360 +/- 0.0055 | 0.8220 / 0.8150 / 0.8160 / 0.8150 / 0.8210 |
| Metadata-estimated GERM-BO w64_k2_t10_s3 | 5 | 0.8168 +/- 0.0032 | 0.8359 +/- 0.0040 | 0.8170 / 0.8210 / 0.8170 / 0.8170 / 0.8120 |

## Paired Deltas

| Comparison | Metric | Delta Mean | Bootstrap 95% CI | Win Rate | Per-Seed Delta |
|---|---|---:|---:|---:|---|
| metadata_w64_k2_t10_s3_minus_baseline_lora | test_accuracy | -0.0010 | [-0.0058, +0.0034] | 60.0% | -0.0050 / +0.0060 / +0.0010 / +0.0020 / -0.0090 |
| metadata_w64_k2_t10_s3_minus_baseline_lora | test_f1 | -0.0001 | [-0.0068, +0.0078] | 40.0% | -0.0014 / +0.0140 / +0.0007 / -0.0032 / -0.0106 |
