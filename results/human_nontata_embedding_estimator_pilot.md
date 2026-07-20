# Human Non-TATA Promoters Frozen-Embedding Estimator Pilot

Protocol: frozen DNABERT-2 embedding-shift border estimator on Genomic Benchmarks `human_nontata_promoters`, pilot subset `2000/500/1000`, seeds `42-44`. The estimator is unsupervised and label-free: it computes token-window representation shift from the frozen pretrained backbone, normalizing scores with train-split statistics only.

## Summary

| Tag | Method | Acc Mean +/- Std | F1 Mean +/- Std | Per-Seed Acc |
|---|---|---:|---:|---|
| ctx_tw16_t10_s015 | embedding_metadata_estimated | 0.8130 +/- 0.0040 | 0.8316 +/- 0.0052 | 0.8090 / 0.8170 / 0.8130 |
| baseline_lora | baseline_lora | 0.8103 +/- 0.0021 | 0.8238 +/- 0.0071 | 0.8080 / 0.8120 / 0.8110 |
| emb_tw16_t10_s015 | embedding_metadata_estimated | 0.8097 +/- 0.0055 | 0.8279 +/- 0.0044 | 0.8150 / 0.8100 / 0.8040 |
| emb_tw8_t10_s015 | embedding_metadata_estimated | 0.8037 +/- 0.0067 | 0.8201 +/- 0.0035 | 0.8080 / 0.7960 / 0.8070 |
| ctx_tw8_t10_s015 | embedding_metadata_estimated | 0.8003 +/- 0.0231 | 0.8217 +/- 0.0161 | 0.7740 / 0.8100 / 0.8170 |

## Paired Deltas vs Baseline

| Tag | Metric | Delta Mean | Bootstrap 95% CI | Win Rate | Per-Seed Delta |
|---|---|---:|---:|---:|---|
| emb_tw8_t10_s015 | test_accuracy | -0.0067 | [-0.0160, +0.0000] | 0.0% | +0.0000 / -0.0160 / -0.0040 |
| emb_tw8_t10_s015 | test_f1 | -0.0037 | [-0.0141, +0.0071] | 33.3% | +0.0071 / -0.0141 / -0.0041 |
| emb_tw16_t10_s015 | test_accuracy | -0.0007 | [-0.0070, +0.0070] | 33.3% | +0.0070 / -0.0020 / -0.0070 |
| emb_tw16_t10_s015 | test_f1 | +0.0041 | [-0.0014, +0.0140] | 33.3% | +0.0140 / -0.0003 / -0.0014 |
| ctx_tw8_t10_s015 | test_accuracy | -0.0100 | [-0.0340, +0.0060] | 33.3% | -0.0340 / -0.0020 / +0.0060 |
| ctx_tw8_t10_s015 | test_f1 | -0.0020 | [-0.0133, +0.0081] | 33.3% | -0.0133 / -0.0009 / +0.0081 |
| ctx_tw16_t10_s015 | test_accuracy | +0.0027 | [+0.0010, +0.0050] | 100.0% | +0.0010 / +0.0050 / +0.0020 |
| ctx_tw16_t10_s015 | test_f1 | +0.0079 | [+0.0052, +0.0094] | 100.0% | +0.0094 / +0.0052 / +0.0090 |
