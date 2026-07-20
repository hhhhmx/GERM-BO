param(
    [string]$Python = "python"
)

$ErrorActionPreference = "Stop"
$RepoRoot = Split-Path -Parent $PSScriptRoot
Set-Location $RepoRoot

$env:CUDA_VISIBLE_DEVICES = "3"

Write-Host "Regenerating manuscript figures where source data are available..."
& $Python tools/plot_experiment_figures.py

Write-Host "Regenerating key summary tables..."
& $Python tools/summarize_hard_border_large_metadata.py
& $Python tools/statistics_hard_border_large_metadata.py
& $Python tools/summarize_splice_kmer_balanced_confirmation_50_54.py
& $Python tools/statistics_splice_kmer_balanced.py
& $Python tools/summarize_direction_aware_baselines_splice.py
& $Python tools/summarize_cross_backbone_border_hard.py

Write-Host "Table and figure regeneration complete."

