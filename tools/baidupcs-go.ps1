param(
    [string]$BaiduPCSGoPath = "$PSScriptRoot\BaiduPCS-Go.exe",
    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]]$Args
)

$ErrorActionPreference = 'Stop'

if (-not (Test-Path -LiteralPath $BaiduPCSGoPath)) {
    throw "BaiduPCS-Go not found at $BaiduPCSGoPath. Put BaiduPCS-Go.exe next to this script or pass -BaiduPCSGoPath."
}

& $BaiduPCSGoPath @Args

