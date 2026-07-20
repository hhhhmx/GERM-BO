# Final-Candidate Confirmation: Seeds 50-54

Protocol: real DNABERT-2-117M backbone, enlarged hard-border split, validation-accuracy best checkpoint, early stopping patience 2, and validation-threshold tuned test evaluation. All new remote runs used `CUDA_VISIBLE_DEVICES=3` and reported one visible GPU. Result filenames were fixed to use `${seed}`, producing one independent JSON per seed.

## Confirmation Run

| Method | Seeds | Test accuracy mean +/- std | Test F1 mean +/- std | Per-seed test accuracy |
|---|---|---:|---:|---:|
| GERM-BO main: Wqkv + classifier | 50/51/52/53/54 | 0.8320 +/- 0.0927 | 0.8370 +/- 0.0819 | 0.8906 / 0.6758 / 0.8633 / 0.9062 / 0.8242 |
| GERM-BO candidate: attention.output + classifier | 50/51/52/53/54 | 0.8844 +/- 0.0208 | 0.8788 +/- 0.0248 | 0.9062 / 0.9023 / 0.8828 / 0.8555 / 0.8750 |

Paired accuracy delta of `attention.output + classifier` over `Wqkv + classifier` on seeds 50-54: `+0.0523 +/- 0.1042`, with per-seed deltas `+0.0156 / +0.2266 / +0.0195 / -0.0508 / +0.0508`.

## Combined 13-Seed View

| Method | Seeds | Test accuracy mean +/- std | Test F1 mean +/- std | Per-seed test accuracy |
|---|---|---:|---:|---:|
| GERM-BO main: Wqkv + classifier | 42-54 | 0.8675 +/- 0.0649 | 0.8695 +/- 0.0588 | 0.8672 / 0.8828 / 0.9062 / 0.8594 / 0.8555 / 0.9414 / 0.8984 / 0.9062 / 0.8906 / 0.6758 / 0.8633 / 0.9062 / 0.8242 |
| GERM-BO candidate: attention.output + classifier | 42-54 | 0.8918 +/- 0.0255 | 0.8896 +/- 0.0276 | 0.9102 / 0.9219 / 0.8477 / 0.8984 / 0.9297 / 0.8906 / 0.9102 / 0.8633 / 0.9062 / 0.9023 / 0.8828 / 0.8555 / 0.8750 |

Conclusion: the confirmation run changes the configuration decision. `Wqkv + classifier` is no longer the safer choice because seed 51 collapses to `0.6758`, raising the 13-seed std to `0.0649`. `attention.output + classifier` now has both the higher 13-seed mean accuracy (`0.8918` vs `0.8675`) and much lower variance (`0.0255` vs `0.0649`). Therefore, `attention.output + classifier` is promoted to the final main configuration, and `Wqkv + classifier` is demoted to an ablation/secondary result.
