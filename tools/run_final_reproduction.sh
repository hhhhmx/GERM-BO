#!/usr/bin/env bash
set -euo pipefail

cd ~/germ_bo_project

export CUDA_VISIBLE_DEVICES=3
PYTHON_BIN="/home/sy/micromamba-bin/micromamba run -r /home/sy/micromamba -n germ-bo-py310 python"

usage() {
  cat <<'USAGE'
Usage: bash tools/run_final_reproduction.sh <phase>

Phases:
  benchmark-pilot     Run UCI Promoter real benchmark pilot, 3 methods x 5 seeds.
  main-13seed         Run final hard-border-large metadata-driven 13-seed confirmation.
  mechanism-heldout   Run metadata-vs-activation mechanism held-out experiments.
  shuffled-ablation   Run metadata-shuffled leakage-control ablation.
  summaries           Regenerate final summary/statistics tables from existing JSON results.
  all                 Run all phases in the order above.

All training/evaluation commands explicitly set CUDA_VISIBLE_DEVICES=3 and use one visible GPU.
USAGE
}

run_summaries() {
  PYTHONPATH=/home/sy/germ_bo_project ${PYTHON_BIN} tools/summarize_hard_border_large_metadata.py
  PYTHONPATH=/home/sy/germ_bo_project ${PYTHON_BIN} tools/statistics_hard_border_large_metadata.py
  PYTHONPATH=/home/sy/germ_bo_project ${PYTHON_BIN} tools/summarize_metadata_vs_activation.py
  PYTHONPATH=/home/sy/germ_bo_project ${PYTHON_BIN} tools/statistics_metadata_mechanism.py
  PYTHONPATH=/home/sy/germ_bo_project ${PYTHON_BIN} tools/summarize_metadata_shuffled.py
  if [[ -s results/uci_promoter_baseline_lora_seed42_threshold.json ]]; then
    PYTHONPATH=/home/sy/germ_bo_project ${PYTHON_BIN} tools/summarize_uci_promoter_benchmark_pilot.py
  fi
}

phase="${1:-}"
if [[ -z "${phase}" ]]; then
  usage
  exit 2
fi

case "${phase}" in
  benchmark-pilot)
    CUDA_VISIBLE_DEVICES=3 bash tools/run_uci_promoter_benchmark_pilot.sh
    ;;
  main-13seed)
    CUDA_VISIBLE_DEVICES=3 bash tools/run_hard_border_large_metadata_13seed.sh
    ;;
  mechanism-heldout)
    CUDA_VISIBLE_DEVICES=3 bash tools/run_metadata_mechanism_heldout.sh
    ;;
  shuffled-ablation)
    CUDA_VISIBLE_DEVICES=3 bash tools/run_metadata_shuffled_heldout.sh
    ;;
  summaries)
    run_summaries
    ;;
  all)
    CUDA_VISIBLE_DEVICES=3 bash tools/run_uci_promoter_benchmark_pilot.sh
    CUDA_VISIBLE_DEVICES=3 bash tools/run_hard_border_large_metadata_13seed.sh
    CUDA_VISIBLE_DEVICES=3 bash tools/run_metadata_mechanism_heldout.sh
    CUDA_VISIBLE_DEVICES=3 bash tools/run_metadata_shuffled_heldout.sh
    run_summaries
    ;;
  *)
    usage
    exit 2
    ;;
esac
