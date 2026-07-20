#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${ROOT_DIR}"

PYTHON_BIN="/home/sy/micromamba-bin/micromamba run -r /home/sy/micromamba -n germ-bo-py310 python"
RUN_LOG="results/splice_sites_all_matched_shortcut_checks_run.log"
DONE="results/splice_sites_all_matched_shortcut_checks.done"
STATUS="results/splice_sites_all_matched_shortcut_checks_status.tsv"

mkdir -p results
: > "${RUN_LOG}"
printf "step\tstatus\tartifact\n" > "${STATUS}"
rm -f "${DONE}"

run_prepare() {
  local mode="$1"
  local output_dir="$2"
  local max_test="$3"
  echo "[prepare] ${mode}" | tee -a "${RUN_LOG}"
  PYTHONPATH=/home/sy/germ_bo_project CUDA_VISIBLE_DEVICES=3 ${PYTHON_BIN} tools/prepare_splice_sites_all_matched.py \
    --output-dir "${output_dir}" \
    --match-mode "${mode}" \
    --max-train 9000 \
    --max-val 1800 \
    --max-test "${max_test}" \
    --window 48 \
    --search-radius 24 \
    --kmer 2 \
    --top-ratio 0.25 \
    --score-normalization train_quantile \
    --quantile-score-min 0.80 \
    --quantile-score-max 1.20 | tee -a "${RUN_LOG}"
  printf "prepare_%s\tcompleted\t%s\n" "${mode}" "${output_dir}" >> "${STATUS}"
}

run_kmer() {
  local tag="$1"
  local split_dir="$2"
  local output_prefix="results/${tag}_kmer_comparison"
  echo "[kmer] ${tag}" | tee -a "${RUN_LOG}"
  PYTHONPATH=/home/sy/germ_bo_project CUDA_VISIBLE_DEVICES=3 ${PYTHON_BIN} tools/run_splice_sites_all_larger_kmer_comparison_models.py \
    --split-dir "${split_dir}" \
    --output-prefix "${output_prefix}" | tee -a "${RUN_LOG}"
  printf "kmer_%s\tcompleted\t%s\n" "${tag}" "${output_prefix}.md" >> "${STATUS}"
}

run_prepare "gc_matched" "data/benchmarks/splice_sites_all_gc_matched" 1800
run_prepare "kmer_balanced" "data/benchmarks/splice_sites_all_kmer_balanced" 1800
run_kmer "splice_sites_all_gc_matched" "data/benchmarks/splice_sites_all_gc_matched"
run_kmer "splice_sites_all_kmer_balanced" "data/benchmarks/splice_sites_all_kmer_balanced"

PYTHONPATH=/home/sy/germ_bo_project CUDA_VISIBLE_DEVICES=3 ${PYTHON_BIN} tools/summarize_splice_sites_all_matched_shortcut_checks.py | tee -a "${RUN_LOG}"
printf "summary\tcompleted\tresults/splice_sites_all_matched_shortcut_checks.md\n" >> "${STATUS}"
touch "${DONE}"
echo "splice_sites_all_matched_shortcut_checks_done" | tee -a "${RUN_LOG}"
