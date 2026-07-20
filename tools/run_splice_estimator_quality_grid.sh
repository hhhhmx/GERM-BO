#!/usr/bin/env bash
set -euo pipefail

cd ~/germ_bo_project

export CUDA_VISIBLE_DEVICES=3
PYTHON_BIN="/home/sy/micromamba-bin/micromamba run -r /home/sy/micromamba -n germ-bo-py310 python"
RUN_LOG="results/splice_estimator_quality_grid_run.log"
STATUS="results/splice_estimator_quality_grid_status.tsv"
DONE="results/splice_estimator_quality_grid.done"

: > "${RUN_LOG}"
: > "${STATUS}"
rm -f "${DONE}"

run_one() {
  local window="$1"
  local kmer="$2"
  local top_ratio="$3"
  local normalization="$4"
  local score_min="$5"
  local score_max="$6"
  local top_tag="${top_ratio/./}"
  local min_tag="${score_min/./}"
  local max_tag="${score_max/./}"
  local tag="w${window}_k${kmer}_t${top_tag}_${normalization}_r${min_tag}_${max_tag}"
  local split_dir="data/benchmarks/splice_estimator_grid_${tag}"
  local output_prefix="results/splice_estimator_quality_grid_${tag}"

  if [[ -s "${output_prefix}_score_by_label.csv" && -s "${output_prefix}_prediction_summary.csv" ]]; then
    echo -e "${tag}\tskipped_existing\t${output_prefix}" | tee -a "${STATUS}"
    return 0
  fi

  echo "=== ${tag} prepare ===" | tee -a "${RUN_LOG}"
  PYTHONPATH=/home/sy/germ_bo_project CUDA_VISIBLE_DEVICES=3 ${PYTHON_BIN} tools/prepare_splice_sites_all.py \
    --output-dir "${split_dir}" \
    --max-train 9000 \
    --max-val 1800 \
    --max-test 3000 \
    --estimator center_jsd \
    --window "${window}" \
    --search-radius "$((window / 2))" \
    --kmer "${kmer}" \
    --top-ratio "${top_ratio}" \
    --score-normalization "${normalization}" \
    --quantile-score-min "${score_min}" \
    --quantile-score-max "${score_max}" \
    >> "${RUN_LOG}" 2>&1

  echo "=== ${tag} analyze ===" | tee -a "${RUN_LOG}"
  PYTHONPATH=/home/sy/germ_bo_project CUDA_VISIBLE_DEVICES=3 ${PYTHON_BIN} tools/analyze_splice_estimator_quality.py \
    --split-dir "${split_dir}" \
    --output-prefix "${output_prefix}" \
    >> "${RUN_LOG}" 2>&1

  echo -e "${tag}\tdone\t${output_prefix}" | tee -a "${STATUS}"
}

for window in 32 48 64; do
  for kmer in 2 3; do
    for top_ratio in 0.25 0.5 1.0; do
      for normalization in train_minmax train_quantile; do
        for range_pair in 0.8:1.2 0.7:1.3; do
          score_min="${range_pair%%:*}"
          score_max="${range_pair##*:}"
          run_one "${window}" "${kmer}" "${top_ratio}" "${normalization}" "${score_min}" "${score_max}"
        done
      done
    done
  done
done

PYTHONPATH=/home/sy/germ_bo_project CUDA_VISIBLE_DEVICES=3 ${PYTHON_BIN} tools/summarize_splice_estimator_quality_grid.py \
  >> "${RUN_LOG}" 2>&1

date -Iseconds > "${DONE}"
echo "splice_estimator_quality_grid_done"
