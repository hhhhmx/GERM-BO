# Final Reproduction Notes

All training and evaluation commands use one visible GPU through `CUDA_VISIBLE_DEVICES=3`. The codebase does not use DDP, DataParallel, DeepSpeed, or FSDP.

## Main Entrypoint

Run from the remote project directory:

```bash
cd ~/germ_bo_project
CUDA_VISIBLE_DEVICES=3 bash tools/run_final_reproduction.sh <phase>
```

Available phases:

| Phase | Purpose |
|---|---|
| `benchmark-pilot` | Runs the UCI Promoter real benchmark pilot: baseline, activation-derived GERM-BO, metadata-driven GERM-BO, seeds 42-46. |
| `human-nontata-pilot` | Run manually with `CUDA_VISIBLE_DEVICES=3 bash tools/run_human_nontata_promoters_pilot.sh`: larger Genomic Benchmarks promoter pilot with label-free k-mer JSD border estimation. |
| `human-nontata-estimator-grid` | Run manually with `CUDA_VISIBLE_DEVICES=3 bash tools/run_human_nontata_estimator_grid.sh`: small label-free estimator grid. |
| `human-nontata-w64-heldout` | Run manually with `CUDA_VISIBLE_DEVICES=3 bash tools/run_human_nontata_w64_heldout.sh`: held-out seeds 45-49 confirmation for the best grid estimator. |
| `human-nontata-embedding-estimator` | Run manually with `CUDA_VISIBLE_DEVICES=3 bash tools/run_human_nontata_embedding_estimator_pilot.sh`: frozen DNABERT-2 token-embedding boundary estimator pilot. |
| `human-nontata-ctx-tw16-heldout` | Run manually with `CUDA_VISIBLE_DEVICES=3 bash tools/run_human_nontata_ctx_tw16_heldout.sh`: held-out seeds 45-49 for contextual DNABERT-2 tw16 estimator. |
| `splice-sites-all-pilot` | Run manually with `CUDA_VISIBLE_DEVICES=3 bash tools/run_splice_sites_all_pilot.sh`: boundary-sensitive 3-class splice-site pilot. |
| `main-13seed` | Runs the final hard-border-large metadata-driven 13-seed confirmation. |
| `mechanism-heldout` | Runs metadata-vs-activation held-out mechanism comparison on medium/hard tasks. |
| `shuffled-ablation` | Runs the metadata-shuffled leakage-control ablation. |
| `summaries` | Regenerates summary/statistical tables from existing result JSON files. |
| `all` | Runs all phases above. Use only when intentionally re-running the complete suite. |

## Key Result Artifacts

| Artifact | Description |
|---|---|
| `METADATA_SCORE_DEFINITION.md` | Formal definition of controlled metadata scores and label-free estimated border scores. |
| `results/paper_final_results_table.md` | Paper-style final results section with main results, ablations, external pilot, and reproduction commands. |
| `results/paper_final_results_table.csv` | Compact machine-readable final summary table. |
| `results/hard_border_large_metadata_significance.md` | Formal paired significance table for the final hard-border-large result. |
| `results/metadata_mechanism_significance.md` | Paired significance table for metadata-driven vs activation-derived compensation. |
| `results/uci_promoter_benchmark_pilot.md` | Real public benchmark pilot summary. |
| `results/human_nontata_promoters_pilot.md` | Larger real benchmark pilot summary with label-free metadata-estimated border scores. |
| `results/human_nontata_estimator_grid.md` | Label-free estimator tuning grid on the larger real benchmark. |
| `results/human_nontata_w64_heldout.md` | Held-out confirmation for the best label-free estimator. |
| `results/human_nontata_embedding_estimator_pilot.md` | Frozen DNABERT-2 token-embedding estimator pilot. |
| `results/human_nontata_ctx_tw16_heldout.md` | Held-out confirmation for contextual DNABERT-2 tw16 estimator. |
| `results/splice_sites_all_pilot.md` | Boundary-sensitive splice-site external pilot. |
| `results/splice_sites_all_heldout.md` | Held-out confirmation for splice-site external pilot. |

## Exact Final Main Config

The current main configuration is:

```text
configs/real_dnabert2_germ_bo_hard_border_large_metadata_comp027_p4.yaml
```

It uses:

```text
backbone: local DNABERT-2
adapter target modules: encoder layer 0/1 attention.output.dense + classifier
border_score_type: metadata_border_score
compensation_strength: 0.27
early_stopping_patience: 4
checkpoint monitor: validation accuracy, max
test evaluation: validation-threshold tuned best.pt
```

The metadata score used by this configuration is documented in:

```text
METADATA_SCORE_DEFINITION.md
```

Oracle/non-oracle interpretation is also documented there. In short:

```text
controlled setting = known/oracle border score for mechanism validation
shuffled ablation = metadata-channel leakage control
external pilot = non-oracle sequence-only score estimation
```

Current claim boundary:

```text
Claim 1 supported: controlled mechanism works strongly.
Claim 2 supported: shuffled metadata argues against metadata-channel leakage.
Claim 3 limitation: external non-oracle estimator remains open.
Claim 4 not promoted: contextual estimator is promising in pilot but not confirmed on held-out seeds.
```

## External Benchmark Pilot

The external benchmark pilot uses the UCI Molecular Biology Promoter dataset:

```bash
cd ~/germ_bo_project
PYTHONPATH=/home/sy/germ_bo_project CUDA_VISIBLE_DEVICES=3 \
  /home/sy/micromamba-bin/micromamba run -r /home/sy/micromamba -n germ-bo-py310 \
  python tools/prepare_uci_promoter.py

CUDA_VISIBLE_DEVICES=3 bash tools/run_final_reproduction.sh benchmark-pilot
```

This pilot is intentionally reported separately because the dataset is very small: 106 total sequences with a 74/16/16 split.

## Larger Real Benchmark Pilot

The larger external pilot uses Genomic Benchmarks `human_nontata_promoters`. The remote server could not directly access Google Drive or Hugging Face, so the Parquet files were downloaded locally and copied to:

```text
~/germ_bo_project/data/cache/human_nontata_promoters_train.parquet
~/germ_bo_project/data/cache/human_nontata_promoters_test.parquet
```

Then run:

```bash
cd ~/germ_bo_project
CUDA_VISIBLE_DEVICES=3 bash tools/run_human_nontata_promoters_pilot.sh
```

The current pilot subset is `2000/500/1000` train/validation/test with seeds `42-44`.

The estimator-grid phase is:

```bash
cd ~/germ_bo_project
CUDA_VISIBLE_DEVICES=3 bash tools/run_human_nontata_estimator_grid.sh
```

Current best label-free estimator:

```text
window=64
kmer=2
top_ratio=0.10
score_scale=3.0
```

On the 3-seed pilot, this setting achieved `0.8173 +/- 0.0040` accuracy versus baseline `0.8103 +/- 0.0021`.

Held-out seeds `45-49` did not confirm stable improvement:

```text
Baseline LoRA: 0.8178 +/- 0.0034 accuracy
Metadata-estimated GERM-BO w64_k2_t10_s3: 0.8168 +/- 0.0032 accuracy
Paired delta: -0.0010
```

Therefore this estimator is not upgraded to the external benchmark main configuration.

## Frozen Embedding Estimator

Run:

```bash
cd ~/germ_bo_project
CUDA_VISIBLE_DEVICES=3 bash tools/run_human_nontata_embedding_estimator_pilot.sh
```

The implementation supports both frozen token embeddings and contextual hidden states. Contextual extraction forces DNABERT-2 onto its ordinary PyTorch attention path by setting `attention_probs_dropout_prob=0.1` only for metadata-score preparation.

Pilot result:

```text
Baseline LoRA: 0.8103 +/- 0.0021 accuracy
Token embedding shift tw8: 0.8037 +/- 0.0067 accuracy
Token embedding shift tw16: 0.8097 +/- 0.0055 accuracy
Contextual DNABERT-2 shift tw16: 0.8130 +/- 0.0040 accuracy
```

Held-out confirmation:

```text
Baseline LoRA seeds 45-49: 0.8178 +/- 0.0034 accuracy
Contextual DNABERT-2 shift tw16 seeds 45-49: 0.8136 +/- 0.0064 accuracy
Paired delta: -0.0042
```

The contextual `tw16` estimator is not promoted. Current external non-oracle estimators remain a limitation/future-work item.
