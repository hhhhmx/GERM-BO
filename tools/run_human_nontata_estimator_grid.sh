#!/usr/bin/env bash
set -euo pipefail

cd ~/germ_bo_project

export CUDA_VISIBLE_DEVICES=3
PYTHON_BIN="/home/sy/micromamba-bin/micromamba run -r /home/sy/micromamba -n germ-bo-py310 python"
RUN_LOG="results/human_nontata_estimator_grid_run.log"
STATUS="results/human_nontata_estimator_grid_status.tsv"
DONE="results/human_nontata_estimator_grid.done"

: > "${RUN_LOG}"
: > "${STATUS}"
rm -f "${DONE}"

PYTHONPATH=/home/sy/germ_bo_project ${PYTHON_BIN} tools/generate_human_nontata_estimator_grid.py \
  >> "${RUN_LOG}" 2>&1

prepare_one() {
  local tag="$1"
  local window="$2"
  local kmer="$3"
  local top_ratio="$4"
  local score_scale="$5"
  local split_dir="data/benchmarks/human_nontata_promoters_border_estimated_${tag}"

  if [[ -s "${split_dir}/train.csv" && -s "${split_dir}/val.csv" && -s "${split_dir}/test.csv" ]]; then
    echo -e "${tag}\tprepare\tskipped_existing\t${split_dir}" | tee -a "${STATUS}"
    return 0
  fi

  echo "=== prepare ${tag} ===" | tee -a "${RUN_LOG}"
  PYTHONPATH=/home/sy/germ_bo_project CUDA_VISIBLE_DEVICES=3 ${PYTHON_BIN} tools/prepare_genomic_benchmark.py \
    --dataset human_nontata_promoters \
    --source hf_parquet \
    --output-dir "${split_dir}" \
    --max-train 2000 \
    --max-val 500 \
    --max-test 1000 \
    --window "${window}" \
    --kmer "${kmer}" \
    --top-ratio "${top_ratio}" \
    --score-scale "${score_scale}" \
    >> "${RUN_LOG}" 2>&1
  echo -e "${tag}\tprepare\tdone\t${split_dir}" | tee -a "${STATUS}"
}

run_one() {
  local tag="$1"
  local seed="$2"
  local config="configs/real_dnabert2_germ_bo_human_nontata_promoters_metadata_estimated_${tag}.yaml"
  local run_id="human_nontata_estimator_${tag}_seed${seed}"
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

prepare_one "w16_k2_t10_s3" 16 2 0.10 3.0
prepare_one "w32_k2_t10_s3" 32 2 0.10 3.0
prepare_one "w64_k2_t10_s3" 64 2 0.10 3.0
prepare_one "w32_k3_t10_s3" 32 3 0.10 3.0
prepare_one "w32_k2_t20_s3" 32 2 0.20 3.0
prepare_one "w32_k2_t10_s6" 32 2 0.10 6.0

for tag in w16_k2_t10_s3 w32_k2_t10_s3 w64_k2_t10_s3 w32_k3_t10_s3 w32_k2_t20_s3 w32_k2_t10_s6; do
  for seed in 42 43 44; do
    run_one "${tag}" "${seed}"
  done
done

PYTHONPATH=/home/sy/germ_bo_project ${PYTHON_BIN} tools/summarize_human_nontata_estimator_grid.py \
  >> "${RUN_LOG}" 2>&1

date -Iseconds > "${DONE}"
echo "human_nontata_estimator_grid_done"
