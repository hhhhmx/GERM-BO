#!/usr/bin/env bash
set -euo pipefail

cd ~/germ_bo_project

export CUDA_VISIBLE_DEVICES=3
PYTHON_BIN="/home/sy/micromamba-bin/micromamba run -r /home/sy/micromamba -n germ-bo-py310 python"
RUN_LOG="results/splice_kmer_balanced_ablation_baselines_run.log"
STATUS="results/splice_kmer_balanced_ablation_baselines_status.tsv"
DONE="results/splice_kmer_balanced_ablation_baselines.done"
SOURCE_SPLIT="data/benchmarks/splice_sites_all_kmer_balanced"
SHUFFLED_SPLIT="data/benchmarks/splice_sites_all_kmer_balanced_shuffled"

: > "${RUN_LOG}"
: > "${STATUS}"
rm -f "${DONE}"

PYTHONPATH=/home/sy/germ_bo_project CUDA_VISIBLE_DEVICES=3 ${PYTHON_BIN} tools/prepare_shuffled_metadata_split.py \
  --input-dir "${SOURCE_SPLIT}" \
  --output-dir "${SHUFFLED_SPLIT}" \
  --seed 20260425 \
  >> "${RUN_LOG}" 2>&1

write_common_config() {
  local path="$1"
  local method="$2"
  local split_dir="$3"
  local target_modules="$4"
  local adapter_name="$5"
  local compensation_strength="${6:-0.27}"

  cat > "${path}" <<EOF
seed: 42
device: cuda
gpu_id: 3
output_dir: outputs
results_dir: results
task:
  name: splice_sites_all
  num_labels: 3
data:
  dataset_type: genomic
  seq_length: 512
  num_workers: 0
  sequence_column: sequence
  label_column: label
  id_column: id
  metadata_column: metadata
  tokenizer_mode: raw
  splits:
    train: ${split_dir}/train.csv
    val: ${split_dir}/val.csv
    test: ${split_dir}/test.csv
model:
  backbone_type: hf
  pretrained_model_name_or_path: local_assets/dnabert2_117m
  tokenizer_name_or_path: local_assets/dnabert2_117m
  cache_dir: null
  trust_remote_code: true
  attention_probs_dropout_prob: 0.1
  classifier_dropout: 0.1
adapter:
  name: ${adapter_name}
  rank: 8
  alpha: 16
  dropout: 0.05
  target_modules:
${target_modules}
EOF

  if [[ "${adapter_name}" == "germ_bo" ]]; then
    cat >> "${path}" <<EOF
  compensation_strength: ${compensation_strength}
  border_score_type: metadata_border_score
  border_normalization: mean
  compensation_clip_min: 0.70
  compensation_clip_max: 1.30
EOF
  fi

  cat >> "${path}" <<EOF
optim:
  lr: 0.0003
  weight_decay: 0.01
scheduler:
  name: none
train:
  epochs: 4
  batch_size: 4
  checkpoint_every: 1
  log_every: 100
  checkpoint_monitor: accuracy
  checkpoint_mode: max
  early_stopping_patience: 2
  early_stopping_min_delta: 0.0
debug:
  train_size: 32
  val_size: 16
  test_size: 16
  batch_size: 2
  epochs: 1
  max_steps: 4
  output_subdir: debug_${method}
logging:
  save_predictions: true
EOF
}

TM_FULL="    - encoder.encoder.layer.0.attention.self.Wqkv
    - encoder.encoder.layer.0.attention.output.dense
    - encoder.encoder.layer.1.attention.self.Wqkv
    - encoder.encoder.layer.1.attention.output.dense
    - classifier"
TM_ATTN="    - encoder.encoder.layer.0.attention.output.dense
    - encoder.encoder.layer.1.attention.output.dense
    - classifier"

write_common_config \
  "configs/real_dnabert2_baseline_lora_splice_sites_all_kmer_balanced.yaml" \
  "baseline_lora_splice_sites_all_kmer_balanced" \
  "${SOURCE_SPLIT}" \
  "${TM_FULL}" \
  "baseline_lora"

write_common_config \
  "configs/real_dnabert2_germ_bo_comp0_splice_sites_all_kmer_balanced.yaml" \
  "germ_bo_comp0_splice_sites_all_kmer_balanced" \
  "${SOURCE_SPLIT}" \
  "${TM_ATTN}" \
  "germ_bo" \
  "0.0"

write_common_config \
  "configs/real_dnabert2_germ_bo_shuffled_splice_sites_all_kmer_balanced.yaml" \
  "germ_bo_shuffled_splice_sites_all_kmer_balanced" \
  "${SHUFFLED_SPLIT}" \
  "${TM_ATTN}" \
  "germ_bo" \
  "0.27"

cat > "configs/real_dnabert2_linear_probe_splice_sites_all_kmer_balanced.yaml" <<EOF
seed: 42
device: cuda
gpu_id: 3
output_dir: outputs
results_dir: results
task:
  name: splice_sites_all
  num_labels: 3
data:
  dataset_type: genomic
  seq_length: 512
  num_workers: 0
  sequence_column: sequence
  label_column: label
  id_column: id
  metadata_column: metadata
  tokenizer_mode: raw
  splits:
    train: ${SOURCE_SPLIT}/train.csv
    val: ${SOURCE_SPLIT}/val.csv
    test: ${SOURCE_SPLIT}/test.csv
model:
  backbone_type: hf
  pretrained_model_name_or_path: local_assets/dnabert2_117m
  tokenizer_name_or_path: local_assets/dnabert2_117m
  cache_dir: null
  trust_remote_code: true
  attention_probs_dropout_prob: 0.1
  classifier_dropout: 0.1
adapter:
  name: linear_probe
  rank: 0
  alpha: 0
  dropout: 0.0
  target_modules: []
optim:
  lr: 0.001
  weight_decay: 0.01
scheduler:
  name: none
train:
  epochs: 4
  batch_size: 4
  checkpoint_every: 1
  log_every: 100
  checkpoint_monitor: accuracy
  checkpoint_mode: max
  early_stopping_patience: 2
  early_stopping_min_delta: 0.0
debug:
  train_size: 32
  val_size: 16
  test_size: 16
  batch_size: 2
  epochs: 1
  max_steps: 4
  output_subdir: debug_linear_probe_splice_sites_all_kmer_balanced
logging:
  save_predictions: true
EOF

run_one() {
  local method="$1"
  local config="$2"
  local seed="$3"
  local run_id="splice_kmer_balanced_ablation_${method}_seed${seed}"
  local outdir="outputs/${run_id}"
  local json_path="results/${run_id}_argmax.json"
  local csv_path="results/${run_id}_predictions.csv"

  if [[ -s "${json_path}" ]]; then
    echo -e "${method}\t${seed}\tskipped_existing\t${json_path}" | tee -a "${STATUS}"
    return 0
  fi

  echo "=== ${run_id} train ===" | tee -a "${RUN_LOG}"
  PYTHONPATH=/home/sy/germ_bo_project CUDA_VISIBLE_DEVICES=3 ${PYTHON_BIN} train.py \
    --config "${config}" \
    --seed "${seed}" \
    --output-dir "${outdir}" \
    >> "${RUN_LOG}" 2>&1

  echo "=== ${run_id} argmax eval ===" | tee -a "${RUN_LOG}"
  PYTHONPATH=/home/sy/germ_bo_project CUDA_VISIBLE_DEVICES=3 ${PYTHON_BIN} tools/evaluate_argmax.py \
    --config "${config}" \
    --checkpoint "${outdir}/checkpoints/best.pt" \
    --output-json "${json_path}" \
    --output-csv "${csv_path}" \
    >> "${RUN_LOG}" 2>&1

  rm -rf "${outdir}"
  echo -e "${method}\t${seed}\tdone\t${json_path}" | tee -a "${STATUS}"
}

for seed in 50 51 52 53 54; do
  run_one "baseline_lora_full" "configs/real_dnabert2_baseline_lora_splice_sites_all_kmer_balanced.yaml" "${seed}"
  run_one "germ_bo_comp0" "configs/real_dnabert2_germ_bo_comp0_splice_sites_all_kmer_balanced.yaml" "${seed}"
  run_one "germ_bo_shuffled" "configs/real_dnabert2_germ_bo_shuffled_splice_sites_all_kmer_balanced.yaml" "${seed}"
  run_one "linear_probe" "configs/real_dnabert2_linear_probe_splice_sites_all_kmer_balanced.yaml" "${seed}"
done

PYTHONPATH=/home/sy/germ_bo_project CUDA_VISIBLE_DEVICES=3 ${PYTHON_BIN} tools/summarize_splice_kmer_balanced_full_comparison.py \
  >> "${RUN_LOG}" 2>&1

date -Iseconds > "${DONE}"
echo "splice_kmer_balanced_ablation_baselines_done"
