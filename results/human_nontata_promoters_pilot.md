# Real Benchmark Pilot: Human Non-TATA Promoters

Protocol: Genomic Benchmarks `human_nontata_promoters`, real DNABERT-2 backbone, single GPU, train/val/test pilot subset `2000/500/1000`, seeds `42-44`, validation-accuracy best checkpoint, and validation-threshold tuned test evaluation. Metadata-estimated GERM-BO uses a label-free sequence-only k-mer JSD border-score estimator.

## Summary

| Method | Seeds | Test Acc Mean +/- Std | Test F1 Mean +/- Std | Per-Seed Acc |
|---|---:|---:|---:|---|
| Baseline LoRA | 3 | 0.8103 +/- 0.0021 | 0.8238 +/- 0.0071 | 0.8080 / 0.8120 / 0.8110 |
| GERM-BO activation-derived | 3 | 0.8090 +/- 0.0151 | 0.8289 +/- 0.0119 | 0.8210 / 0.8140 / 0.7920 |
| GERM-BO metadata-estimated | 3 | 0.7993 +/- 0.0184 | 0.8207 +/- 0.0148 | 0.7790 / 0.8150 / 0.8040 |

## Paired Deltas

| Comparison | Metric | Delta Mean | Bootstrap 95% CI | Win Rate | Per-Seed Delta |
|---|---|---:|---:|---:|---|
| germ_bo_metadata_estimated_minus_baseline_lora | test_accuracy | -0.0110 | [-0.0290, +0.0030] | 33.3% | -0.0290 / +0.0030 / -0.0070 |
| germ_bo_metadata_estimated_minus_baseline_lora | test_f1 | -0.0031 | [-0.0108, +0.0046] | 33.3% | -0.0108 / +0.0046 / -0.0030 |
| germ_bo_metadata_estimated_minus_germ_bo_activation | test_accuracy | -0.0097 | [-0.0420, +0.0120] | 66.7% | -0.0420 / +0.0010 / +0.0120 |
| germ_bo_metadata_estimated_minus_germ_bo_activation | test_f1 | -0.0082 | [-0.0330, +0.0056] | 66.7% | -0.0330 / +0.0028 / +0.0056 |
| germ_bo_activation_minus_baseline_lora | test_accuracy | -0.0013 | [-0.0190, +0.0130] | 66.7% | +0.0130 / +0.0020 / -0.0190 |
| germ_bo_activation_minus_baseline_lora | test_f1 | +0.0051 | [-0.0086, +0.0221] | 66.7% | +0.0221 / +0.0018 / -0.0086 |
