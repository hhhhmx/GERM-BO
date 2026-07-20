#!/usr/bin/env bash
set -euo pipefail

cd ~/germ_bo_project

export CUDA_VISIBLE_DEVICES=3
export HF_ENDPOINT="${HF_ENDPOINT:-https://hf-mirror.com}"
PYTHON_BIN="/home/sy/micromamba-bin/micromamba run -r /home/sy/micromamba -n germ-bo-py310 python"
RUN_LOG="results/nt_downstream_pilot_run.log"
STATUS="results/nt_downstream_pilot_status.tsv"
DONE="results/nt_downstream_pilot.done"

: > "${RUN_LOG}"
: > "${STATUS}"
rm -f "${DONE}"

prepare_task() {
  local task="$1"
  echo "=== prepare ${task} ===" | tee -a "${RUN_LOG}"
  PYTHONPATH=/home/sy/germ_bo_project CUDA_VISIBLE_DEVICES=3 ${PYTHON_BIN} tools/prepare_nt_downstream_task.py \
    --task-name "${task}" \
    --download-from-hf \
    --output-dir "data/benchmarks/${task}_center_jsd" \
    --max-train 2000 \
    --max-val 500 \
    --max-test 1000 \
    --score-normalization train_quantile \
    >> "${RUN_LOG}" 2>&1
}

prepare_task "H3K4me3"
prepare_task "enhancers"

run_one() {
  local task="$1"
  local method="$2"
  local config="$3"
  local seed="$4"
  local run_id="${task}_${method}_seed${seed}"
  local outdir="outputs/${run_id}"
  local json_path="results/${run_id}_argmax.json"

  if [[ -s "${json_path}" ]]; then
    echo -e "${task}\t${method}\t${seed}\tskipped_existing\t${json_path}" | tee -a "${STATUS}"
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
    --output-csv "results/${run_id}_predictions.csv" \
    >> "${RUN_LOG}" 2>&1

  rm -rf "${outdir}"
  echo -e "${task}\t${method}\t${seed}\tdone\t${json_path}" | tee -a "${STATUS}"
}

for seed in 42 43 44; do
  run_one "H3K4me3" "baseline_lora" "configs/real_dnabert2_baseline_H3K4me3_pilot.yaml" "${seed}"
  run_one "H3K4me3" "germ_bo_center_jsd" "configs/real_dnabert2_germ_bo_H3K4me3_center_jsd_pilot.yaml" "${seed}"
  run_one "enhancers" "baseline_lora" "configs/real_dnabert2_baseline_enhancers_pilot.yaml" "${seed}"
  run_one "enhancers" "germ_bo_center_jsd" "configs/real_dnabert2_germ_bo_enhancers_center_jsd_pilot.yaml" "${seed}"
done

PYTHONPATH=/home/sy/germ_bo_project ${PYTHON_BIN} tools/summarize_nt_downstream_pilot.py \
  >> "${RUN_LOG}" 2>&1

date -Iseconds > "${DONE}"
echo "nt_downstream_pilot_done"
