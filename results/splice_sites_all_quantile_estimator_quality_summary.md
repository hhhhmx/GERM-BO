# Quantile-Normalized Estimator Quality Summary

Goal: compare raw clipped score with train-quantile normalized score ranges before running new training.

| Tag | Test Score Std Avg | Test Clip-Max Rate Avg | Baseline Score-Error r | GERM-BO Score-Error r | Entropy3 r | GC r |
|---|---:|---:|---:|---:|---:|---:|
| raw_clipped | 0.0026 | 99.9% | +0.0068 | +0.0105 | +0.1281 | -0.0322 |
| quantile_q08_12 | 0.1137 | 0.0% | +0.0306 | +0.0027 | +0.2673 | -0.0341 |
| quantile_q075_125 | 0.1421 | 0.0% | +0.0306 | +0.0027 | +0.2673 | -0.0341 |
| quantile_q09_11 | 0.0568 | 0.0% | +0.0306 | +0.0027 | +0.2673 | -0.0341 |

Interpretation: a usable estimator should avoid saturation and produce non-trivial sample-level variation. Score-error correlation is diagnostic only because predictions were produced by already-trained raw-score models.
