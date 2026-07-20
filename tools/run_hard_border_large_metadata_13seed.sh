#!/usr/bin/env bash
set -euo pipefail

cd ~/germ_bo_project

PYTHON_BIN="/home/sy/micromamba-bin/micromamba run -r /home/sy/micromamba -n germ-bo-py310 python"
CONFIG="configs/real_dnabert2_germ_bo_hard_border_large_metadata_comp027_p4.yaml"
RUN_LOG="results/hard_border_large_metadata_13seed_run.log"
STATUS="results/hard_border_large_metadata_13seed_status.tsv"
DONE="results/hard_border_large_metadata_13seed.done"

: > "${RUN_LOG}"
: > "${STATUS}"
rm -f "${DONE}"

run_one() {
  local seed="$1"
  local run_id="hard_border_large_metadata_comp027_p4_seed${seed}"
  local outdir="outputs/${run_id}"
  local json_path="results/${run_id}_threshold.json"
  local csv_path="results/${run_id}_predictions.csv"

  if [[ -s "${json_path}" ]]; then
    echo -e "${seed}\tskipped_existing\t${json_path}" | tee -a "${STATUS}"
    return 0
  fi

  echo "=== ${run_id} train ===" | tee -a "${RUN_LOG}"
  PYTHONPATH=/home/sy/germ_bo_project CUDA_VISIBLE_DEVICES=3 ${PYTHON_BIN} train.py \
    --config "${CONFIG}" \
    --seed "${seed}" \
    --output-dir "${outdir}" \
    >> "${RUN_LOG}" 2>&1

  echo "=== ${run_id} threshold/test ===" | tee -a "${RUN_LOG}"
  PYTHONPATH=/home/sy/germ_bo_project CUDA_VISIBLE_DEVICES=3 ${PYTHON_BIN} tools/tune_threshold.py \
    --config "${CONFIG}" \
    --checkpoint "${outdir}/checkpoints/best.pt" \
    --output-json "${json_path}" \
    --output-csv "${csv_path}" \
    >> "${RUN_LOG}" 2>&1

  rm -rf "${outdir}"
  echo -e "${seed}\tdone\t${json_path}" | tee -a "${STATUS}"
}

for seed in 42 43 44 45 46 47 48 49 50 51 52 53 54; do
  run_one "${seed}"
done

date -Iseconds > "${DONE}"
echo "hard_border_large_metadata_13seed_done"
