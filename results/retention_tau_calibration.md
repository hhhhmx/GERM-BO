# Retention Ratio R_w(tau) Calibration

Empirical estimate on pretrained DNABERT-2 with a randomly initialized classifier head: R_emp = E[phi_tau(a)^2 g^2]/E[g^2] at layer-0 attention output.

## Summary

| Split | tau* (1% clip) | R at tau* (low / high border) | tau_med | R at tau_med (low / high border) | Spearman_med |
|---|---:|---:|---:|---:|---:|
| border_hard | 0.1768 | 1.000 / 1.000 | 0.1103 | 0.558 / 0.384 | -0.600 |
| hard_border_large | 0.1760 | 0.968 / 1.000 | 0.1102 | 0.364 / 0.401 | 0.600 |
