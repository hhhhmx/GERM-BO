# Extended Seed Validation on Enlarged Hard-Border Split

Protocol: real DNABERT-2-117M backbone, enlarged hard-border split, seeds `42/43/44/45/46/47/48/49`, validation-accuracy best checkpoint, early stopping patience 2, and validation-threshold tuned test evaluation. The new remote runs for seeds `45-49` explicitly used `CUDA_VISIBLE_DEVICES=3` and reported one visible GPU.

| Method | Test accuracy mean +/- std | Test F1 mean +/- std | Paired accuracy delta vs baseline | Per-seed test accuracy |
|---|---:|---:|---:|---:|
| Baseline LoRA | 0.8257 +/- 0.0608 | 0.8145 +/- 0.0872 | 0.0000 +/- 0.0000 | 0.8281 / 0.8477 / 0.8438 / 0.8828 / 0.7344 / 0.7305 / 0.8867 / 0.8516 |
| GERM-BO main: Wqkv + classifier | 0.8896 +/- 0.0291 | 0.8897 +/- 0.0297 | +0.0640 +/- 0.0725 | 0.8672 / 0.8828 / 0.9062 / 0.8594 / 0.8555 / 0.9414 / 0.8984 / 0.9062 |
| GERM-BO candidate: attention.output + classifier | 0.8965 +/- 0.0284 | 0.8964 +/- 0.0286 | +0.0708 +/- 0.0726 | 0.9102 / 0.9219 / 0.8477 / 0.8984 / 0.9297 / 0.8906 / 0.9102 / 0.8633 |

Per-seed paired accuracy deltas:

| Method | Seeds 42/43/44/45/46/47/48/49 |
|---|---:|
| GERM-BO main: Wqkv + classifier | +0.0391 / +0.0352 / +0.0625 / -0.0234 / +0.1211 / +0.2109 / +0.0117 / +0.0547 |
| GERM-BO candidate: attention.output + classifier | +0.0820 / +0.0742 / +0.0039 / +0.0156 / +0.1953 / +0.1602 / +0.0234 / +0.0117 |

Conclusion: both GERM-BO target-module choices remain clearly above the matched baseline after extending to 8 seeds. `Wqkv + classifier` remains a defensible robust main configuration because its accuracy variance is much lower than the baseline's (`0.0291` vs `0.0608`) and it improves mean accuracy by `+0.0640`. The `attention.output + classifier` candidate now has the best mean accuracy (`0.8965`) and similar variance to Wqkv (`0.0284`), so it is no longer just a high-variance candidate; it should be promoted to a serious final-candidate configuration, but `Wqkv + classifier` is still safer as the primary claim unless one more validation round confirms the candidate.

Artifact note: during the seeds `45-49` run, the remote output JSON filenames used `$seed_threshold`-style shell expansion and were overwritten per method. The per-seed metrics above come from the completed remote command outputs, and the summary CSV/Markdown files are the authoritative records for this extended seed validation.
