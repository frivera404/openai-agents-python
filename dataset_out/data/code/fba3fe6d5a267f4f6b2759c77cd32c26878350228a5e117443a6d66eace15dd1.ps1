param(
    [string]$RedisUrl = $env:REDIS_URL,
    [string]$LogFile = ".\scripts\logs\task-loop.log",
    [string]$PidFile = ".agent_state\task_loop.pid",
    [switch]$Force
)

# Ensure paths
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
# Compute project root as parent of the scripts folder; be defensive if resolution fails.
try {
    $projectRoot = Resolve-Path (Join-Path $scriptDir "..") -ErrorAction Stop
    Set-Location -Path $projectRoot.Path
} catch {
    Write-Warning "Could not resolve project root from script location, leaving current location unchanged. Error: $_"
}

New-Item -ItemType Directory -Path (Split-Path $LogFile) -Force | Out-Null
New-Item -ItemType Directory -Path ".agent_state" -Force | Out-Null

# Compute full log file path (relative paths become absolute against current location)
$logFull = Join-Path (Get-Location) $LogFile

# Ensure the directory for the log file exists
$logDir = Split-Path $logFull -Parent
New-Item -ItemType Directory -Path $logDir -Force | Out-Null

if (Test-Path $PidFile) {
    try {
        $existingPid = Get-Content $PidFile -ErrorAction Stop
        if ($existingPid) {
            if (-not $Force) {
                Write-Host "Task loop already running (PID=$existingPid). Use -Force to restart." -ForegroundColor Yellow
                exit 1
            } else {
                Write-Host "Force restarting: stopping PID $existingPid" -ForegroundColor Yellow
                Stop-Process -Id $existingPid -ErrorAction SilentlyContinue
                Remove-Item $PidFile -ErrorAction SilentlyContinue
            }
        }
    } catch {
        # proceed
    }
}

if ($RedisUrl) {
    Write-Host "Starting task loop with REDIS_URL=$RedisUrl" -ForegroundColor Green
    $env:REDIS_URL = $RedisUrl
} else {
    Write-Host "Starting task loop in local-file mode" -ForegroundColor Green
}

 $exe = "uv"
 $args = "run python -m agent_private_i.task_loop"

try {
    # Use cmd.exe to append both stdout and stderr to the same log file (works on PowerShell 5.1)
    $cmdLine = $exe + ' ' + $args + ' >> "' + $logFull + '" 2>&1'
    $proc = Start-Process -FilePath "cmd.exe" -ArgumentList "/c", $cmdLine -WorkingDirectory (Get-Location) -WindowStyle Hidden -PassThru
    $loopPid = $proc.Id
    Set-Content -Path $PidFile -Value $loopPid -Encoding ASCII
    Write-Host "Task loop started (PID=$loopPid). Logs -> $logFull"
} catch {
    Write-Error "Failed to start task loop: $_"
    exit 1
}
