#!/usr/bin/env bash
set -euo pipefail

cd ~/germ_bo_project

export CUDA_VISIBLE_DEVICES=3
PYTHON_BIN="/home/sy/micromamba-bin/micromamba run -r /home/sy/micromamba -n germ-bo-py310 python"
RUN_LOG="results/human_nontata_ctx_tw16_heldout_run.log"
STATUS="results/human_nontata_ctx_tw16_heldout_status.tsv"
DONE="results/human_nontata_ctx_tw16_heldout.done"

: > "${RUN_LOG}"
: > "${STATUS}"
rm -f "${DONE}"

PYTHONPATH=/home/sy/germ_bo_project ${PYTHON_BIN} tools/generate_human_nontata_embedding_configs.py \
  >> "${RUN_LOG}" 2>&1

prepare_ctx_tw16() {
  local split_dir="data/benchmarks/human_nontata_promoters_embedding_ctx_tw16_t10_s015"
  if [[ -s "${split_dir}/train.csv" && -s "${split_dir}/val.csv" && -s "${split_dir}/test.csv" ]]; then
    echo -e "ctx_tw16_t10_s015\tprepare\tskipped_existing\t${split_dir}" | tee -a "${STATUS}"
    return 0
  fi
  echo "=== prepare ctx_tw16_t10_s015 ===" | tee -a "${RUN_LOG}"
  PYTHONPATH=/home/sy/germ_bo_project CUDA_VISIBLE_DEVICES=3 ${PYTHON_BIN} tools/prepare_embedding_boundary_scores.py \
    --source-dir data/benchmarks/human_nontata_promoters_border_estimated_w64_k2_t10_s3 \
    --output-dir "${split_dir}" \
    --model-path local_assets/dnabert2_117m \
    --seq-length 256 \
    --batch-size 8 \
    --token-window 16 \
    --top-ratio 0.10 \
    --score-scale 0.15 \
    --device cuda \
    --embedding-source contextual \
    >> "${RUN_LOG}" 2>&1
  echo -e "ctx_tw16_t10_s015\tprepare\tdone\t${split_dir}" | tee -a "${STATUS}"
}

run_one() {
  local method="$1"
  local config="$2"
  local seed="$3"
  local run_id="$4"
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

prepare_ctx_tw16

for seed in 45 46 47 48 49; do
  run_one "baseline_lora" \
    "configs/real_dnabert2_baseline_human_nontata_promoters_pilot.yaml" \
    "${seed}" \
    "human_nontata_heldout_baseline_lora_seed${seed}"
  run_one "ctx_tw16_t10_s015" \
    "configs/real_dnabert2_germ_bo_human_nontata_promoters_metadata_estimated_ctx_tw16_t10_s015.yaml" \
    "${seed}" \
    "human_nontata_heldout_ctx_tw16_t10_s015_seed${seed}"
done

PYTHONPATH=/home/sy/germ_bo_project ${PYTHON_BIN} tools/summarize_human_nontata_ctx_tw16_heldout.py \
  >> "${RUN_LOG}" 2>&1

date -Iseconds > "${DONE}"
echo "human_nontata_ctx_tw16_heldout_done"
