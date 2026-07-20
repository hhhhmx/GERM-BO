# DNABERT-2 Multi-Seed Pilot Summary

Test split results for the real pretrained genomic backbone pilot under the required single-GPU policy (`CUDA_VISIBLE_DEVICES=3`).

## Aggregate Summary

| Model | Seeds | Accuracy Mean | Accuracy Std | F1 Mean | F1 Std | Loss Mean | Loss Std |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| baseline_lora | 5 | 0.6375 | 0.1442 | 0.5006 | 0.3080 | 0.6615 | 0.0204 |
| germ_bo_mild | 5 | 0.7063 | 0.1386 | 0.5701 | 0.3343 | 0.6571 | 0.0141 |

## Per-Seed Test Results

| Model | Seed | Accuracy | F1 | Loss |
| --- | ---: | ---: | ---: | ---: |
| baseline_lora | 42 | 0.8438 | 0.8148 | 0.6457 |
| baseline_lora | 43 | 0.6875 | 0.5455 | 0.6463 |
| baseline_lora | 44 | 0.6563 | 0.4762 | 0.6554 |
| baseline_lora | 45 | 0.5000 | 0.0000 | 0.6650 |
| baseline_lora | 46 | 0.5000 | 0.6667 | 0.6952 |
| germ_bo_mild | 42 | 0.8438 | 0.8276 | 0.6366 |
| germ_bo_mild | 43 | 0.8281 | 0.8197 | 0.6503 |
| germ_bo_mild | 44 | 0.6250 | 0.4000 | 0.6627 |
| germ_bo_mild | 45 | 0.5156 | 0.0606 | 0.6624 |
| germ_bo_mild | 46 | 0.7188 | 0.7429 | 0.6736 |

## Paper-Friendly Takeaway

On the current real DNABERT-2 pilot, the tuned mild GERM-BO setting outperforms `baseline_lora` on mean accuracy, mean F1, and mean loss across five seeds, while also showing lower loss variance. This mild setting is the current formal default GERM-BO configuration for the project.

## Formal Run Check

Formal single-GPU runs were also evaluated with the current official configs:

| Run | Accuracy | F1 | Loss |
| --- | ---: | ---: | ---: |
| formal_baseline_lora | 0.8438 | 0.8148 | 0.6457 |
| formal_germ_bo | 0.7969 | 0.7547 | 0.6426 |

These formal runs match the previously observed single-seed pilot behavior for the same configurations.
