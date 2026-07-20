# Retention Ratio R_w(tau) Calibration (Trained-checkpoint)

Empirical estimate: R_emp = E[phi_tau(a)^2 g^2]/E[g^2] at layer-0 attention output.

## Summary

| Split | Model | tau* | R at tau* (low / high) | tau_med | R at tau_med (low / high) | Spearman_med |
|---|---|---:|---:|---:|---:|---:|
| border_hard | GERM-BO | 0.1845 | 1.000 / 0.999 | 0.1195 | 0.209 / 0.034 | -0.200 |
| border_hard | LoRA | 0.1755 | 1.000 / 1.000 | 0.1068 | 0.637 / 0.960 | 0.000 |
| hard_border_large | GERM-BO | 0.1776 | 1.000 / 1.000 | 0.1121 | 0.715 / 0.715 | 0.000 |
| hard_border_large | LoRA | 0.1685 | 1.000 / 1.000 | 0.1046 | 0.935 / 0.621 | -1.000 |
