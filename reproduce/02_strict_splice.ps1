param(
    [string]$Python = "python",
    [int[]]$Seeds = @(50, 51, 52, 53, 54),
    [switch]$RunTraining
)

$ErrorActionPreference = "Stop"
$RepoRoot = Split-Path -Parent $PSScriptRoot
Set-Location $RepoRoot

$env:CUDA_VISIBLE_DEVICES = "3"
New-Item -ItemType Directory -Force -Path results | Out-Null
New-Item -ItemType Directory -Force -Path outputs | Out-Null

$Runs = @(
    @{
        Method = "lora_attention_output_classifier"
        Config = "configs/real_dnabert2_lora_attention_output_classifier_splice_sites_all_kmer_balanced.yaml"
    },
    @{
        Method = "germ_bo_quantile_q08_12_comp027"
        Config = "configs/real_dnabert2_germ_bo_quantile_q08_12_comp027_splice_sites_all_kmer_balanced.yaml"
    }
)

if ($RunTraining) {
    foreach ($Seed in $Seeds) {
        foreach ($Run in $Runs) {
            $Method = $Run.Method
            $Config = $Run.Config
            $RunId = "splice_kmer_balanced_confirm_${Method}_seed$Seed"
            $OutDir = "outputs/$RunId"
            $JsonPath = "results/${RunId}_argmax.json"
            $CsvPath = "results/${RunId}_predictions.csv"

            if (Test-Path $JsonPath) {
                Write-Host "Skipping existing $JsonPath"
                continue
            }

            Write-Host "Training $RunId"
            & $Python train.py --config $Config --seed $Seed --output-dir $OutDir

            Write-Host "Evaluating argmax test metrics for $RunId"
            & $Python tools/evaluate_argmax.py `
                --config $Config `
                --checkpoint "$OutDir/checkpoints/best.pt" `
                --output-json $JsonPath `
                --output-csv $CsvPath
        }
    }
}

Write-Host "Regenerating strict splice summaries..."
& $Python tools/summarize_splice_kmer_balanced_confirmation_50_54.py
& $Python tools/statistics_splice_kmer_balanced.py

Write-Host "Strict splice reproduction complete."

