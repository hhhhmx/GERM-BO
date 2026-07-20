#!/usr/bin/env bash
# Advisor-requested supplement: efficiency snapshot + LoRA rank sweep (controlled border_hard).
set -euo pipefail

cd ~/germ_bo_project

PYTHON_BIN="/home/sy/micromamba-bin/micromamba run -r /home/sy/micromamba -n germ-bo-py310 python"
GPU="${ADVISOR_GPU_ID:-3}"
export CUDA_VISIBLE_DEVICES="${GPU}"

RESULT_DIR="results/advisor_supplement"
mkdir -p "${RESULT_DIR}" configs/advisor_generated

echo "=== Efficiency snapshot (strict splice, seed 50) ===" | tee "${RESULT_DIR}/run.log"

run_efficiency() {
  local tag="$1"
  local config="$2"
  local run_id="advisor_efficiency_${tag}_seed50"
  local outdir="outputs/${run_id}"
  local json="${RESULT_DIR}/${run_id}_metrics.json"
  local snap="${RESULT_DIR}/${run_id}_snapshot.json"

  if [[ ! -s "${snap}" ]]; then
    PYTHONPATH=/home/sy/germ_bo_project ${PYTHON_BIN} tools/profile_adapter_snapshot.py \
      --config "${config}" \
      --seed 50 \
      --output-json "${snap}" >> "${RESULT_DIR}/run.log" 2>&1
  fi

  if [[ ! -s "${json}" ]]; then
    echo "--- train ${run_id} ---" | tee -a "${RESULT_DIR}/run.log"
    local start end
    start=$(date +%s)
    PYTHONPATH=/home/sy/germ_bo_project ${PYTHON_BIN} train.py \
      --config "${config}" \
      --seed 50 \
      --output-dir "${outdir}" >> "${RESULT_DIR}/run.log" 2>&1
    end=$(date +%s)
    echo "wall_seconds_${run_id}=$((end-start))" | tee -a "${RESULT_DIR}/run.log"
    cp "${outdir}/logs/train_metrics.json" "${json}"
  fi
}

run_efficiency "lora" "configs/real_dnabert2_lora_attention_output_classifier_splice_sites_all_kmer_balanced.yaml"
run_efficiency "germ_bo" "configs/real_dnabert2_germ_bo_quantile_q08_12_comp027_splice_sites_all_kmer_balanced.yaml"

echo "=== Rank sweep (border_hard metadata, ranks 4/8/16, seeds 42-44) ===" | tee -a "${RESULT_DIR}/run.log"
BASE="configs/real_dnabert2_germ_bo_border_hard_metadata_comp027_p4.yaml"
for rank in 4 8 16; do
  cfg="configs/advisor_generated/germ_bo_border_hard_metadata_rank${rank}_comp027.yaml"
  sed -E "s/^  rank: [0-9]+/  rank: ${rank}/" "${BASE}" > "${cfg}"
  for seed in 42 43 44; do
    run_id="advisor_rank${rank}_seed${seed}"
    outdir="outputs/${run_id}"
    json_path="results/${run_id}_threshold.json"
    if [[ -s "${json_path}" ]]; then
      echo "skip ${run_id}" | tee -a "${RESULT_DIR}/run.log"
      continue
    fi
    echo "--- ${run_id} ---" | tee -a "${RESULT_DIR}/run.log"
    PYTHONPATH=/home/sy/germ_bo_project ${PYTHON_BIN} train.py \
      --config "${cfg}" \
      --seed "${seed}" \
      --output-dir "${outdir}" >> "${RESULT_DIR}/run.log" 2>&1
    PYTHONPATH=/home/sy/germ_bo_project ${PYTHON_BIN} tools/tune_threshold.py \
      --config "${cfg}" \
      --checkpoint "${outdir}/checkpoints/best.pt" \
      --output-json "${json_path}" \
      --output-csv "results/${run_id}_predictions.csv" >> "${RESULT_DIR}/run.log" 2>&1
    rm -rf "${outdir}"
  done
done

date -Iseconds > "${RESULT_DIR}/done.txt"
echo "advisor_supplement_complete" | tee -a "${RESULT_DIR}/run.log"
