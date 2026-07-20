#!/usr/bin/env bash
# Cross-backbone replication on border_hard (NT v2 50m + HyenaDNA tiny), seeds 50-54.
set -euo pipefail

cd ~/germ_bo_project

export CUDA_VISIBLE_DEVICES=3
PYTHON_BIN="/home/sy/micromamba-bin/micromamba run -r /home/sy/micromamba -n germ-bo-py310 python"
RUN_LOG="results/cross_backbone_border_hard_run.log"
STATUS="results/cross_backbone_border_hard_status.tsv"
DONE="results/cross_backbone_border_hard.done"

: > "${RUN_LOG}"
: > "${STATUS}"
rm -f "${DONE}"

run_one() {
  local tag="$1"
  local config="$2"
  local seed="$3"
  local run_id="cross_backbone_${tag}_border_hard_seed${seed}"
  local outdir="outputs/${run_id}"
  local json_path="results/${run_id}_argmax.json"

  if [[ -s "${json_path}" ]]; then
    echo -e "${tag}\t${seed}\tskipped_existing\t${json_path}" | tee -a "${STATUS}"
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
  echo -e "${tag}\t${seed}\tdone\t${json_path}" | tee -a "${STATUS}"
}

for seed in 50 51 52 53 54; do
  run_one "nt_v2_50m_lora" "configs/real_nt_v2_50m_lora_border_hard.yaml" "${seed}"
  run_one "nt_v2_50m_germ_bo" "configs/real_nt_v2_50m_germ_bo_border_hard.yaml" "${seed}"
  run_one "hyenadna_tiny_lora" "configs/real_hyenadna_tiny_lora_border_hard.yaml" "${seed}"
  run_one "hyenadna_tiny_germ_bo" "configs/real_hyenadna_tiny_germ_bo_border_hard.yaml" "${seed}"
done

PYTHONPATH=/home/sy/germ_bo_project ${PYTHON_BIN} tools/summarize_cross_backbone_border_hard.py \
  >> "${RUN_LOG}" 2>&1

date -Iseconds > "${DONE}"
echo "cross_backbone_border_hard_done" | tee -a "${RUN_LOG}"
