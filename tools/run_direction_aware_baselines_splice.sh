#!/usr/bin/env bash
# Direction-aware PEFT baselines on strict 3-mer-balanced splice split (seeds 50-54).
set -euo pipefail

cd ~/germ_bo_project

export CUDA_VISIBLE_DEVICES=3
PYTHON_BIN="/home/sy/micromamba-bin/micromamba run -r /home/sy/micromamba -n germ-bo-py310 python"
RUN_LOG="results/direction_aware_baselines_splice_run.log"
STATUS="results/direction_aware_baselines_splice_status.tsv"
DONE="results/direction_aware_baselines_splice.done"
SPLIT="data/benchmarks/splice_sites_all_kmer_balanced"

: > "${RUN_LOG}"
: > "${STATUS}"
rm -f "${DONE}"

TM_ATTN="    - encoder.encoder.layer.0.attention.output.dense
    - encoder.encoder.layer.1.attention.output.dense
    - classifier"

write_config() {
  local path="$1"
  local adapter_name="$2"
  local border_score_type="${3:-metadata_border_score}"
  local compensation_strength="${4:-0.27}"

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
    train: ${SPLIT}/train.csv
    val: ${SPLIT}/val.csv
    test: ${SPLIT}/test.csv
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
${TM_ATTN}
EOF

  if [[ "${adapter_name}" == "germ_bo" ]]; then
    cat >> "${path}" <<EOF
  compensation_strength: ${compensation_strength}
  border_score_type: ${border_score_type}
  border_normalization: mean
  compensation_clip_min: 0.73
  compensation_clip_max: 1.42
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
  output_subdir: debug_direction_aware_baselines
logging:
  save_predictions: true
EOF
}

write_config "configs/real_dnabert2_gated_lora_splice_sites_all_kmer_balanced.yaml" "gated_lora"
write_config "configs/real_dnabert2_germ_bo_activation_splice_sites_all_kmer_balanced.yaml" "germ_bo" "activation_abs_mean" "0.27"

run_one() {
  local method="$1"
  local config="$2"
  local seed="$3"
  local run_id="splice_kmer_balanced_direction_${method}_seed${seed}"
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
  run_one "gated_lora" "configs/real_dnabert2_gated_lora_splice_sites_all_kmer_balanced.yaml" "${seed}"
  run_one "germ_bo_activation" "configs/real_dnabert2_germ_bo_activation_splice_sites_all_kmer_balanced.yaml" "${seed}"
done

PYTHONPATH=/home/sy/germ_bo_project ${PYTHON_BIN} tools/summarize_direction_aware_baselines_splice.py \
  >> "${RUN_LOG}" 2>&1

date -Iseconds > "${DONE}"
echo "direction_aware_baselines_splice_done" | tee -a "${RUN_LOG}"
