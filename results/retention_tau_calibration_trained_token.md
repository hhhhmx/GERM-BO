# Retention Ratio R_w(tau) Calibration (Trained-checkpoint, token-level)

Empirical estimate: R_emp = E[phi_tau(a)^2 g^2]/E[g^2] at layer-0 attention output.

## Summary

| Split | Model | tau* | R at tau* (low / high) | tau_med | R at tau_med (low / high) | Spearman_med |
|---|---|---:|---:|---:|---:|---:|
| border_hard | GERM-BO | 0.2067 | 1.000 / 1.000 | 0.1185 | 0.928 / 0.838 | -0.400 |
| border_hard | LoRA | 0.1714 | 1.000 / 0.999 | 0.1096 | 0.660 / 0.641 | -0.200 |
| hard_border_large | GERM-BO | 0.1739 | 1.000 / 0.990 | 0.1118 | 0.741 / 0.401 | -1.000 |
| hard_border_large | LoRA | 0.1644 | 1.000 / 1.000 | 0.1102 | 0.859 / 0.759 | -0.800 |
