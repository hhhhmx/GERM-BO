# Experimental Results

All experiments use the real DNABERT-2 backbone under the required single-GPU policy (`CUDA_VISIBLE_DEVICES=3`). Unless otherwise specified, results use validation-accuracy best-checkpoint selection and validation-threshold tuned test evaluation.

## Main: Controlled Hard-Border Result

The main experiment evaluates whether GERM-BO can exploit meaningful border information when such information is available. We use the enlarged controlled `hard_border_large` split and compare Baseline LoRA, activation-derived GERM-BO, and metadata-driven GERM-BO across 13 random seeds.

The metadata score is a scalar stored as `border_score=<float>` in the CSV metadata field. In the controlled split, this score is produced by the task construction procedure and should be interpreted as a known/oracle border-score annotation for mechanism validation, not as naturally available biological metadata. Full score definitions are in `METADATA_SCORE_DEFINITION.md`.

| Model | Seeds | Accuracy Mean | Accuracy Std | F1 Mean | F1 Std | Min Acc | Max Acc |
|---|---:|---:|---:|---:|---:|---:|---:|
| Baseline LoRA | 13 | 0.8377 | 0.0544 | 0.8300 | 0.0725 | 0.7305 | 0.9102 |
| Activation-derived GERM-BO | 13 | 0.8918 | 0.0255 | 0.8896 | 0.0276 | 0.8477 | 0.9297 |
| Metadata-driven GERM-BO | 13 | 0.9519 | 0.0443 | 0.9493 | 0.0483 | 0.8828 | 0.9961 |

| Metric | Comparison | Mean A +/- Std | Mean B +/- Std | Delta | t-test p | Wilcoxon p | Bootstrap 95% CI | Win Rate |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| Accuracy | Metadata-driven vs Baseline | 0.9519 +/- 0.0443 | 0.8377 +/- 0.0544 | +0.1142 | 0.0000 | 0.0005 | [+0.0703, +0.1593] | 92.3% |
| F1 | Metadata-driven vs Baseline | 0.9493 +/- 0.0483 | 0.8300 +/- 0.0725 | +0.1192 | 0.0000 | 0.0005 | [+0.0676, +0.1746] | 92.3% |
| Accuracy | Metadata-driven vs Activation-derived | 0.9519 +/- 0.0443 | 0.8918 +/- 0.0255 | +0.0601 | 0.0000 | 0.0015 | [+0.0361, +0.0835] | 92.3% |
| Accuracy | Activation-derived vs Baseline | 0.8918 +/- 0.0255 | 0.8377 +/- 0.0544 | +0.0541 | 0.0021 | 0.0015 | [+0.0240, +0.0892] | 84.6% |

Main result: metadata-driven GERM-BO is the strongest controlled-task configuration. This supports the mechanism claim that GERM-BO can use meaningful border scores to improve adapter learning.

## Mechanism: Compensation Source and Leakage Control

The mechanism experiments separate three questions: whether explicit metadata scores outperform activation-derived proxies, whether compensation itself matters, and whether the gain is caused by metadata-channel leakage.

First, we compare no compensation, activation-derived compensation, and metadata-driven compensation on held-out seeds `47-54` over `border_medium` and `border_hard`.

| Variant | Runs | Accuracy Mean | Accuracy Std | F1 Mean | F1 Std | Min Acc |
|---|---:|---:|---:|---:|---:|---:|
| No compensation | 16 | 0.8706 | 0.0685 | 0.8741 | 0.0601 | 0.6367 |
| Activation-derived compensation | 16 | 0.8757 | 0.0543 | 0.8768 | 0.0532 | 0.7461 |
| Metadata-driven compensation | 16 | 0.9272 | 0.0583 | 0.9251 | 0.0613 | 0.7891 |

Metadata-driven compensation improves combined held-out accuracy over activation-derived compensation by `+0.0515`, with bootstrap CI `[+0.0095, +0.0920]`. Activation-derived compensation is not clearly distinguishable from no compensation in this mechanism table.

Second, we shuffle metadata strings within each split while keeping sequences and labels unchanged.

| Variant | Runs | Accuracy Mean | Accuracy Std | F1 Mean | F1 Std |
|---|---:|---:|---:|---:|---:|
| Real metadata | 16 | 0.9272 | 0.0583 | 0.9251 | 0.0613 |
| Shuffled metadata | 16 | 0.8638 | 0.0598 | 0.8607 | 0.0718 |
| Activation-derived compensation | 16 | 0.8757 | 0.0543 | 0.8768 | 0.0532 |
| No compensation | 16 | 0.8706 | 0.0685 | 0.8741 | 0.0601 |

Shuffling metadata removes the gain: real metadata outperforms shuffled metadata by `+0.0635` accuracy. This supports the interpretation that correct sample-to-border-score alignment matters, rather than the mere presence of a metadata field.

Target-module ablation also supports the final design choice:

| Variant | Accuracy Mean +/- Std | F1 Mean +/- Std |
|---|---:|---:|
| Classifier only | 0.8737 +/- 0.0098 | 0.8735 +/- 0.0149 |
| Wqkv + classifier | 0.8854 +/- 0.0197 | 0.8881 +/- 0.0155 |
| Attention.output + classifier | 0.8932 +/- 0.0399 | 0.8935 +/- 0.0369 |
| Wqkv + attention.output + classifier | 0.8620 +/- 0.0148 | 0.8600 +/- 0.0081 |

The final metadata-driven configuration uses `attention.output.dense` layer 0/1 plus `classifier`.

## External: Non-Oracle Benchmark Pilots

The external experiments test the harder non-oracle setting: real genomic benchmarks do not provide ground-truth border annotations, so the score must be estimated from sequence alone. These experiments are not the main contribution; they evaluate whether simple label-free estimators are sufficient.

### UCI Promoter

UCI Promoter is a very small public DNA benchmark with 106 labeled sequences and a 74/16/16 train/validation/test split.

| Model | Seeds | Accuracy Mean | Accuracy Std | F1 Mean | F1 Std |
|---|---:|---:|---:|---:|---:|
| Baseline LoRA | 5 | 0.6000 | 0.0342 | 0.6490 | 0.0494 |
| Activation-derived GERM-BO | 5 | 0.6125 | 0.1677 | 0.5856 | 0.2149 |
| Metadata-driven GERM-BO | 5 | 0.5750 | 0.1118 | 0.6129 | 0.1382 |

This benchmark is too small for a strong external claim and does not reproduce the controlled-task gain.

### Genomic Benchmarks: human_nontata_promoters

We then used the larger Genomic Benchmarks `human_nontata_promoters` task. The raw benchmark has 27,097 training and 9,033 test sequences; the current single-GPU pilot uses a 2,000/500/1,000 train/validation/test subset.

Initial label-free k-mer JSD scores underperform baseline:

| Model | Seeds | Accuracy Mean | Accuracy Std | F1 Mean | F1 Std |
|---|---:|---:|---:|---:|---:|
| Baseline LoRA | 3 | 0.8103 | 0.0021 | 0.8238 | 0.0071 |
| Activation-derived GERM-BO | 3 | 0.8090 | 0.0151 | 0.8289 | 0.0119 |
| Metadata-estimated GERM-BO | 3 | 0.7993 | 0.0184 | 0.8207 | 0.0148 |

We tested three estimator families: k-mer JSD boundary shifts, frozen DNABERT-2 token-embedding shifts, and contextual DNABERT-2 representation shifts.

| Estimator | Seeds | Accuracy Mean | Accuracy Std | F1 Mean | F1 Std | Delta Acc vs Baseline | Held-Out Decision |
|---|---:|---:|---:|---:|---:|---:|---|
| k-mer JSD `w64_k2_t10_s3` | 42-44 | 0.8173 | 0.0040 | 0.8350 | 0.0029 | +0.0070 | Promising first-stage |
| k-mer JSD `w64_k2_t10_s3` | 45-49 | 0.8168 | 0.0032 | 0.8359 | 0.0040 | -0.0010 | Not promoted |
| Token embedding shift `tw16` | 42-44 | 0.8097 | 0.0055 | 0.8279 | 0.0044 | -0.0007 | Not promoted |
| Contextual DNABERT-2 shift `tw16` | 42-44 | 0.8130 | 0.0040 | 0.8316 | 0.0052 | +0.0027 | Promising first-stage |
| Contextual DNABERT-2 shift `tw16` | 45-49 | 0.8136 | 0.0064 | 0.8299 | 0.0071 | -0.0042 | Not promoted |

External result: none of the current non-oracle estimators stably outperforms baseline on held-out seeds. This does not invalidate the controlled GERM-BO mechanism; it shows that robustly estimating useful border scores from natural sequences remains unresolved.

### Boundary-Sensitive Splice-Site Pilot

Because promoter classification may not be strongly boundary-sensitive, we added a more appropriate real benchmark: Hugging Face `InstaDeepAI/nucleotide_transformer_downstream_tasks/splice_sites_all`. This is a 3-class splice-site classification task with a balanced pilot subset of 3,000/600/1,200 train/validation/test examples. Evaluation uses argmax predictions and macro-F1 because the task is multi-class.

The metadata-estimated GERM-BO variant uses a label-free center-window k-mer JSD score. It uses the shared center-position prior of the benchmark for all samples but does not read labels.

| Model | Seeds | Accuracy Mean | Accuracy Std | Macro-F1 Mean | Macro-F1 Std | Delta Acc vs Baseline | Delta Macro-F1 vs Baseline |
|---|---:|---:|---:|---:|---:|---:|---:|
| Baseline LoRA | 3 | 0.3597 | 0.0245 | 0.2481 | 0.0705 | 0.0000 | 0.0000 |
| Metadata-estimated GERM-BO center-JSD | 3 | 0.3975 | 0.0044 | 0.3467 | 0.0252 | +0.0378 | +0.0987 |

This is the strongest external non-oracle signal so far: metadata-estimated GERM-BO wins on all three first-stage pilot seeds. We then ran held-out seeds `45-49`.

| Held-Out Model | Seeds | Accuracy Mean | Accuracy Std | Macro-F1 Mean | Macro-F1 Std | Delta Acc vs Baseline | Delta Macro-F1 vs Baseline |
|---|---:|---:|---:|---:|---:|---:|---:|
| Baseline LoRA | 5 | 0.3815 | 0.0289 | 0.2930 | 0.0823 | 0.0000 | 0.0000 |
| Metadata-estimated GERM-BO center-JSD | 5 | 0.3863 | 0.0284 | 0.3297 | 0.0665 | +0.0048 | +0.0368 |

Held-out confirmation is directionally positive but not stable enough for a strong external claim: accuracy win rate is `60.0%`, macro-F1 win rate is `40.0%`, and bootstrap intervals cross zero. The splice-site result is still useful because it shows that using a boundary-sensitive task improves the external signal compared with promoter benchmarks, but it remains a pilot rather than a final external main result.

## Limitation: Oracle Score and Estimator Bottleneck

The project should be framed with an explicit oracle vs non-oracle boundary.

| Claim | Status | Supporting Evidence | Boundary / Caveat |
|---|---|---|---|
| Controlled mechanism works strongly | Supported | On `hard_border_large`, metadata-driven GERM-BO improves accuracy from `0.8377 +/- 0.0544` to `0.9519 +/- 0.0443` over 13 seeds. | This is a controlled/oracle-border-score setting, not a claim that real datasets provide this score. |
| Improvement is not metadata-channel leakage | Supported | Shuffled metadata ablation drops performance from `0.9272 +/- 0.0583` to `0.8638 +/- 0.0598` while sequences and labels are unchanged. | This rules out generic metadata-channel leakage, but does not make the controlled score naturally available. |
| External non-oracle estimator remains open | Supported as a limitation | k-mer JSD and contextual DNABERT-2 estimators fail to stably beat baseline on held-out seeds. | External benchmark should be framed as limitation/future work, not as the main contribution. |
| Boundary-sensitive splice-site estimator is promising | Partially supported | First-stage seeds show `+0.0378` accuracy and `+0.0987` macro-F1; held-out remains directionally positive but weak (`+0.0048` accuracy, `+0.0368` macro-F1). | Useful external pilot, but not yet a strong external main result. |

Recommended takeaway: GERM-BO works strongly when meaningful border scores are available; estimating such scores robustly in non-oracle real genomic benchmarks is the key open problem.

## Reproducibility

The final reproduction entrypoint is `tools/run_final_reproduction.sh`. Example remote commands:

```bash
cd ~/germ_bo_project
CUDA_VISIBLE_DEVICES=3 bash tools/run_final_reproduction.sh main-13seed
CUDA_VISIBLE_DEVICES=3 bash tools/run_final_reproduction.sh mechanism-heldout
CUDA_VISIBLE_DEVICES=3 bash tools/run_final_reproduction.sh shuffled-ablation
CUDA_VISIBLE_DEVICES=3 bash tools/run_final_reproduction.sh benchmark-pilot
CUDA_VISIBLE_DEVICES=3 bash tools/run_human_nontata_promoters_pilot.sh
CUDA_VISIBLE_DEVICES=3 bash tools/run_human_nontata_estimator_grid.sh
CUDA_VISIBLE_DEVICES=3 bash tools/run_human_nontata_w64_heldout.sh
CUDA_VISIBLE_DEVICES=3 bash tools/run_human_nontata_embedding_estimator_pilot.sh
CUDA_VISIBLE_DEVICES=3 bash tools/run_human_nontata_ctx_tw16_heldout.sh
CUDA_VISIBLE_DEVICES=3 bash tools/run_final_reproduction.sh summaries
```
