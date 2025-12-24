param(
  [string]$ProjectRoot = $PSScriptRoot + '\\..',
  [switch]$SkipDocker,
  [switch]$SkipFastAPI
)

$ErrorActionPreference = 'Stop'

function Test-Port {
  param([int]$Port)
  try {
    $conn = Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue | Select-Object -First 1
    return [bool]$conn
  } catch {
    return $false
  }
}

$projRoot = (Resolve-Path $ProjectRoot).Path
Set-Location $projRoot

# 1) Start everything except UI first
& (Join-Path $PSScriptRoot 'start-all.ps1') -ProjectRoot $projRoot -SkipUI -SkipDocker:$SkipDocker -SkipFastAPI:$SkipFastAPI

# 2) Then start UI in the foreground so logs stay in this terminal
if (-not (Get-Command npm -ErrorAction SilentlyContinue)) {
  Write-Error "npm is not on PATH. Install Node.js and try again."
  exit 1
}

if ((Test-Port 5173) -and (Test-Port 3002)) {
  Write-Output "UI already appears to be running (:5173 and :3002 are listening)"
  exit 0
}

Write-Output "Starting UI dev servers in foreground (npm run dev)"
# Invoke the Windows cmd shim `npm.cmd` when available to avoid PowerShell wrapper recursion
if (Get-Command npm.cmd -ErrorAction SilentlyContinue) {
  & npm.cmd run dev
} else {
  # Fallback: run through cmd.exe to avoid PowerShell npm.ps1 wrapper recursion.
  Write-Output "Falling back to cmd /c npm run dev to avoid PowerShell wrapper recursion"
  cmd /c "npm run dev"
}
