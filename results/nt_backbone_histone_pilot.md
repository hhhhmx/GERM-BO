# NT v2 50M Histone-Mark Pilot (seeds 42--44)

Protocol: ten histone ChIP-seq peak tasks, pilot subset `2000/500/1000`, Nucleotide Transformer v2 50M backbone, LoRA vs metadata-estimated GERM-BO.

| Task | NT LoRA Acc | NT GERM-BO Acc | ? Acc [95% CI] | DNABERT-2 ? Acc | Same sign? |
|---|---:|---:|---:|---:|---|
| H3 | 0.7917 | 0.7880 | -0.0037 [-0.0070, +0.0000] | +0.0083 | no |
| H3K14ac | 0.6307 | 0.6283 | -0.0023 [-0.0100, +0.0030] | +0.0727 | no |
| H3K36me3 | 0.6813 | 0.6767 | -0.0047 [-0.0110, +0.0010] | +0.0167 | no |
| H3K4me1 | 0.6167 | 0.6153 | -0.0013 [-0.0050, +0.0020] | -0.0147 | yes |
| H3K4me2 | 0.6020 | 0.6060 | +0.0040 [+0.0000, +0.0110] | +0.0310 | yes |
| H3K4me3 | 0.5657 | 0.5643 | -0.0013 [-0.0070, +0.0020] | +0.0117 | no |
| H3K79me3 | 0.7333 | 0.7340 | +0.0007 [-0.0020, +0.0030] | +0.0130 | yes |
| H3K9ac | 0.6530 | 0.6483 | -0.0047 [-0.0080, +0.0000] | +0.0310 | no |
| H4 | 0.8423 | 0.8373 | -0.0050 [-0.0120, +0.0000] | -0.0513 | yes |
| H4ac | 0.5837 | 0.5967 | +0.0130 [+0.0080, +0.0180] | -0.0073 | no |

NT v2 50M tasks with positive mean GERM-BO delta: 3/10.
