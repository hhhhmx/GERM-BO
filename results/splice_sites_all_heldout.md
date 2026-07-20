# Splice Sites All Held-Out Confirmation

Protocol: Hugging Face `InstaDeepAI/nucleotide_transformer_downstream_tasks/splice_sites_all`, 3-class splice-site classification, same pilot subset `3000/600/1200`, held-out seeds `45-49`, real DNABERT-2 backbone, validation-accuracy best checkpoint, and argmax test evaluation. Metadata-estimated GERM-BO uses the label-free center-window k-mer JSD score.

## Summary

| Method | Seeds | Test Acc Mean +/- Std | Test Macro-F1 Mean +/- Std | Per-Seed Acc |
|---|---:|---:|---:|---|
| Baseline LoRA | 5 | 0.3815 +/- 0.0289 | 0.2930 +/- 0.0823 | 0.3333 / 0.3983 / 0.4083 / 0.3808 / 0.3867 |
| Metadata-estimated GERM-BO center-JSD | 5 | 0.3863 +/- 0.0284 | 0.3297 +/- 0.0665 | 0.3908 / 0.3750 / 0.4208 / 0.3450 / 0.4000 |

## Paired Deltas

| Comparison | Metric | Delta Mean | Bootstrap 95% CI | Win Rate | Per-Seed Delta |
|---|---|---:|---:|---:|---|
| germ_bo_center_jsd_minus_baseline_lora | test_accuracy | +0.0048 | [-0.0235, +0.0323] | 60.0% | +0.0575 / -0.0233 / +0.0125 / -0.0358 / +0.0133 |
| germ_bo_center_jsd_minus_baseline_lora | test_macro_f1 | +0.0368 | [-0.0342, +0.1197] | 40.0% | +0.1984 / -0.0037 / -0.0141 / -0.0695 / +0.0728 |
