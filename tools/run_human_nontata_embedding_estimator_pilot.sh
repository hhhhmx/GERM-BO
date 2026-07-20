#!/usr/bin/env bash
set -euo pipefail

cd ~/germ_bo_project

export CUDA_VISIBLE_DEVICES=3
PYTHON_BIN="/home/sy/micromamba-bin/micromamba run -r /home/sy/micromamba -n germ-bo-py310 python"
RUN_LOG="results/human_nontata_embedding_estimator_pilot_run.log"
STATUS="results/human_nontata_embedding_estimator_pilot_status.tsv"
DONE="results/human_nontata_embedding_estimator_pilot.done"

: > "${RUN_LOG}"
: > "${STATUS}"
rm -f "${DONE}"

PYTHONPATH=/home/sy/germ_bo_project ${PYTHON_BIN} tools/generate_human_nontata_embedding_configs.py \
  >> "${RUN_LOG}" 2>&1

prepare_one() {
  local tag="$1"
  local token_window="$2"
  local top_ratio="$3"
  local score_scale="$4"
  local embedding_source="$5"
  local device="$6"
  local split_dir="data/benchmarks/human_nontata_promoters_embedding_${tag}"
  if [[ -s "${split_dir}/train.csv" && -s "${split_dir}/val.csv" && -s "${split_dir}/test.csv" ]]; then
    echo -e "${tag}\tprepare\tskipped_existing\t${split_dir}" | tee -a "${STATUS}"
    return 0
  fi
  echo "=== prepare embedding ${tag} ===" | tee -a "${RUN_LOG}"
  PYTHONPATH=/home/sy/germ_bo_project CUDA_VISIBLE_DEVICES=3 ${PYTHON_BIN} tools/prepare_embedding_boundary_scores.py \
    --source-dir data/benchmarks/human_nontata_promoters_border_estimated_w64_k2_t10_s3 \
    --output-dir "${split_dir}" \
    --model-path local_assets/dnabert2_117m \
    --seq-length 256 \
    --batch-size 8 \
    --token-window "${token_window}" \
    --top-ratio "${top_ratio}" \
    --score-scale "${score_scale}" \
    --device "${device}" \
    --embedding-source "${embedding_source}" \
    >> "${RUN_LOG}" 2>&1
  echo -e "${tag}\tprepare\tdone\t${split_dir}" | tee -a "${STATUS}"
}

run_one() {
  local tag="$1"
  local seed="$2"
  local config="configs/real_dnabert2_germ_bo_human_nontata_promoters_metadata_estimated_${tag}.yaml"
  local run_id="human_nontata_embedding_${tag}_seed${seed}"
  local outdir="outputs/${run_id}"
  local json_path="results/${run_id}_threshold.json"
  local csv_path="results/${run_id}_predictions.csv"
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
  echo "=== ${run_id} threshold/test ===" | tee -a "${RUN_LOG}"
  PYTHONPATH=/home/sy/germ_bo_project CUDA_VISIBLE_DEVICES=3 ${PYTHON_BIN} tools/tune_threshold.py \
    --config "${config}" \
    --checkpoint "${outdir}/checkpoints/best.pt" \
    --output-json "${json_path}" \
    --output-csv "${csv_path}" \
    >> "${RUN_LOG}" 2>&1
  rm -rf "${outdir}"
  echo -e "${tag}\t${seed}\tdone\t${json_path}" | tee -a "${STATUS}"
}

prepare_one "emb_tw8_t10_s015" 8 0.10 0.15 token_embedding cpu
prepare_one "emb_tw16_t10_s015" 16 0.10 0.15 token_embedding cpu
prepare_one "ctx_tw8_t10_s015" 8 0.10 0.15 contextual cuda
prepare_one "ctx_tw16_t10_s015" 16 0.10 0.15 contextual cuda

for tag in emb_tw8_t10_s015 emb_tw16_t10_s015 ctx_tw8_t10_s015 ctx_tw16_t10_s015; do
  for seed in 42 43 44; do
    run_one "${tag}" "${seed}"
  done
done

PYTHONPATH=/home/sy/germ_bo_project ${PYTHON_BIN} tools/summarize_human_nontata_embedding_estimator.py \
  >> "${RUN_LOG}" 2>&1

date -Iseconds > "${DONE}"
echo "human_nontata_embedding_estimator_pilot_done"
