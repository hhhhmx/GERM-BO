#!/usr/bin/env bash
set -euo pipefail

cd ~/germ_bo_project

export CUDA_VISIBLE_DEVICES=3
PYTHON_BIN="/home/sy/micromamba-bin/micromamba run -r /home/sy/micromamba -n germ-bo-py310 python"
RUN_LOG="results/splice_sites_all_larger_grid_run.log"
STATUS="results/splice_sites_all_larger_grid_status.tsv"
DONE="results/splice_sites_all_larger_grid.done"

: > "${RUN_LOG}"
: > "${STATUS}"
rm -f "${DONE}"

write_config() {
  local path="$1"
  local method="$2"
  local split_dir="$3"

  if [[ "${method}" == "baseline_lora" ]]; then
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
  name: baseline_lora
  rank: 8
  alpha: 16
  dropout: 0.05
  target_modules:
    - encoder.encoder.layer.0.attention.self.Wqkv
    - encoder.encoder.layer.0.attention.output.dense
    - encoder.encoder.layer.1.attention.self.Wqkv
    - encoder.encoder.layer.1.attention.output.dense
    - classifier
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
  output_subdir: debug_splice_sites_all_larger_grid
logging:
  save_predictions: true
EOF
  else
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
  name: germ_bo
  rank: 8
  alpha: 16
  dropout: 0.05
  target_modules:
    - encoder.encoder.layer.0.attention.output.dense
    - encoder.encoder.layer.1.attention.output.dense
    - classifier
  compensation_strength: 0.27
  border_score_type: metadata_border_score
  border_normalization: mean
  compensation_clip_min: 0.73
  compensation_clip_max: 1.42
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
  output_subdir: debug_splice_sites_all_larger_grid
logging:
  save_predictions: true
EOF
  fi
}

prepare_split() {
  local method="$1"
  local split_dir="$2"
  shift 2
  echo "=== prepare ${method}: ${split_dir} ===" | tee -a "${RUN_LOG}"
  PYTHONPATH=/home/sy/germ_bo_project CUDA_VISIBLE_DEVICES=3 ${PYTHON_BIN} tools/prepare_splice_sites_all.py \
    --output-dir "${split_dir}" \
    --max-train 9000 \
    --max-val 1800 \
    --max-test 3000 \
    "$@" \
    >> "${RUN_LOG}" 2>&1
  write_config "configs/real_dnabert2_${method}_splice_sites_all_larger_grid.yaml" "${method}" "${split_dir}"
}

run_one() {
  local method="$1"
  local seed="$2"
  local config="configs/real_dnabert2_${method}_splice_sites_all_larger_grid.yaml"
  local run_id="splice_sites_all_larger_grid_${method}_seed${seed}"
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

prepare_split "baseline_lora" "data/benchmarks/splice_sites_all_larger_baseline" \
  --estimator center_jsd --window 48 --search-radius 24 --kmer 2 --top-ratio 0.25 --score-scale 4.0
prepare_split "germ_bo_center_w48_k2_t25_s4" "data/benchmarks/splice_sites_all_larger_center_w48_k2_t25_s4" \
  --estimator center_jsd --window 48 --search-radius 24 --kmer 2 --top-ratio 0.25 --score-scale 4.0
prepare_split "germ_bo_center_w64_k2_t10_s4" "data/benchmarks/splice_sites_all_larger_center_w64_k2_t10_s4" \
  --estimator center_jsd --window 64 --search-radius 32 --kmer 2 --top-ratio 0.10 --score-scale 4.0
prepare_split "germ_bo_center_w64_k3_t10_s3" "data/benchmarks/splice_sites_all_larger_center_w64_k3_t10_s3" \
  --estimator center_jsd --window 64 --search-radius 32 --kmer 3 --top-ratio 0.10 --score-scale 3.0
prepare_split "germ_bo_motif_w64_k2_t10_s3_m05" "data/benchmarks/splice_sites_all_larger_motif_w64_k2_t10_s3_m05" \
  --estimator center_jsd_motif --window 64 --search-radius 32 --kmer 2 --top-ratio 0.10 --score-scale 3.0 --motif-weight 0.5 --motif-radius 12

for seed in 42 43 44; do
  run_one "baseline_lora" "${seed}"
  run_one "germ_bo_center_w48_k2_t25_s4" "${seed}"
  run_one "germ_bo_center_w64_k2_t10_s4" "${seed}"
  run_one "germ_bo_center_w64_k3_t10_s3" "${seed}"
  run_one "germ_bo_motif_w64_k2_t10_s3_m05" "${seed}"
done

PYTHONPATH=/home/sy/germ_bo_project ${PYTHON_BIN} tools/summarize_splice_sites_all_larger_grid.py \
  >> "${RUN_LOG}" 2>&1

date -Iseconds > "${DONE}"
echo "splice_sites_all_larger_grid_done"
