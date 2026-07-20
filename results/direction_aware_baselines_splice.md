# Direction-Aware PEFT Baselines on Strict 3-mer-Balanced Splice Split

Protocol: held-out seeds 50--54, same target modules as LoRA-ATT (`attention.output + classifier`), rank 8, lr 3e-4.

## Summary

| Method | Seeds | Test Acc Mean +/- Std | Test Macro-F1 Mean +/- Std | Per-Seed Acc |
|---|---:|---:|---:|---|
| Gated LoRA attention.output + classifier | 5 | 0.3606 +/- 0.0227 | 0.2769 +/- 0.0781 | 0.3889 / 0.3350 / 0.3733 / 0.3322 / 0.3733 |
| GERM-BO activation-derived comp0.27 | 5 | 0.3709 +/- 0.0129 | 0.3112 +/- 0.0440 | 0.3750 / 0.3578 / 0.3733 / 0.3917 / 0.3567 |
