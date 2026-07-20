# Cross-Backbone Replication on border_hard (seeds 50--54)

Protocol: held-out seeds 50--54, oracle metadata border scores, rank 8, lr 3e-4, early stopping patience 4.

## Summary

| Method | Seeds | Test Acc Mean +/- Std | Test Macro-F1 Mean +/- Std | Per-Seed Acc |
|---|---:|---:|---:|---|
| NT v2 50m LoRA | 5 | 0.8945 +/- 0.0124 | 0.8944 +/- 0.0124 | 0.9141 / 0.8906 / 0.8984 / 0.8867 / 0.8828 |
| NT v2 50m GERM-BO metadata comp0.27 | 5 | 0.9828 +/- 0.0045 | 0.9828 +/- 0.0045 | 0.9805 / 0.9844 / 0.9844 / 0.9883 / 0.9766 |
| HyenaDNA tiny LoRA | 5 | 0.9625 +/- 0.0090 | 0.9625 +/- 0.0090 | 0.9727 / 0.9609 / 0.9609 / 0.9688 / 0.9492 |
| HyenaDNA tiny GERM-BO metadata comp0.27 | 5 | 0.9945 +/- 0.0021 | 0.9945 +/- 0.0021 | 0.9922 / 0.9961 / 0.9961 / 0.9922 / 0.9961 |
