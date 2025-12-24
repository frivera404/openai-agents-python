param(
  [string]$ProjectRoot = $PSScriptRoot + '\\..',
  [switch]$SkipDocker,
  [switch]$SkipFastAPI,
  [switch]$SkipUI
)

# Backward-compatible wrapper around launch-all.ps1
& (Join-Path $PSScriptRoot 'launch-all.ps1') -ProjectRoot $ProjectRoot -SkipDocker:$SkipDocker -SkipFastAPI:$SkipFastAPI -SkipUI:$SkipUI
