#!/usr/bin/env bash
# Cross-backbone strict splice (3-mer-balanced, label-free quantile estimator), seeds 50-54.
set -euo pipefail

cd ~/germ_bo_project

export CUDA_VISIBLE_DEVICES=3
PYTHON_BIN="/home/sy/micromamba-bin/micromamba run -r /home/sy/micromamba -n germ-bo-py310 python"
RUN_LOG="results/cross_backbone_splice_kmer_balanced_50_54_run.log"
STATUS="results/cross_backbone_splice_kmer_balanced_50_54_status.tsv"
DONE="results/cross_backbone_splice_kmer_balanced_50_54.done"

: > "${RUN_LOG}"
: > "${STATUS}"
rm -f "${DONE}"

run_one() {
  local backbone="$1"
  local method="$2"
  local config="$3"
  local seed="$4"
  local run_id="splice_kmer_balanced_crossbackbone_${backbone}_${method}_seed${seed}"
  local outdir="outputs/${run_id}"
  local json_path="results/${run_id}_argmax.json"

  if [[ -s "${json_path}" ]]; then
    echo -e "${backbone}\t${method}\t${seed}\tskipped_existing\t${json_path}" | tee -a "${STATUS}"
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
  echo -e "${backbone}\t${method}\t${seed}\tdone\t${json_path}" | tee -a "${STATUS}"
}

for seed in 50 51 52 53 54; do
  run_one "nt_v2_50m" "lora" "configs/real_nt_v2_50m_lora_splice_kmer_balanced.yaml" "${seed}"
  run_one "nt_v2_50m" "germ_bo_quantile" "configs/real_nt_v2_50m_germ_bo_quantile_splice_kmer_balanced.yaml" "${seed}"
  run_one "hyenadna_tiny" "lora" "configs/real_hyenadna_tiny_lora_splice_kmer_balanced.yaml" "${seed}"
  run_one "hyenadna_tiny" "germ_bo_quantile" "configs/real_hyenadna_tiny_germ_bo_quantile_splice_kmer_balanced.yaml" "${seed}"
done

PYTHONPATH=/home/sy/germ_bo_project ${PYTHON_BIN} tools/summarize_cross_backbone_splice_kmer_balanced.py \
  >> "${RUN_LOG}" 2>&1

date -Iseconds > "${DONE}"
echo "cross_backbone_splice_kmer_balanced_50_54_done"
