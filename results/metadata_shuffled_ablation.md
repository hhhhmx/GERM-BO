# Metadata Shuffled Ablation

Protocol: sequence and label are unchanged; only metadata strings are shuffled within each split. Runs use metadata-driven `comp=0.27/p4`, held-out seeds `47-54`, real DNABERT-2 backbone, validation-accuracy best checkpoint, and validation-threshold tuned test evaluation.

## Summary

| Group | Variant | Test Acc Mean +/- Std | Test F1 Mean +/- Std | Min Acc | Max Acc |
|---|---|---:|---:|---:|---:|
| border_medium | metadata real comp=0.27/p4 | 0.9258 +/- 0.0652 | 0.9238 +/- 0.0675 | 0.7891 | 0.9961 |
| border_medium | metadata shuffled comp=0.27/p4 | 0.8706 +/- 0.0820 | 0.8629 +/- 0.1017 | 0.6719 | 0.9297 |
| border_medium | activation-derived comp=0.27/p4 | 0.9175 +/- 0.0168 | 0.9161 +/- 0.0180 | 0.8945 | 0.9375 |
| border_medium | no compensation comp=0.00/p4 | 0.9077 +/- 0.0153 | 0.9092 +/- 0.0142 | 0.8867 | 0.9336 |
| border_hard | metadata real comp=0.27/p4 | 0.9287 +/- 0.0550 | 0.9264 +/- 0.0590 | 0.8359 | 0.9883 |
| border_hard | metadata shuffled comp=0.27/p4 | 0.8569 +/- 0.0287 | 0.8586 +/- 0.0264 | 0.8203 | 0.8906 |
| border_hard | activation-derived comp=0.27/p4 | 0.8340 +/- 0.0453 | 0.8376 +/- 0.0471 | 0.7461 | 0.8828 |
| border_hard | no compensation comp=0.00/p4 | 0.8335 +/- 0.0816 | 0.8390 +/- 0.0687 | 0.6367 | 0.8945 |
| combined | metadata real comp=0.27/p4 | 0.9272 +/- 0.0583 | 0.9251 +/- 0.0613 | 0.7891 | 0.9961 |
| combined | metadata shuffled comp=0.27/p4 | 0.8638 +/- 0.0598 | 0.8607 +/- 0.0718 | 0.6719 | 0.9297 |
| combined | activation-derived comp=0.27/p4 | 0.8757 +/- 0.0543 | 0.8768 +/- 0.0532 | 0.7461 | 0.9375 |
| combined | no compensation comp=0.00/p4 | 0.8706 +/- 0.0685 | 0.8741 +/- 0.0601 | 0.6367 | 0.9336 |

## Paired Accuracy Deltas

| Group | Comparison | Delta Mean | Delta Std | Win Rate | Per-Seed Delta |
|---|---|---:|---:|---:|---:|
| border_medium | metadata_real_minus_metadata_shuffled | +0.0552 | 0.1239 | 75.0% | +0.1094 / -0.1289 / +0.0312 / +0.0000 / +0.0039 / +0.0508 / +0.0664 / +0.3086 |
| border_medium | metadata_real_minus_activation | +0.0083 | 0.0694 | 75.0% | +0.0820 / -0.1484 / +0.0195 / +0.0234 / -0.0078 / +0.0078 / +0.0312 / +0.0586 |
| border_medium | metadata_shuffled_minus_activation | -0.0469 | 0.0845 | 12.5% | -0.0273 / -0.0195 / -0.0117 / +0.0234 / -0.0117 / -0.0430 / -0.0352 / -0.2500 |
| border_medium | metadata_shuffled_minus_no_comp | -0.0371 | 0.0854 | 25.0% | -0.0156 / +0.0312 / -0.0391 / -0.0039 / -0.0234 / -0.0078 / +0.0039 / -0.2422 |
| border_hard | metadata_real_minus_metadata_shuffled | +0.0718 | 0.0703 | 75.0% | +0.1133 / +0.0781 / +0.1602 / +0.0938 / +0.1094 / -0.0547 / -0.0117 / +0.0859 |
| border_hard | metadata_real_minus_activation | +0.0947 | 0.0873 | 75.0% | +0.1211 / +0.2148 / +0.1133 / +0.1250 / +0.1680 / -0.0430 / -0.0156 / +0.0742 |
| border_hard | metadata_shuffled_minus_activation | +0.0229 | 0.0553 | 62.5% | +0.0078 / +0.1367 / -0.0469 / +0.0312 / +0.0586 / +0.0117 / -0.0039 / -0.0117 |
| border_hard | metadata_shuffled_minus_no_comp | +0.0234 | 0.0946 | 37.5% | -0.0312 / +0.0156 / -0.0273 / -0.0078 / -0.0156 / +0.2539 / +0.0117 / -0.0117 |
| combined | metadata_real_minus_metadata_shuffled | +0.0635 | 0.0977 | 75.0% | +0.1094 / -0.1289 / +0.0312 / +0.0000 / +0.0039 / +0.0508 / +0.0664 / +0.3086 / +0.1133 / +0.0781 / +0.1602 / +0.0938 / +0.1094 / -0.0547 / -0.0117 / +0.0859 |
| combined | metadata_real_minus_activation | +0.0515 | 0.0883 | 75.0% | +0.0820 / -0.1484 / +0.0195 / +0.0234 / -0.0078 / +0.0078 / +0.0312 / +0.0586 / +0.1211 / +0.2148 / +0.1133 / +0.1250 / +0.1680 / -0.0430 / -0.0156 / +0.0742 |
| combined | metadata_shuffled_minus_activation | -0.0120 | 0.0778 | 37.5% | -0.0273 / -0.0195 / -0.0117 / +0.0234 / -0.0117 / -0.0430 / -0.0352 / -0.2500 / +0.0078 / +0.1367 / -0.0469 / +0.0312 / +0.0586 / +0.0117 / -0.0039 / -0.0117 |
| combined | metadata_shuffled_minus_no_comp | -0.0068 | 0.0925 | 31.2% | -0.0156 / +0.0312 / -0.0391 / -0.0039 / -0.0234 / -0.0078 / +0.0039 / -0.2422 / -0.0312 / +0.0156 / -0.0273 / -0.0078 / -0.0156 / +0.2539 / +0.0117 / -0.0117 |
