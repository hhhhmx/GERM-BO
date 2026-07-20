#!/usr/bin/env bash
set -euo pipefail

cd ~/germ_bo_project
export CUDA_VISIBLE_DEVICES=3
PYTHON_BIN="/home/sy/micromamba-bin/micromamba run -r /home/sy/micromamba -n germ-bo-py310 python"
RUN_LOG="results/retention_tau_calibration_run.log"
DONE="results/retention_tau_calibration.done"

: > "${RUN_LOG}"
rm -f "${DONE}"

run_one() {
  local split_tag="$1"
  local config="$2"
  local output_json="results/retention_tau_calibration_${split_tag}.json"
  if [[ -s "${output_json}" ]]; then
    echo "skip existing ${output_json}" | tee -a "${RUN_LOG}"
    return 0
  fi
  echo "=== calibrate ${split_tag} ===" | tee -a "${RUN_LOG}"
  PYTHONPATH=/home/sy/germ_bo_project CUDA_VISIBLE_DEVICES=3 ${PYTHON_BIN} tools/calibrate_retention_tau.py \
    --config "${config}" \
    --output-json "${output_json}" \
    --target-clip-fraction 0.01 \
    --seed 42 \
    >> "${RUN_LOG}" 2>&1
}

run_one "border_hard" "configs/calibration_retention_tau_border_hard.yaml"
run_one "hard_border_large" "configs/calibration_retention_tau_hard_border_large.yaml"

PYTHONPATH=/home/sy/germ_bo_project ${PYTHON_BIN} tools/summarize_retention_tau_calibration.py \
  --pattern "retention_tau_calibration_*.json" \
  >> "${RUN_LOG}" 2>&1

date -Iseconds > "${DONE}"
echo "retention_tau_calibration_done" | tee -a "${RUN_LOG}"
