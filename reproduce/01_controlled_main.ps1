param(
    [string]$Python = "python",
    [int[]]$Seeds = @(42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54),
    [switch]$RunTraining
)

$ErrorActionPreference = "Stop"
$RepoRoot = Split-Path -Parent $PSScriptRoot
Set-Location $RepoRoot

$env:CUDA_VISIBLE_DEVICES = "3"
New-Item -ItemType Directory -Force -Path results | Out-Null
New-Item -ItemType Directory -Force -Path outputs | Out-Null

$MetadataConfig = "configs/real_dnabert2_germ_bo_hard_border_large_metadata_comp027_p4.yaml"

if ($RunTraining) {
    foreach ($Seed in $Seeds) {
        $RunId = "hard_border_large_metadata_comp027_p4_seed$Seed"
        $OutDir = "outputs/$RunId"
        $JsonPath = "results/${RunId}_threshold.json"
        $CsvPath = "results/${RunId}_predictions.csv"

        if (Test-Path $JsonPath) {
            Write-Host "Skipping existing $JsonPath"
            continue
        }

        Write-Host "Training $RunId"
        & $Python train.py --config $MetadataConfig --seed $Seed --output-dir $OutDir

        Write-Host "Evaluating threshold-tuned test metrics for $RunId"
        & $Python tools/tune_threshold.py `
            --config $MetadataConfig `
            --checkpoint "$OutDir/checkpoints/best.pt" `
            --output-json $JsonPath `
            --output-csv $CsvPath
    }
}

if (-not (Test-Path "results/hard_border_large_final_13seed_comparison.csv")) {
    Write-Warning "Missing results/hard_border_large_final_13seed_comparison.csv. The metadata summary script uses this archived file for the Baseline LoRA and activation-derived GERM-BO rows."
}

Write-Host "Regenerating hard-border-large metadata summaries..."
& $Python tools/summarize_hard_border_large_metadata.py
& $Python tools/statistics_hard_border_large_metadata.py

Write-Host "Controlled main reproduction complete."

