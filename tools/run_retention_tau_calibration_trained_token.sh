#!/usr/bin/env bash
# Token-level R_w(tau) calibration on trained LoRA / GERM-BO checkpoints (seed 50).
set -euo pipefail

cd ~/germ_bo_project

export CUDA_VISIBLE_DEVICES=3
PYTHON_BIN="/home/sy/micromamba-bin/micromamba run -r /home/sy/micromamba -n germ-bo-py310 python"
RUN_LOG="results/retention_tau_calibration_trained_token_run.log"
DONE="results/retention_tau_calibration_trained_token.done"
SEED=50

: > "${RUN_LOG}"
rm -f "${DONE}"

calibrate_token() {
  local split_tag="$1"
  local model_tag="$2"
  local config="$3"
  local run_id="retention_calib_train_${split_tag}_${model_tag}_seed${SEED}"
  local ckpt="outputs/${run_id}/checkpoints/best.pt"
  local json_path="results/retention_tau_calibration_trained_token_${split_tag}_${model_tag}_seed${SEED}.json"

  if [[ ! -s "${ckpt}" ]]; then
    echo "missing checkpoint ${ckpt}" | tee -a "${RUN_LOG}"
    return 1
  fi

  if [[ -s "${json_path}" ]]; then
    echo "skip existing ${json_path}" | tee -a "${RUN_LOG}"
    return 0
  fi

  echo "=== token calibrate ${split_tag} ${model_tag} ===" | tee -a "${RUN_LOG}"
  PYTHONPATH=/home/sy/germ_bo_project CUDA_VISIBLE_DEVICES=3 ${PYTHON_BIN} tools/calibrate_retention_tau.py \
    --config "${config}" \
    --checkpoint "${ckpt}" \
    --model-label "${model_tag}" \
    --pooling token \
    --output-json "${json_path}" \
    --target-clip-fraction 0.01 \
    --seed "${SEED}" \
    >> "${RUN_LOG}" 2>&1
}

calibrate_token "border_hard" "lora" "configs/real_dnabert2_baseline_border_hard_5seed.yaml"
calibrate_token "border_hard" "germ_bo" "configs/real_dnabert2_germ_bo_border_hard_metadata_comp027_p4.yaml"
calibrate_token "hard_border_large" "lora" "configs/real_dnabert2_baseline_hard_border_large_formal.yaml"
calibrate_token "hard_border_large" "germ_bo" "configs/real_dnabert2_germ_bo_hard_border_large_comp027_final_attn_output_classifier.yaml"

PYTHONPATH=/home/sy/germ_bo_project ${PYTHON_BIN} tools/summarize_retention_tau_calibration.py \
  --pattern "retention_tau_calibration_trained_token_*.json" \
  --output results/retention_tau_calibration_trained_token.md \
  >> "${RUN_LOG}" 2>&1

date -Iseconds > "${DONE}"
echo "retention_tau_calibration_trained_token_done" | tee -a "${RUN_LOG}"
