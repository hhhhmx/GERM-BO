#!/usr/bin/env bash
set -euo pipefail

cd ~/germ_bo_project

export CUDA_VISIBLE_DEVICES=3
PYTHON_BIN="/home/sy/micromamba-bin/micromamba run -r /home/sy/micromamba -n germ-bo-py310 python"
RUN_LOG="results/splice_quantile_q08_12_confirmation_50_54_run.log"
STATUS="results/splice_quantile_q08_12_confirmation_50_54_status.tsv"
DONE="results/splice_quantile_q08_12_confirmation_50_54.done"

: > "${RUN_LOG}"
: > "${STATUS}"
rm -f "${DONE}"

run_one() {
  local method="$1"
  local config="$2"
  local seed="$3"
  local run_id="splice_quantile_q08_12_confirm_${method}_seed${seed}"
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
  run_one "lora_attention_output_classifier" \
    "configs/real_dnabert2_lora_attention_output_classifier_splice_sites_all_larger_ablation.yaml" \
    "${seed}"
  run_one "germ_bo_quantile_q08_12_comp027" \
    "configs/real_dnabert2_germ_bo_quantile_q08_12_comp027_splice_sites_all_quantile.yaml" \
    "${seed}"
done

PYTHONPATH=/home/sy/germ_bo_project CUDA_VISIBLE_DEVICES=3 ${PYTHON_BIN} tools/summarize_splice_quantile_confirmation_50_54.py \
  >> "${RUN_LOG}" 2>&1

date -Iseconds > "${DONE}"
echo "splice_quantile_q08_12_confirmation_50_54_done"
