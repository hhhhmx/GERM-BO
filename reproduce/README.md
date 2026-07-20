# Reproduction Entry Points

These scripts provide reviewer-facing entry points for the Cell Reports Methods submission package. They assume commands are launched from the repository root or from this directory.

## Quick path

Run the smoke test first:

```powershell
powershell -ExecutionPolicy Bypass -File reproduce/00_smoke_debug.ps1
```

Regenerate summary artifacts from archived result files:

```powershell
powershell -ExecutionPolicy Bypass -File reproduce/01_controlled_main.ps1
powershell -ExecutionPolicy Bypass -File reproduce/02_strict_splice.ps1
powershell -ExecutionPolicy Bypass -File reproduce/03_tables_and_figures.ps1
```

## Full training path

Full training is single-GPU and can be slow. Add `-RunTraining` to rerun the key experiments:

```powershell
powershell -ExecutionPolicy Bypass -File reproduce/01_controlled_main.ps1 -RunTraining
powershell -ExecutionPolicy Bypass -File reproduce/02_strict_splice.ps1 -RunTraining
```

All scripts set `CUDA_VISIBLE_DEVICES=3` before launching Python.

