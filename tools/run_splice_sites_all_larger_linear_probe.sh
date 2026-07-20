#!/usr/bin/env bash
set -euo pipefail

cd ~/germ_bo_project

export CUDA_VISIBLE_DEVICES=3
PYTHON_BIN="/home/sy/micromamba-bin/micromamba run -r /home/sy/micromamba -n germ-bo-py310 python"
RUN_LOG="results/splice_sites_all_larger_linear_probe_run.log"
STATUS="results/splice_sites_all_larger_linear_probe_status.tsv"
DONE="results/splice_sites_all_larger_linear_probe.done"
CONFIG="configs/real_dnabert2_linear_probe_splice_sites_all_larger.yaml"
SPLIT_DIR="data/benchmarks/splice_sites_all_larger_center_w64_k3_t10_s3"

: > "${RUN_LOG}"
: > "${STATUS}"
rm -f "${DONE}"

cat > "${CONFIG}" <<EOF
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
    train: ${SPLIT_DIR}/train.csv
    val: ${SPLIT_DIR}/val.csv
    test: ${SPLIT_DIR}/test.csv
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
  output_subdir: debug_splice_sites_all_larger_linear_probe
logging:
  save_predictions: true
EOF

run_one() {
  local seed="$1"
  local run_id="splice_sites_all_larger_linear_probe_seed${seed}"
  local outdir="outputs/${run_id}"
  local json_path="results/${run_id}_argmax.json"
  local csv_path="results/${run_id}_predictions.csv"

  if [[ -s "${json_path}" ]]; then
    echo -e "linear_probe\t${seed}\tskipped_existing\t${json_path}" | tee -a "${STATUS}"
    return 0
  fi

  echo "=== ${run_id} train ===" | tee -a "${RUN_LOG}"
  PYTHONPATH=/home/sy/germ_bo_project CUDA_VISIBLE_DEVICES=3 ${PYTHON_BIN} train.py \
    --config "${CONFIG}" \
    --seed "${seed}" \
    --output-dir "${outdir}" \
    >> "${RUN_LOG}" 2>&1

  echo "=== ${run_id} argmax eval ===" | tee -a "${RUN_LOG}"
  PYTHONPATH=/home/sy/germ_bo_project CUDA_VISIBLE_DEVICES=3 ${PYTHON_BIN} tools/evaluate_argmax.py \
    --config "${CONFIG}" \
    --checkpoint "${outdir}/checkpoints/best.pt" \
    --output-json "${json_path}" \
    --output-csv "${csv_path}" \
    >> "${RUN_LOG}" 2>&1

  rm -rf "${outdir}"
  echo -e "linear_probe\t${seed}\tdone\t${json_path}" | tee -a "${STATUS}"
}

for seed in 45 46 47 48 49; do
  run_one "${seed}"
done

date -Iseconds > "${DONE}"
echo "splice_sites_all_larger_linear_probe_done"
