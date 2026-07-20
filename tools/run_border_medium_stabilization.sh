set -euo pipefail
cd ~/germ_bo_project
: > results/border_medium_stabilization_run.log

run_one() {
  local tag="$1"
  local config="$2"
  local seed="$3"
  local outdir="outputs/${tag}_seed${seed}"
  PYTHONPATH=/home/sy/germ_bo_project CUDA_VISIBLE_DEVICES=3 /home/sy/micromamba-bin/micromamba run -r /home/sy/micromamba -n germ-bo-py310 python train.py --config "$config" --seed "$seed" --output-dir "$outdir" >> results/border_medium_stabilization_run.log 2>&1
  PYTHONPATH=/home/sy/germ_bo_project CUDA_VISIBLE_DEVICES=3 /home/sy/micromamba-bin/micromamba run -r /home/sy/micromamba -n germ-bo-py310 python tools/tune_threshold.py --config "$config" --checkpoint "$outdir/checkpoints/best.pt" --output-json "results/${tag}_seed${seed}_threshold.json" --output-csv "results/${tag}_seed${seed}_predictions.csv" >> results/border_medium_stabilization_run.log 2>&1
  rm -rf "$outdir"
}

for seed in 47 48 49 50 51; do
  run_one stab_border_medium_final configs/real_dnabert2_germ_bo_border_medium_5seed.yaml "$seed"
done

run_one stab_border_medium_comp027_patience4 configs/real_dnabert2_germ_bo_border_medium_comp027_patience4.yaml 46
run_one stab_border_medium_comp015 configs/real_dnabert2_germ_bo_border_medium_comp015_5seed.yaml 46
run_one stab_border_medium_comp020 configs/real_dnabert2_germ_bo_border_medium_comp020_5seed.yaml 46

echo border_medium_stabilization_done
