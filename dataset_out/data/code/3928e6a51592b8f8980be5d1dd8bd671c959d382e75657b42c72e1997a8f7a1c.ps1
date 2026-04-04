<#
.SYNOPSIS
  Show status for the task-loop service, PID/process info, and tail the task-loop log.

.DESCRIPTION
  Prints `Get-Service` output for the task loop service, queries the service via `sc.exe`, shows
  the PID recorded in `.agent_state\task_loop.pid` and associated process info, and prints the
  last 200 lines of the task-loop log (if present).
#>

param(
    [string]$ServiceName = 'OpenAIAgentsTaskLoop',
    [int]$TailLines = 200
)

# Resolve project root (parent of the scripts folder)
if ($PSScriptRoot -and $PSScriptRoot -ne '') { $scriptDir = $PSScriptRoot } elseif ($PSCommandPath) { $scriptDir = Split-Path -Parent $PSCommandPath } else { $scriptDir = (Get-Location).Path }
$projRoot = [IO.Path]::GetFullPath((Join-Path $scriptDir '..'))

Write-Host "Service: $ServiceName`nProject root: $projRoot`n" -ForegroundColor Cyan

# Service status
Write-Host '--- Service Status (Get-Service) ---' -ForegroundColor Green
try {
    $svc = Get-Service -Name $ServiceName -ErrorAction Stop
    $svc | Format-List *
} catch {
    Write-Warning "Service '$ServiceName' not found via Get-Service."
}

Write-Host '--- Service Control (sc.exe query) ---' -ForegroundColor Green
try {
    sc.exe query $ServiceName
} catch {
    Write-Warning "sc.exe query failed for $ServiceName"
}

# PID file and process info
$pidFile = Join-Path $projRoot '.agent_state\task_loop.pid'
Write-Host "`n--- PID File ---" -ForegroundColor Green
if (Test-Path $pidFile) {
    try {
        $loopPid = (Get-Content $pidFile -ErrorAction Stop).Trim()
        Write-Host "PID file: $pidFile -> $loopPid"
        $proc = Get-Process -Id $loopPid -ErrorAction SilentlyContinue
        if ($proc) {
            Write-Host "Process info:" -ForegroundColor Yellow
            $proc | Select-Object Id, ProcessName, StartTime, CPU, Threads | Format-List
        } else {
            Write-Warning "No running process found with PID $loopPid"
        }
    } catch {
        Write-Warning "Failed to read PID file: $_"
    }
} else {
    Write-Host "PID file not found: $pidFile" -ForegroundColor Yellow
}

# Tail log
$logPath = Join-Path $projRoot 'scripts\logs\task-loop.log'
Write-Host "`n--- Tail log: $logPath (last $TailLines lines) ---" -ForegroundColor Green
if (Test-Path $logPath) {
    try {
        Get-Content -Path $logPath -Tail $TailLines
    } catch {
        Write-Warning "Failed to read log file: $_"
    }
} else {
    Write-Host "Log file not found: $logPath" -ForegroundColor Yellow
}

Write-Host "`nIf the service isn't running, run the installer or start scripts as Administrator." -ForegroundColor Cyan
