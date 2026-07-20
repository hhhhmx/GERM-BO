#!/usr/bin/env bash
set -euo pipefail

cd ~/germ_bo_project

export CUDA_VISIBLE_DEVICES=3
PYTHON_BIN="/home/sy/micromamba-bin/micromamba run -r /home/sy/micromamba -n germ-bo-py310 python"
RUN_LOG="results/splice_sites_all_quantile_estimator_quality_run.log"
DONE="results/splice_sites_all_quantile_estimator_quality.done"

: > "${RUN_LOG}"
rm -f "${DONE}"

run_prepare() {
  local tag="$1"
  local outdir="$2"
  shift 2
  echo "=== prepare ${tag} ===" | tee -a "${RUN_LOG}"
  PYTHONPATH=/home/sy/germ_bo_project CUDA_VISIBLE_DEVICES=3 ${PYTHON_BIN} tools/prepare_splice_sites_all.py \
    --output-dir "${outdir}" \
    --max-train 9000 \
    --max-val 1800 \
    --max-test 3000 \
    --estimator center_jsd \
    --window 64 \
    --search-radius 32 \
    --kmer 3 \
    --top-ratio 0.10 \
    --score-normalization train_quantile \
    "$@" \
    >> "${RUN_LOG}" 2>&1
}

run_prepare "q08_12" "data/benchmarks/splice_sites_all_larger_center_w64_k3_t10_quantile_q08_12" \
  --quantile-score-min 0.80 --quantile-score-max 1.20

run_prepare "q075_125" "data/benchmarks/splice_sites_all_larger_center_w64_k3_t10_quantile_q075_125" \
  --quantile-score-min 0.75 --quantile-score-max 1.25

run_prepare "q09_11" "data/benchmarks/splice_sites_all_larger_center_w64_k3_t10_quantile_q09_11" \
  --quantile-score-min 0.90 --quantile-score-max 1.10

PYTHONPATH=/home/sy/germ_bo_project CUDA_VISIBLE_DEVICES=3 ${PYTHON_BIN} tools/analyze_splice_estimator_quality.py \
  --split-dir data/benchmarks/splice_sites_all_larger_center_w64_k3_t10_quantile_q08_12 \
  --output-prefix results/splice_sites_all_larger_estimator_quality_quantile_q08_12 \
  >> "${RUN_LOG}" 2>&1

PYTHONPATH=/home/sy/germ_bo_project CUDA_VISIBLE_DEVICES=3 ${PYTHON_BIN} tools/analyze_splice_estimator_quality.py \
  --split-dir data/benchmarks/splice_sites_all_larger_center_w64_k3_t10_quantile_q075_125 \
  --output-prefix results/splice_sites_all_larger_estimator_quality_quantile_q075_125 \
  >> "${RUN_LOG}" 2>&1

PYTHONPATH=/home/sy/germ_bo_project CUDA_VISIBLE_DEVICES=3 ${PYTHON_BIN} tools/analyze_splice_estimator_quality.py \
  --split-dir data/benchmarks/splice_sites_all_larger_center_w64_k3_t10_quantile_q09_11 \
  --output-prefix results/splice_sites_all_larger_estimator_quality_quantile_q09_11 \
  >> "${RUN_LOG}" 2>&1

PYTHONPATH=/home/sy/germ_bo_project CUDA_VISIBLE_DEVICES=3 ${PYTHON_BIN} tools/summarize_splice_quantile_estimator_quality.py \
  >> "${RUN_LOG}" 2>&1

date -Iseconds > "${DONE}"
echo "splice_sites_all_quantile_estimator_quality_done"
