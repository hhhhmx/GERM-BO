#!/usr/bin/env bash
set -euo pipefail

cd ~/germ_bo_project

CONFIG="configs/real_dnabert2_germ_bo_border_medium_comp027_patience4.yaml"
PYTHON_BIN="/home/sy/micromamba-bin/micromamba run -r /home/sy/micromamba -n germ-bo-py310 python"
RUN_LOG="results/border_medium_patience4_42_46_run.log"

: > "${RUN_LOG}"

run_one() {
  local seed="$1"
  local outdir="outputs/stabilized_border_medium_patience4_seed${seed}"
  local json_path="results/stabilized_border_medium_patience4_seed${seed}_threshold.json"
  local csv_path="results/stabilized_border_medium_patience4_seed${seed}_predictions.csv"

  echo "=== seed ${seed} train ===" | tee -a "${RUN_LOG}"
  PYTHONPATH=/home/sy/germ_bo_project CUDA_VISIBLE_DEVICES=3 ${PYTHON_BIN} train.py \
    --config "${CONFIG}" \
    --seed "${seed}" \
    --output-dir "${outdir}" \
    >> "${RUN_LOG}" 2>&1

  echo "=== seed ${seed} threshold/test ===" | tee -a "${RUN_LOG}"
  PYTHONPATH=/home/sy/germ_bo_project CUDA_VISIBLE_DEVICES=3 ${PYTHON_BIN} tools/tune_threshold.py \
    --config "${CONFIG}" \
    --checkpoint "${outdir}/checkpoints/best.pt" \
    --output-json "${json_path}" \
    --output-csv "${csv_path}" \
    >> "${RUN_LOG}" 2>&1

  rm -rf "${outdir}"
  echo "=== seed ${seed} done ===" | tee -a "${RUN_LOG}"
}

for seed in 42 43 44 45 46; do
  run_one "${seed}"
done

echo "border_medium_patience4_42_46_done"
