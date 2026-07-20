#!/usr/bin/env bash
set -euo pipefail

cd ~/germ_bo_project

export CUDA_VISIBLE_DEVICES=3
PYTHON_BIN="/home/sy/micromamba-bin/micromamba run -r /home/sy/micromamba -n germ-bo-py310 python"
RUN_LOG="results/human_nontata_promoters_pilot_run.log"
STATUS="results/human_nontata_promoters_pilot_status.tsv"
DONE="results/human_nontata_promoters_pilot.done"

: > "${RUN_LOG}"
: > "${STATUS}"
rm -f "${DONE}"

PYTHONPATH=/home/sy/germ_bo_project CUDA_VISIBLE_DEVICES=3 ${PYTHON_BIN} tools/prepare_genomic_benchmark.py \
  --dataset human_nontata_promoters \
  --output-dir data/benchmarks/human_nontata_promoters_border_estimated \
  --max-train 2000 \
  --max-val 500 \
  --max-test 1000 \
  >> "${RUN_LOG}" 2>&1

run_one() {
  local method="$1"
  local config="$2"
  local seed="$3"
  local run_id="human_nontata_${method}_seed${seed}"
  local outdir="outputs/${run_id}"
  local json_path="results/${run_id}_threshold.json"
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

  echo "=== ${run_id} threshold/test ===" | tee -a "${RUN_LOG}"
  PYTHONPATH=/home/sy/germ_bo_project CUDA_VISIBLE_DEVICES=3 ${PYTHON_BIN} tools/tune_threshold.py \
    --config "${config}" \
    --checkpoint "${outdir}/checkpoints/best.pt" \
    --output-json "${json_path}" \
    --output-csv "${csv_path}" \
    >> "${RUN_LOG}" 2>&1

  rm -rf "${outdir}"
  echo -e "${method}\t${seed}\tdone\t${json_path}" | tee -a "${STATUS}"
}

for seed in 42 43 44; do
  run_one "baseline_lora" "configs/real_dnabert2_baseline_human_nontata_promoters_pilot.yaml" "${seed}"
  run_one "germ_bo_activation" "configs/real_dnabert2_germ_bo_human_nontata_promoters_activation_pilot.yaml" "${seed}"
  run_one "germ_bo_metadata_estimated" "configs/real_dnabert2_germ_bo_human_nontata_promoters_metadata_estimated_pilot.yaml" "${seed}"
done

PYTHONPATH=/home/sy/germ_bo_project ${PYTHON_BIN} tools/summarize_human_nontata_promoters_pilot.py \
  >> "${RUN_LOG}" 2>&1

date -Iseconds > "${DONE}"
echo "human_nontata_promoters_pilot_done"
