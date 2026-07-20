# NT Downstream Held-Out Confirmation (heldout)

Protocol: ten histone ChIP-seq peak tasks plus `enhancers` from `InstaDeepAI/nucleotide_transformer_downstream_tasks`, pilot subset `2000/500/1000`, seeds `45-49`, DNABERT-2 LoRA vs metadata-estimated GERM-BO (train-quantile center-window k-mer JSD).

| Task | Category | LoRA Acc | GERM-BO Acc | ? Acc [95% CI] | Win Rate |
|---|---|---:|---:|---:|---:|
| H3 | histone | 0.8182 | 0.7640 | -0.0542 [-0.1922, +0.0316] | 40% |
| H3K14ac | histone | 0.6654 | 0.6594 | -0.0060 [-0.0346, +0.0206] | 40% |
| H3K36me3 | histone | 0.7038 | 0.7084 | +0.0046 [-0.0228, +0.0404] | 40% |
| H3K4me1 | histone | 0.6380 | 0.6522 | +0.0142 [-0.0028, +0.0310] | 60% |
| H3K4me2 | histone | 0.6262 | 0.6328 | +0.0066 [-0.0148, +0.0300] | 60% |
| H3K4me3 | histone | 0.5568 | 0.5536 | -0.0032 [-0.0370, +0.0302] | 40% |
| H3K79me3 | histone | 0.7356 | 0.7342 | -0.0014 [-0.0558, +0.0648] | 40% |
| H3K9ac | histone | 0.6544 | 0.6794 | +0.0250 [-0.0194, +0.0666] | 60% |
| H4 | histone | 0.7998 | 0.8542 | +0.0544 [-0.0162, +0.1338] | 60% |
| H4ac | histone | 0.5768 | 0.5774 | +0.0006 [-0.0462, +0.0404] | 60% |
| enhancers | regulatory | 0.7395 | 0.7325 | -0.0070 [-0.0150, +0.0010] | 40% |

Histone marks with positive mean accuracy delta: 6/10. Tasks with bootstrap 95% CI excluding zero: 0/10.
