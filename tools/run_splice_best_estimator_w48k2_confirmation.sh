#!/usr/bin/env bash
set -euo pipefail

cd ~/germ_bo_project

export CUDA_VISIBLE_DEVICES=3
PYTHON_BIN="/home/sy/micromamba-bin/micromamba run -r /home/sy/micromamba -n germ-bo-py310 python"
RUN_LOG="results/splice_best_estimator_w48k2_confirmation_run.log"
STATUS="results/splice_best_estimator_w48k2_confirmation_status.tsv"
DONE="results/splice_best_estimator_w48k2_confirmation.done"
SPLIT_DIR="data/benchmarks/splice_best_estimator_w48_k2_t025_train_quantile_r07_13"
CONFIG="configs/real_dnabert2_germ_bo_w48_k2_t025_train_quantile_r07_13_splice_sites.yaml"

: > "${RUN_LOG}"
: > "${STATUS}"
rm -f "${DONE}"

echo "=== prepare best estimator split ===" | tee -a "${RUN_LOG}"
PYTHONPATH=/home/sy/germ_bo_project CUDA_VISIBLE_DEVICES=3 ${PYTHON_BIN} tools/prepare_splice_sites_all.py \
  --output-dir "${SPLIT_DIR}" \
  --max-train 9000 \
  --max-val 1800 \
  --max-test 3000 \
  --estimator center_jsd \
  --window 48 \
  --search-radius 24 \
  --kmer 2 \
  --top-ratio 0.25 \
  --score-normalization train_quantile \
  --quantile-score-min 0.7 \
  --quantile-score-max 1.3 \
  >> "${RUN_LOG}" 2>&1

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
  compensation_clip_min: 0.70
  compensation_clip_max: 1.30
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
  output_subdir: debug_splice_best_estimator_w48k2_confirmation
logging:
  save_predictions: true
EOF

run_one() {
  local seed="$1"
  local run_id="splice_best_estimator_w48k2_seed${seed}"
  local outdir="outputs/${run_id}"
  local json_path="results/${run_id}_argmax.json"
  local csv_path="results/${run_id}_predictions.csv"

  if [[ -s "${json_path}" ]]; then
    echo -e "germ_bo_w48k2_best\t${seed}\tskipped_existing\t${json_path}" | tee -a "${STATUS}"
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
  echo -e "germ_bo_w48k2_best\t${seed}\tdone\t${json_path}" | tee -a "${STATUS}"
}

for seed in 50 51 52 53 54; do
  run_one "${seed}"
done

PYTHONPATH=/home/sy/germ_bo_project CUDA_VISIBLE_DEVICES=3 ${PYTHON_BIN} tools/summarize_splice_best_estimator_w48k2_confirmation.py \
  >> "${RUN_LOG}" 2>&1

date -Iseconds > "${DONE}"
echo "splice_best_estimator_w48k2_confirmation_done"
