param(
  [string]$ProjectRoot = $PSScriptRoot + '\\..',
  [switch]$SkipDocker,
  [switch]$SkipFastAPI,
  [switch]$SkipUI
)

$ErrorActionPreference = 'Stop'

function Stop-ListeningProcesses {
  param([int]$Port)

  $conns = @()
  try {
    $conns = Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue
  } catch {
    $conns = @()
  }

  if (-not $conns -or $conns.Count -eq 0) {
    Write-Output "No listener on :$Port"
    return
  }

  $procIds = $conns | Select-Object -ExpandProperty OwningProcess -Unique
  foreach ($procId in $procIds) {
    if (-not $procId) { continue }
    try {
      $proc = Get-Process -Id $procId -ErrorAction SilentlyContinue
      $name = if ($proc) { $proc.ProcessName } else { 'unknown' }
      Write-Output "Stopping PID=$procId ($name) listening on :$Port"
      Stop-Process -Id $procId -Force -ErrorAction SilentlyContinue
    } catch {
      Write-Warning "Failed stopping PID=$procId on :$Port ($($_.Exception.Message))"
    }
  }
}

# Resolve absolute project root
$projRoot = (Resolve-Path $ProjectRoot).Path
Set-Location $projRoot

Write-Output "Project root: $projRoot"

if (-not $SkipUI) {
  # 1) Stop UI dev servers
  Stop-ListeningProcesses -Port 5173
  Stop-ListeningProcesses -Port 3002
} else {
  Write-Output "Skipping UI stop (:5173, :3002)"
}

if (-not $SkipFastAPI) {
  # 2) Stop FastAPI automation API
  Stop-ListeningProcesses -Port 8000
} else {
  Write-Output "Skipping FastAPI stop (:8000)"
}

if (-not $SkipDocker) {
  # 3) Stop Docker MCP filesystem
  if (Get-Command docker -ErrorAction SilentlyContinue) {
    try {
      Write-Output "Stopping Docker service: mcp-filesystem"
      & docker compose stop mcp-filesystem | Out-Null
      Write-Output "Stopped Docker service: mcp-filesystem"
    } catch {
      Write-Warning "Docker compose stop failed: $($_.Exception.Message)"
    }
  } else {
    Write-Warning "docker not found on PATH; skipping Docker stop"
  }
} else {
  Write-Output "Skipping Docker stop (mcp-filesystem)"
}

Write-Output "Stopped all known services (if they were running)."
