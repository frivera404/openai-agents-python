param(
    [string]$PidFile = ".agent_state\task_loop.pid"
)

if (-not (Test-Path $PidFile)) {
    Write-Host "No PID file found at $PidFile. Is the task loop running?" -ForegroundColor Yellow
    exit 0
}

try {
    $loopPid = Get-Content $PidFile | Select-Object -First 1
    if ($loopPid) {
        Write-Host "Stopping task loop PID $loopPid" -ForegroundColor Green
        Stop-Process -Id $loopPid -ErrorAction SilentlyContinue
    }
} catch {
    Write-Warning "Error stopping process: $_"
}

try {
    Remove-Item $PidFile -ErrorAction SilentlyContinue
} catch {
    # ignore
}

Write-Host "Stopped (if running)." -ForegroundColor Green
