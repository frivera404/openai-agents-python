param(
  [string]$ProjectRoot = $PSScriptRoot + '\..',
  [switch]$SkipDocker,
  [switch]$SkipFastAPI,
  [switch]$SkipUI
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

# Resolve absolute project root
$projRoot = (Resolve-Path $ProjectRoot).Path
Set-Location $projRoot

Write-Output "Project root: $projRoot"

if (-not $SkipDocker) {
  # 1) Docker MCP filesystem
  if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
    Write-Error "docker is not on PATH. Install Docker Desktop and try again."
    exit 1
  }

  Write-Output "Starting Docker service: mcp-filesystem (port 3000 -> 8000)"
  & docker compose up -d --build mcp-filesystem
} else {
  Write-Output "Skipping Docker (mcp-filesystem)"
}

if (-not $SkipFastAPI) {
  # 2) FastAPI automation API (port 8000)
  if (-not (Get-Command uv -ErrorAction SilentlyContinue)) {
    Write-Error "uv is not on PATH. Install uv (https://astral.sh/uv) and try again."
    exit 1
  }

  if (Test-Port 8000) {
    Write-Output "FastAPI already listening on :8000"
  } else {
    Write-Output "Starting FastAPI on http://127.0.0.1:8000 (hidden window)"
    Start-Process -WorkingDirectory $projRoot -FilePath "uv" -ArgumentList @(
      "run",
      "uvicorn",
      "src.agents.http_prime_goal_api:app",
      "--host",
      "127.0.0.1",
      "--port",
      "8000"
    ) -WindowStyle Hidden | Out-Null
  }
} else {
  Write-Output "Skipping FastAPI (:8000)"
}

if (-not $SkipFastAPI) {
  # Quick readiness checks
  $deadline = (Get-Date).AddSeconds(15)
  $ok = $false
  while ((Get-Date) -lt $deadline) {
    try {
      $status = (Invoke-WebRequest -UseBasicParsing "http://127.0.0.1:8000/health" -TimeoutSec 2).StatusCode
      if ($status -eq 200) { $ok = $true; break }
    } catch {
      Start-Sleep -Milliseconds 500
    }
  }

  if ($ok) {
    Write-Output "OK: FastAPI healthcheck http://127.0.0.1:8000/health"
  } else {
    Write-Warning "FastAPI did not become healthy within 15s. Check running processes/ports."
  }
}

# 3) UI dev server (Vite + Express) - started last so backends are ready first.
if (-not $SkipUI) {
  if (-not (Get-Command npm -ErrorAction SilentlyContinue)) {
    Write-Error "npm is not on PATH. Install Node.js and try again."
    exit 1
  }

  $needUi = -not (Test-Port 5173) -or -not (Test-Port 3002)
  if ($needUi) {
    Write-Output "Starting UI dev servers (Vite :5173 + Express :3002)"
    Start-Process -WorkingDirectory $projRoot -FilePath "npm" -ArgumentList @("run", "dev") -WindowStyle Normal | Out-Null
  } else {
    Write-Output "UI already appears to be running (:5173 and :3002 are listening)"
  }
} else {
  Write-Output "Skipping UI (Vite :5173 + Express :3002)"
}

Write-Output "URLs:"
Write-Output "  FastAPI automation: http://127.0.0.1:8000"
Write-Output "  Docker filesystem MCP: http://127.0.0.1:3000/mcp"
Write-Output "  UI (Vite): http://127.0.0.1:5173"
Write-Output "  UI backend (Express): http://127.0.0.1:3002"
