#!/usr/bin/env bash
set -euo pipefail

cd ~/germ_bo_project

export CUDA_VISIBLE_DEVICES=3
PYTHON_BIN="/home/sy/micromamba-bin/micromamba run -r /home/sy/micromamba -n germ-bo-py310 python"
RUN_LOG="results/nt_backbone_histone_pilot_run.log"
STATUS="results/nt_backbone_histone_pilot_status.tsv"
DONE="results/nt_backbone_histone_pilot.done"

HISTONE_TASKS=(
  H3
  H3K14ac
  H3K36me3
  H3K4me1
  H3K4me2
  H3K4me3
  H3K79me3
  H3K9ac
  H4
  H4ac
)

: > "${RUN_LOG}"
: > "${STATUS}"
rm -f "${DONE}"

PYTHONPATH=/home/sy/germ_bo_project ${PYTHON_BIN} tools/generate_nt_backbone_histone_configs.py \
  >> "${RUN_LOG}" 2>&1

run_one() {
  local task="$1"
  local method="$2"
  local config="$3"
  local seed="$4"
  local run_id="${task}_nt_v2_50m_${method}_seed${seed}"
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

for task in "${HISTONE_TASKS[@]}"; do
  for seed in 42 43 44; do
    run_one "${task}" "baseline_lora" "configs/real_nt_v2_50m_baseline_${task}_pilot.yaml" "${seed}"
    run_one "${task}" "germ_bo_center_jsd" "configs/real_nt_v2_50m_germ_bo_${task}_center_jsd_pilot.yaml" "${seed}"
  done
done

PYTHONPATH=/home/sy/germ_bo_project ${PYTHON_BIN} tools/summarize_nt_backbone_histone_pilot.py \
  >> "${RUN_LOG}" 2>&1

date -Iseconds > "${DONE}"
echo "nt_backbone_histone_pilot_done"
