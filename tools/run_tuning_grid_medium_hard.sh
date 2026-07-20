#!/usr/bin/env bash
set -euo pipefail

cd ~/germ_bo_project

PYTHON_BIN="/home/sy/micromamba-bin/micromamba run -r /home/sy/micromamba -n germ-bo-py310 python"
RUN_LOG="results/tuning_border_medium_hard_grid_run.log"
STATUS="results/tuning_border_medium_hard_grid_status.tsv"
DONE="results/tuning_border_medium_hard_grid.done"

: > "${RUN_LOG}"
: > "${STATUS}"
rm -f "${DONE}"

run_one() {
  local task="$1"
  local comp="$2"
  local seed="$3"
  local config="configs/real_dnabert2_germ_bo_border_${task}_comp${comp}_p4_tuning.yaml"
  local run_id="tuning_${task}_comp${comp}_p4_seed${seed}"
  local outdir="outputs/${run_id}"
  local json_path="results/${run_id}_threshold.json"
  local csv_path="results/${run_id}_predictions.csv"

  if [[ -s "${json_path}" ]]; then
    echo -e "${task}\t${comp}\t${seed}\tskipped_existing\t${json_path}" | tee -a "${STATUS}"
    return 0
  fi

  echo "=== ${run_id} train ===" | tee -a "${RUN_LOG}"
  PYTHONPATH=/home/sy/germ_bo_project CUDA_VISIBLE_DEVICES=3 ${PYTHON_BIN} train.py \
    --config "${config}" \
    --seed "${seed}" \
    --output-dir "${outdir}" \
    >> "${RUN_LOG}" 2>&1

  echo "=== ${run_id} threshold/test ===" | tee -a "${RUN_LOG}"
  PYTHONPATH=/home/sy/germ_bo_project CUDA_VISIBLE_DEVICES=3 ${PYTHON_BIN} tools/tune_threshold.py \
    --config "${config}" \
    --checkpoint "${outdir}/checkpoints/best.pt" \
    --output-json "${json_path}" \
    --output-csv "${csv_path}" \
    >> "${RUN_LOG}" 2>&1

  rm -rf "${outdir}"
  echo -e "${task}\t${comp}\t${seed}\tdone\t${json_path}" | tee -a "${STATUS}"
}

for task in medium hard; do
  for comp in 015 020 025 027; do
    for seed in 42 43 44 45 46; do
      run_one "${task}" "${comp}" "${seed}"
    done
  done
done

date -Iseconds > "${DONE}"
echo "tuning_border_medium_hard_grid_done"
