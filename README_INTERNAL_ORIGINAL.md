# GERM-BO

Minimal experimental repository for studying border-aware outlier compensation in genomic foundation model adaptation.

## Scope

This repository starts with a runnable mock-data pipeline and a small toy backbone. It is designed to be extended later with real genomic datasets and Hugging Face compatible backbones.

## Constraints

- Single-GPU only.
- All training and evaluation commands must explicitly use `CUDA_VISIBLE_DEVICES=3`.
- No DDP, `DataParallel`, DeepSpeed, or FSDP.
- Start from mock-data smoke tests before any real experiment.
- The code now enforces `CUDA_VISIBLE_DEVICES=3` when `device: cuda` is used.

## Structure

- `configs/`: YAML configs
- `src/data/`: mock and future real dataset interfaces
- `src/models/`: toy backbone and future backbone loader
- `src/adapters/`: baseline LoRA-style and GERM-BO adapters
- `src/utils/`: device, metrics, training, and border utilities
- `outputs/`: logs and checkpoints
- `results/`: evaluation artifacts

Real-data-ready additions:

- CSV/JSONL split loading from disk via `src/data/genomic_dataset.py`
- Hugging Face compatible backbone loading via `src/models/backbone_loader.py`
- Example real-data configs: `configs/real_baseline_lora.yaml`, `configs/real_germ_bo.yaml`
- Example split files under `data/splits/`

## Install

```bash
pip install -r requirements.txt
```

## Remote Server Usage

Run from the remote machine via `ssh gpu-server`.

```bash
ssh gpu-server
cd ~/germ_bo_project
/home/sy/micromamba-bin/micromamba run -r /home/sy/micromamba -n germ-bo-py310 python -m pip install -r requirements.txt
```

Recommended H20 environment bootstrap on `gpu-server`:

```bash
curl -L https://micro.mamba.pm/api/micromamba/linux-64/latest | tar -xvj -C ~/micromamba-bin --strip-components=1 bin/micromamba
~/micromamba-bin/micromamba create -y -r ~/micromamba -n germ-bo-py310 python=3.10 pip
~/micromamba-bin/micromamba run -r ~/micromamba -n germ-bo-py310 python -m pip install torch==2.5.1 --index-url https://download.pytorch.org/whl/cu124
~/micromamba-bin/micromamba run -r ~/micromamba -n germ-bo-py310 python -m pip install -r requirements.txt
```

## Smoke Test

```bash
CUDA_VISIBLE_DEVICES=3 /home/sy/micromamba-bin/micromamba run -r /home/sy/micromamba -n germ-bo-py310 python train.py --config configs/default.yaml --debug
CUDA_VISIBLE_DEVICES=3 /home/sy/micromamba-bin/micromamba run -r /home/sy/micromamba -n germ-bo-py310 python eval.py --config configs/default.yaml --checkpoint outputs/debug/checkpoints/debug_last.pt --debug
```

If the remote environment cannot execute on the H20 yet, use CPU fallback for the smoke test while still keeping the explicit GPU-selection prefix:

```bash
CUDA_VISIBLE_DEVICES=3 /home/sy/micromamba-bin/micromamba run -r /home/sy/micromamba -n germ-bo-py310 python train.py --config configs/default.yaml --debug --device cpu
CUDA_VISIBLE_DEVICES=3 /home/sy/micromamba-bin/micromamba run -r /home/sy/micromamba -n germ-bo-py310 python eval.py --config configs/default.yaml --checkpoint outputs/debug/checkpoints/debug_last.pt --debug --device cpu
```

## Baseline LoRA Debug

```bash
CUDA_VISIBLE_DEVICES=3 /home/sy/micromamba-bin/micromamba run -r /home/sy/micromamba -n germ-bo-py310 python train.py --config configs/baseline_lora.yaml --debug
```

## GERM-BO Debug

```bash
CUDA_VISIBLE_DEVICES=3 /home/sy/micromamba-bin/micromamba run -r /home/sy/micromamba -n germ-bo-py310 python train.py --config configs/germ_bo.yaml --debug
```

## Real Backbone / File-Based Data Smoke Test

These commands validate the file-based genomic dataset loader plus a Hugging Face backbone path. Replace the included sample split files and model path with your actual dataset and checkpoint before paper-scale runs.

```bash
CUDA_VISIBLE_DEVICES=3 /home/sy/micromamba-bin/micromamba run -r /home/sy/micromamba -n germ-bo-py310 python tools/create_hf_smoke_backbone.py
CUDA_VISIBLE_DEVICES=3 /home/sy/micromamba-bin/micromamba run -r /home/sy/micromamba -n germ-bo-py310 python train.py --config configs/real_baseline_lora.yaml --output-dir outputs/debug_real_baseline --debug
CUDA_VISIBLE_DEVICES=3 /home/sy/micromamba-bin/micromamba run -r /home/sy/micromamba -n germ-bo-py310 python train.py --config configs/real_germ_bo.yaml --output-dir outputs/debug_real_germ_bo --debug
```

For an offline HF smoke test that does not depend on `huggingface.co`, use:

```bash
CUDA_VISIBLE_DEVICES=3 /home/sy/micromamba-bin/micromamba run -r /home/sy/micromamba -n germ-bo-py310 python tools/create_hf_smoke_backbone.py
CUDA_VISIBLE_DEVICES=3 /home/sy/micromamba-bin/micromamba run -r /home/sy/micromamba -n germ-bo-py310 python train.py --config configs/real_hf_smoke_baseline.yaml --output-dir outputs/real_hf_smoke
```

## Notes

- `--debug` uses tiny synthetic DNA data and a short run for smoke testing.
- The current backbone is a toy encoder for engineering validation.
- The repository now also supports file-based genomic splits under `data/splits` and Hugging Face compatible backbones.
- `gpu_id: 3` refers to the physical GPU selection policy; after `CUDA_VISIBLE_DEVICES=3`, PyTorch will see that GPU as local device `cuda:0`.
- The validated H20 stack on `gpu-server` is `micromamba` + `Python 3.10` + `torch 2.5.1+cu124`.
- The current real-data configs keep LoRA / GERM-BO attached only to the top-level `classifier` head for a conservative first executable path.

## Checkpoints

Training now writes two checkpoint files under each run's `checkpoints/` directory:

- `debug_last.pt`: the final checkpoint, kept for backward compatibility with earlier commands.
- `best.pt`: the best validation checkpoint, selected by `train.checkpoint_monitor` and `train.checkpoint_mode`.

The default best-checkpoint rule is validation `loss` with `mode=min`. To select by another validation metric, add fields such as:

```yaml
train:
  checkpoint_monitor: f1
  checkpoint_mode: max
```

Early stopping is disabled by default. Enable it with the same monitored metric:

```yaml
train:
  checkpoint_monitor: loss
  checkpoint_mode: min
  early_stopping_patience: 2
  early_stopping_min_delta: 0.0
```

## Current Default

The current recommended real-backbone GERM-BO setting is the enlarged hard-border `attention.output + classifier` configuration:

- config: `configs/real_dnabert2_germ_bo_hard_border_large_comp027_final_attn_output_classifier.yaml`
- backbone: local `DNABERT-2-117M`
- split: `data/splits_hard_border_large`
- target modules: first two `attention.output.dense` layers plus `classifier`
- `compensation_strength: 0.27`
- `compensation_clip_min: 0.73`
- `compensation_clip_max: 1.42`
- checkpoint selection: validation `accuracy` with `mode=max`
- final reporting: validation-threshold tuned test evaluation

This setting is treated as the final formal default because 13-seed confirmation showed both higher mean accuracy and lower variance than `Wqkv + classifier`.

Secondary / ablation config:
`configs/real_dnabert2_germ_bo_hard_border_large_comp027_main_wqkv_classifier.yaml` is retained as the historical Wqkv secondary result. It should not be used as the final main config.

Deprecated config note:
`configs/real_dnabert2_germ_bo_mild_pilot.yaml` is retained only as an archival artifact from the tuning sweep. Do not use it as the primary config going forward; use `configs/real_dnabert2_germ_bo_pilot.yaml` instead.

Deprecated config note:
`configs/real_dnabert2_germ_bo_hard_border_large_comp027_formal.yaml` is retained only as the historical full `Wqkv + attention.output + classifier` ablation point. Do not use it as the primary hard-border formal config going forward.

Deprecated naming note:
`configs/real_dnabert2_germ_bo_hard_border_large_comp027_candidate_attn_output_classifier.yaml` is retained as the pre-promotion candidate filename. Prefer the final alias `configs/real_dnabert2_germ_bo_hard_border_large_comp027_final_attn_output_classifier.yaml`.

## Long-Run Configs

For paper-style longer single-GPU runs, use:

- `configs/real_dnabert2_baseline_longrun.yaml`
- `configs/real_dnabert2_germ_bo_longrun.yaml`

These long-run configs keep the same real DNABERT-2 backbone and adapter targets, but raise the experiment scale in a conservative single-GPU way:

- `seq_length: 256`
- `epochs: 12`
- `batch_size: 2`
- `lr: 3e-4`

Recommended launch pattern:

```bash
CUDA_VISIBLE_DEVICES=3 /home/sy/micromamba-bin/micromamba run -r /home/sy/micromamba -n germ-bo-py310 python train.py --config configs/real_dnabert2_baseline_longrun.yaml --output-dir outputs/longrun_real_dnabert2_baseline
CUDA_VISIBLE_DEVICES=3 /home/sy/micromamba-bin/micromamba run -r /home/sy/micromamba -n germ-bo-py310 python train.py --config configs/real_dnabert2_germ_bo_longrun.yaml --output-dir outputs/longrun_real_dnabert2_germ_bo
```
