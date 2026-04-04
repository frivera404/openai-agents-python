param(
  [switch]$Remove,
  [switch]$StopServices
)

$ErrorActionPreference = 'Continue'

function Test-Port { param([int]$Port) try { $conn = Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue | Select-Object -First 1; return [bool]$conn } catch { return $false } }

$projRoot = (Resolve-Path "$PSScriptRoot\..\").Path
Set-Location $projRoot

Write-Output "Project root: $projRoot"

if ($StopServices) {
  Write-Output "Stopping services (safe)..."
  try {
    & (Join-Path $PSScriptRoot 'stop-all.ps1') -ProjectRoot $projRoot -SkipUI:$false -SkipFastAPI:$false -SkipDocker:$false
  } catch {
    Write-Warning "stop-all.ps1 failed: $($_.Exception.Message)"
  }
}

# Candidate cleanup targets (non-destructive by default)
$targets = @(
  'dist',
  '__pycache__',
  '.pytest_cache',
  'node_modules/.vite',
  'node_modules/.cache',
  '.venv/.cache',
  'coverage.xml',
  'coverage',
  'build',
  'docs/site'
)

$found = @()
foreach ($t in $targets) {
  $full = Join-Path $projRoot $t
  if (Test-Path $full) { $found += $full }
}

if (-not $found -or $found.Count -eq 0) {
  Write-Output "No known temp/build targets found."
} else {
  Write-Output "Found these candidate files/directories to cleanup:"
  $found | ForEach-Object { Write-Output "  $_" }
}

if ($Remove) {
  Write-Output "Removing found targets..."
  foreach ($p in $found) {
    try {
      # Try normal removal first. Do not use low-level handles that could lock files.
      Remove-Item -LiteralPath $p -Recurse -Force -ErrorAction Stop
      Write-Output "Removed: $p"
    } catch {
      Write-Warning "Failed to remove $p (may be in use): $($_.Exception.Message)"
    }
  }
  Write-Output "Cleanup complete."
} else {
  if ($found.Count -gt 0) {
    Write-Output "No files deleted. To remove the listed targets, re-run this script with the -Remove switch."
  }
}
