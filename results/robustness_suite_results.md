# Robustness Suite Results

## Expanded Datasets and Tasks

This robustness batch extends the earlier main-line experiments in three ways:

- it scales the original file-based setup to a larger `primary` split (`512/128/128`)
- it adds a harder `hard_border` task with stronger border sensitivity
- it probes a targeted GERM-BO grid over `compensation_strength` and `target_modules`

All runs were executed on `gpu-server` under the same constraints:

- explicit `CUDA_VISIBLE_DEVICES=3`
- single visible GPU only
- no DDP, `DataParallel`, DeepSpeed, or FSDP
- real `DNABERT-2-117M` backbone

## Result Table

| Dataset | Method | Variant | Compensation | Target Scope | Accuracy | F1 | Loss |
| --- | --- | --- | --- | --- | ---: | ---: | ---: |
| `splits_large_primary` | baseline LoRA | default | - | attn2 + classifier | 0.5000 | 0.6667 | 0.6933 |
| `splits_large_primary` | GERM-BO | mild default | 0.3 | attn2 + classifier | 0.8203 | 0.7850 | 0.5588 |
| `splits_hard_border` | baseline LoRA | default | - | attn2 + classifier | 0.5000 | 0.6667 | 0.6940 |
| `splits_hard_border` | GERM-BO | mild default | 0.3 | attn2 + classifier | 0.5078 | 0.1370 | 0.7551 |
| `splits_hard_border` | GERM-BO | lowcomp | 0.2 | attn2 + classifier | 0.8984 | 0.8926 | 0.5179 |
| `splits_hard_border` | GERM-BO | highcomp | 0.4 | attn2 + classifier | 0.5000 | 0.0000 | 0.6932 |
| `splits_hard_border` | GERM-BO | mlp expanded | 0.3 | attn2 + mlp2 + classifier | 0.5000 | 0.6667 | 0.6990 |

## Interpretation

The robustness picture is now sharper than before.

On the larger `primary` split, the formal mild GERM-BO setting remains clearly better than the baseline. This supports the earlier conclusion that the method is not winning only because of a tiny split or an accidental pilot.

On the harder `hard_border` task, the default mild setting does not remain stable. A lower `compensation_strength=0.2` is dramatically better than both the baseline and the default `0.3` setting, while a higher `0.4` setting collapses. This indicates that the compensation mechanism is useful on the harder task, but only inside a narrower strength range.

The `attention + MLP` expanded target-layer variant does not help on the current `hard_border` task. In this robustness batch, widening the intervention scope is worse than keeping the compensation localized to the first two attention blocks.

## Practical Conclusion

The current results support a two-level conclusion:

- `configs/real_dnabert2_germ_bo_pilot.yaml` remains a reasonable default for the previously validated main-line setting
- for harder border-sensitive tasks, a lower-compensation setting is more robust than the current default

If this robustness branch is promoted into the paper's main ablation, the next clean follow-up would be to treat `compensation_strength=0.2` as the hard-task candidate default and verify it with a small multi-seed repeat on `splits_hard_border`.
