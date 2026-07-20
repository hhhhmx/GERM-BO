# Statistical Significance: Metadata-Driven Mechanism

Protocol: paired comparison on held-out seeds `47-54`. The combined group contains `border_medium` and `border_hard` pairs. P-values are reported as paired t-test normal approximation and exact Wilcoxon signed-rank test. Bootstrap CIs are 20,000-sample paired bootstrap intervals over mean deltas.

## combined

| Metric | Comparison | Mean A +/- Std | Mean B +/- Std | Delta | t-test p | Wilcoxon p | Bootstrap 95% CI | Win Rate |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| accuracy | metadata-driven comp=0.27/p4 vs activation-derived comp=0.27/p4 | 0.9272 +/- 0.0583 | 0.8757 +/- 0.0543 | +0.0515 | 0.0196 | 0.0259 | [+0.0095, +0.0920] | 75.0% |
| f1 | metadata-driven comp=0.27/p4 vs activation-derived comp=0.27/p4 | 0.9251 +/- 0.0613 | 0.8768 +/- 0.0532 | +0.0482 | 0.0315 | 0.0386 | [+0.0054, +0.0894] | 75.0% |
| precision | metadata-driven comp=0.27/p4 vs activation-derived comp=0.27/p4 | 0.9423 +/- 0.0539 | 0.8741 +/- 0.0673 | +0.0682 | 0.0044 | 0.0092 | [+0.0216, +0.1128] | 81.2% |
| recall | metadata-driven comp=0.27/p4 vs activation-derived comp=0.27/p4 | 0.9102 +/- 0.0774 | 0.8818 +/- 0.0565 | +0.0283 | 0.2685 | 0.2025 | [-0.0225, +0.0742] | 62.5% |
| accuracy | metadata-driven comp=0.27/p4 vs no compensation comp=0.00/p4 | 0.9272 +/- 0.0583 | 0.8706 +/- 0.0685 | +0.0566 | 0.0012 | 0.0179 | [+0.0227, +0.0896] | 68.8% |
| f1 | metadata-driven comp=0.27/p4 vs no compensation comp=0.00/p4 | 0.9251 +/- 0.0613 | 0.8741 +/- 0.0601 | +0.0510 | 0.0021 | 0.0181 | [+0.0177, +0.0808] | 68.8% |
| precision | metadata-driven comp=0.27/p4 vs no compensation comp=0.00/p4 | 0.9423 +/- 0.0539 | 0.8619 +/- 0.0747 | +0.0804 | 0.0000 | 0.0004 | [+0.0454, +0.1194] | 87.5% |
| recall | metadata-driven comp=0.27/p4 vs no compensation comp=0.00/p4 | 0.9102 +/- 0.0774 | 0.8887 +/- 0.0540 | +0.0215 | 0.2996 | 0.1925 | [-0.0205, +0.0576] | 68.8% |
| accuracy | activation-derived comp=0.27/p4 vs no compensation comp=0.00/p4 | 0.8757 +/- 0.0543 | 0.8706 +/- 0.0685 | +0.0051 | 0.7903 | 0.9017 | [-0.0276, +0.0452] | 50.0% |
| f1 | activation-derived comp=0.27/p4 vs no compensation comp=0.00/p4 | 0.8768 +/- 0.0532 | 0.8741 +/- 0.0601 | +0.0028 | 0.8757 | 0.9399 | [-0.0279, +0.0389] | 50.0% |
| precision | activation-derived comp=0.27/p4 vs no compensation comp=0.00/p4 | 0.8741 +/- 0.0673 | 0.8619 +/- 0.0747 | +0.0122 | 0.5432 | 0.8603 | [-0.0237, +0.0525] | 56.2% |
| recall | activation-derived comp=0.27/p4 vs no compensation comp=0.00/p4 | 0.8818 +/- 0.0565 | 0.8887 +/- 0.0540 | -0.0068 | 0.7245 | 0.6591 | [-0.0420, +0.0317] | 43.8% |

## border_medium

| Metric | Comparison | Mean A +/- Std | Mean B +/- Std | Delta | t-test p | Wilcoxon p | Bootstrap 95% CI | Win Rate |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| accuracy | metadata-driven comp=0.27/p4 vs activation-derived comp=0.27/p4 | 0.9258 +/- 0.0652 | 0.9175 +/- 0.0168 | +0.0083 | 0.7350 | 0.2656 | [-0.0420, +0.0459] | 75.0% |
| f1 | metadata-driven comp=0.27/p4 vs activation-derived comp=0.27/p4 | 0.9238 +/- 0.0675 | 0.9161 +/- 0.0180 | +0.0077 | 0.7587 | 0.3125 | [-0.0439, +0.0461] | 75.0% |
| precision | metadata-driven comp=0.27/p4 vs activation-derived comp=0.27/p4 | 0.9406 +/- 0.0633 | 0.9308 +/- 0.0272 | +0.0098 | 0.7232 | 0.5469 | [-0.0438, +0.0552] | 62.5% |
| recall | metadata-driven comp=0.27/p4 vs activation-derived comp=0.27/p4 | 0.9092 +/- 0.0818 | 0.9033 +/- 0.0383 | +0.0059 | 0.8397 | 0.5938 | [-0.0508, +0.0547] | 50.0% |
| accuracy | metadata-driven comp=0.27/p4 vs no compensation comp=0.00/p4 | 0.9258 +/- 0.0652 | 0.9077 +/- 0.0153 | +0.0181 | 0.4138 | 0.6406 | [-0.0239, +0.0562] | 50.0% |
| f1 | metadata-driven comp=0.27/p4 vs no compensation comp=0.00/p4 | 0.9238 +/- 0.0675 | 0.9092 +/- 0.0142 | +0.0146 | 0.5345 | 0.6406 | [-0.0303, +0.0554] | 50.0% |
| precision | metadata-driven comp=0.27/p4 vs no compensation comp=0.00/p4 | 0.9406 +/- 0.0633 | 0.8969 +/- 0.0294 | +0.0437 | 0.0270 | 0.0547 | [+0.0082, +0.0798] | 87.5% |
| recall | metadata-driven comp=0.27/p4 vs no compensation comp=0.00/p4 | 0.9092 +/- 0.0818 | 0.9229 +/- 0.0245 | -0.0137 | 0.7010 | 0.8750 | [-0.0811, +0.0479] | 50.0% |
| accuracy | activation-derived comp=0.27/p4 vs no compensation comp=0.00/p4 | 0.9175 +/- 0.0168 | 0.9077 +/- 0.0153 | +0.0098 | 0.3613 | 0.4141 | [-0.0103, +0.0293] | 62.5% |
| f1 | activation-derived comp=0.27/p4 vs no compensation comp=0.00/p4 | 0.9161 +/- 0.0180 | 0.9092 +/- 0.0142 | +0.0069 | 0.5277 | 0.4609 | [-0.0135, +0.0267] | 62.5% |
| precision | activation-derived comp=0.27/p4 vs no compensation comp=0.00/p4 | 0.9308 +/- 0.0272 | 0.8969 +/- 0.0294 | +0.0339 | 0.0263 | 0.0781 | [+0.0054, +0.0615] | 75.0% |
| recall | activation-derived comp=0.27/p4 vs no compensation comp=0.00/p4 | 0.9033 +/- 0.0383 | 0.9229 +/- 0.0245 | -0.0195 | 0.3281 | 0.5312 | [-0.0576, +0.0146] | 37.5% |

## border_hard

| Metric | Comparison | Mean A +/- Std | Mean B +/- Std | Delta | t-test p | Wilcoxon p | Bootstrap 95% CI | Win Rate |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| accuracy | metadata-driven comp=0.27/p4 vs activation-derived comp=0.27/p4 | 0.9287 +/- 0.0550 | 0.8340 +/- 0.0453 | +0.0947 | 0.0021 | 0.0391 | [+0.0371, +0.1494] | 75.0% |
| f1 | metadata-driven comp=0.27/p4 vs activation-derived comp=0.27/p4 | 0.9264 +/- 0.0590 | 0.8376 +/- 0.0471 | +0.0888 | 0.0063 | 0.0391 | [+0.0270, +0.1450] | 75.0% |
| precision | metadata-driven comp=0.27/p4 vs activation-derived comp=0.27/p4 | 0.9440 +/- 0.0469 | 0.8173 +/- 0.0402 | +0.1266 | 0.0000 | 0.0078 | [+0.0799, +0.1768] | 100.0% |
| recall | metadata-driven comp=0.27/p4 vs activation-derived comp=0.27/p4 | 0.9111 +/- 0.0785 | 0.8604 +/- 0.0657 | +0.0508 | 0.2345 | 0.3125 | [-0.0332, +0.1211] | 75.0% |
| accuracy | metadata-driven comp=0.27/p4 vs no compensation comp=0.00/p4 | 0.9287 +/- 0.0550 | 0.8335 +/- 0.0816 | +0.0952 | 0.0000 | 0.0156 | [+0.0601, +0.1328] | 87.5% |
| f1 | metadata-driven comp=0.27/p4 vs no compensation comp=0.00/p4 | 0.9264 +/- 0.0590 | 0.8390 +/- 0.0687 | +0.0874 | 0.0000 | 0.0156 | [+0.0577, +0.1144] | 87.5% |
| precision | metadata-driven comp=0.27/p4 vs no compensation comp=0.00/p4 | 0.9440 +/- 0.0469 | 0.8268 +/- 0.0910 | +0.1171 | 0.0000 | 0.0156 | [+0.0684, +0.1740] | 87.5% |
| recall | metadata-driven comp=0.27/p4 vs no compensation comp=0.00/p4 | 0.9111 +/- 0.0785 | 0.8545 +/- 0.0546 | +0.0566 | 0.0001 | 0.0156 | [+0.0293, +0.0840] | 87.5% |
| accuracy | activation-derived comp=0.27/p4 vs no compensation comp=0.00/p4 | 0.8340 +/- 0.0453 | 0.8335 +/- 0.0816 | +0.0005 | 0.9899 | 0.5312 | [-0.0591, +0.0786] | 37.5% |
| f1 | activation-derived comp=0.27/p4 vs no compensation comp=0.00/p4 | 0.8376 +/- 0.0471 | 0.8390 +/- 0.0687 | -0.0014 | 0.9681 | 0.5469 | [-0.0569, +0.0687] | 37.5% |
| precision | activation-derived comp=0.27/p4 vs no compensation comp=0.00/p4 | 0.8173 +/- 0.0402 | 0.8268 +/- 0.0910 | -0.0095 | 0.7965 | 0.3828 | [-0.0664, +0.0659] | 37.5% |
| recall | activation-derived comp=0.27/p4 vs no compensation comp=0.00/p4 | 0.8604 +/- 0.0657 | 0.8545 +/- 0.0546 | +0.0059 | 0.8639 | 1.0000 | [-0.0527, +0.0723] | 50.0% |

## Main Interpretation

Metadata-driven compensation improves combined accuracy over activation-derived compensation by `+0.0515` with bootstrap CI `[+0.0095, +0.0920]`. The largest gain is on `border_hard`, where accuracy delta is `+0.0947`.
