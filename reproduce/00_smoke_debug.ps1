param(
    [string]$Python = "python"
)

$ErrorActionPreference = "Stop"
$RepoRoot = Split-Path -Parent $PSScriptRoot
Set-Location $RepoRoot

$env:CUDA_VISIBLE_DEVICES = "3"

Write-Host "Running GERM-BO mock-data smoke training..."
& $Python train.py --config configs/default.yaml --debug

Write-Host "Running GERM-BO mock-data smoke evaluation..."
& $Python eval.py --config configs/default.yaml --checkpoint outputs/debug/checkpoints/debug_last.pt --debug

Write-Host "Smoke test complete."

