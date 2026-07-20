# Real Benchmark Pilot: UCI Promoter

Protocol: UCI Molecular Biology Promoter dataset, real DNABERT-2 backbone, single GPU, seeds `42-46`, validation-accuracy best checkpoint, and validation-threshold tuned test evaluation. This is a pilot benchmark, not a final large-scale external validation.

## Summary

| Method | Seeds | Test Acc Mean +/- Std | Test F1 Mean +/- Std | Per-Seed Acc |
|---|---:|---:|---:|---|
| Baseline LoRA | 5 | 0.6000 +/- 0.0342 | 0.6490 +/- 0.0494 | 0.6250 / 0.5625 / 0.6250 / 0.6250 / 0.5625 |
| GERM-BO activation-derived | 5 | 0.6125 +/- 0.1677 | 0.5856 +/- 0.2149 | 0.8750 / 0.6875 / 0.5000 / 0.5000 / 0.5000 |
| GERM-BO metadata-driven | 5 | 0.5750 +/- 0.1118 | 0.6129 +/- 0.1382 | 0.5625 / 0.5625 / 0.7500 / 0.5625 / 0.4375 |

## Paired Pilot Deltas

| Comparison | Metric | Delta Mean | Bootstrap 95% CI | Win Rate | Per-Seed Delta |
|---|---|---:|---:|---:|---|
| germ_bo_metadata_minus_baseline_lora | test_accuracy | -0.0250 | [-0.0875, +0.0500] | 20.0% | -0.0625 / +0.0000 / +0.1250 / -0.0625 / -0.1250 |
| germ_bo_metadata_minus_baseline_lora | test_f1 | -0.0361 | [-0.1203, +0.0333] | 20.0% | -0.0333 / +0.0000 / +0.0778 / -0.0368 / -0.1882 |
| germ_bo_metadata_minus_germ_bo_activation | test_accuracy | -0.0375 | [-0.2000, +0.1375] | 40.0% | -0.3125 / -0.1250 / +0.2500 / +0.0625 / -0.0625 |
| germ_bo_metadata_minus_germ_bo_activation | test_f1 | +0.0272 | [-0.1437, +0.2399] | 40.0% | -0.2222 / -0.0743 / +0.4444 / +0.0882 / -0.1000 |
| germ_bo_activation_minus_baseline_lora | test_accuracy | +0.0125 | [-0.1125, +0.1500] | 40.0% | +0.2500 / +0.1250 / -0.1250 / -0.1250 / -0.0625 |
| germ_bo_activation_minus_baseline_lora | test_f1 | -0.0633 | [-0.2301, +0.0972] | 40.0% | +0.1889 / +0.0743 / -0.3667 / -0.1250 / -0.0882 |
