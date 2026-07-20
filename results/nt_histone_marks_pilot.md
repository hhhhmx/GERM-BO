# NT Histone-Mark Pilot (excluding H3K4me3)

Protocol: nine histone ChIP-seq peak tasks from `InstaDeepAI/nucleotide_transformer_downstream_tasks`, pilot subset `2000/500/1000`, seeds `42-44`, DNABERT-2 LoRA vs metadata-estimated GERM-BO.

## Summary Table

| Task | LoRA Acc | GERM-BO Acc | ? Acc | LoRA F1 | GERM-BO F1 | ? F1 | Win Rate (Acc) |
|---|---:|---:|---:|---:|---:|---:|---:|
| H3 | 0.7750 | 0.7833 | +0.0083 | 0.7688 | 0.7776 | +0.0088 | 67% |
| H3K14ac | 0.5923 | 0.6650 | +0.0727 | 0.5269 | 0.6599 | +0.1330 | 67% |
| H3K36me3 | 0.6843 | 0.7010 | +0.0167 | 0.6669 | 0.6973 | +0.0303 | 33% |
| H3K4me1 | 0.6733 | 0.6587 | -0.0147 | 0.6726 | 0.6577 | -0.0149 | 0% |
| H3K4me2 | 0.5927 | 0.6237 | +0.0310 | 0.5400 | 0.6203 | +0.0803 | 67% |
| H3K79me3 | 0.7430 | 0.7560 | +0.0130 | 0.7417 | 0.7530 | +0.0112 | 33% |
| H3K9ac | 0.6590 | 0.6900 | +0.0310 | 0.6288 | 0.6840 | +0.0552 | 33% |
| H4 | 0.8793 | 0.8280 | -0.0513 | 0.8793 | 0.8256 | -0.0536 | 0% |
| H4ac | 0.6383 | 0.6310 | -0.0073 | 0.6319 | 0.6227 | -0.0092 | 33% |

GERM-BO wins on accuracy (mean delta > 0): 6/9 tasks.
