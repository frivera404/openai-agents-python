<#
.SYNOPSIS
  Installs the task-loop as a Windows service using nssm if available, otherwise falls back to creating
  a service that runs a cmd wrapper around the Python module.

.DESCRIPTION
  This script installs the `OpenAIAgentsTaskLoop` service by default. It prefers `nssm.exe` when available
  (in PATH or when passed with -NssmPath). If nssm is not found it will create a small batch runner in
  `scripts\service-task-loop-runner.bat` and register a service with `sc.exe` that invokes `cmd.exe /c`.

.PARAMETER ServiceName
  Name for the Windows service.

.PARAMETER DisplayName
  Friendly name shown in Services.msc.

.PARAMETER Description
  Service description.

.PARAMETER NssmPath
  Optional explicit path to nssm.exe.

.PARAMETER PythonExe
  Optional path to the Python executable to use. If empty the script will try to locate `python`.

.EXAMPLE
  .\install-task-loop-service.ps1 -NssmPath C:\tools\nssm.exe
#>

param(
    [string]$ServiceName = "OpenAIAgentsTaskLoop",
    [string]$DisplayName = "OpenAI Agents Task Loop",
    [string]$Description = "Runs the agent task loop (agent_private_i)",
    [string]$NssmPath = "",
    [string]$PythonExe = "",
    [ValidateSet('auto','demand','disabled')][string]$StartType = 'auto'
)

# Ensure script is running as Administrator; if not, re-launch elevated with same parameters.
function Ensure-Elevated {
  $isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
  if (-not $isAdmin) {
    Write-Host "Script not running as Administrator. Relaunching elevated..." -ForegroundColor Yellow
    $scriptPath = $MyInvocation.MyCommand.Definition
    $argList = @('-NoProfile','-ExecutionPolicy','Bypass','-File',$scriptPath)
    if ($PSBoundParameters.Count -gt 0) {
      foreach ($kv in $PSBoundParameters.GetEnumerator()) {
        $argList += ('-' + $kv.Key)
        $argList += ($kv.Value.ToString())
      }
    }
    Start-Process -FilePath powershell.exe -ArgumentList $argList -Verb RunAs -Wait
    Exit
  }
}

Ensure-Elevated

function Resolve-ProjectRoot {
  if ($PSScriptRoot -and $PSScriptRoot -ne '') {
    $scriptDir = $PSScriptRoot
  } elseif ($PSCommandPath -and $PSCommandPath -ne '') {
    $scriptDir = Split-Path -Parent $PSCommandPath
  } else {
    $scriptDir = (Get-Location).Path
  }
  $projRoot = [IO.Path]::GetFullPath((Join-Path $scriptDir '..'))
  return $projRoot
}

$projRoot = Resolve-ProjectRoot
$logDir = Join-Path $projRoot 'scripts\logs'
if (-not (Test-Path $logDir)) { New-Item -ItemType Directory -Path $logDir | Out-Null }
$logPath = Join-Path $logDir 'task-loop.log'

if (-not $PythonExe) {
    $pythonCmd = (Get-Command python -ErrorAction SilentlyContinue).Source
    if (-not $pythonCmd) { $pythonCmd = (Get-Command py -ErrorAction SilentlyContinue).Source }
    if (-not $pythonCmd) { throw "Python executable not found. Pass -PythonExe explicitly." }
} else { $pythonCmd = $PythonExe }

# check for nssm
$nssmExe = $null
if ($NssmPath) {
    if (Test-Path $NssmPath) { $nssmExe = (Resolve-Path $NssmPath).Path }
}
if (-not $nssmExe) {
    $nssmCmd = Get-Command nssm -ErrorAction SilentlyContinue
    if ($nssmCmd) { $nssmExe = $nssmCmd.Source }
}

Write-Host "Project root: $projRoot"
Write-Host "Python: $pythonCmd"
Write-Host "Log: $logPath"

if ($nssmExe) {
    Write-Host "Using nssm at: $nssmExe"
    & $nssmExe install $ServiceName $pythonCmd -m agent_private_i.task_loop
    & $nssmExe set $ServiceName AppDirectory $projRoot
    & $nssmExe set $ServiceName AppStdout $logPath
    & $nssmExe set $ServiceName AppStderr $logPath
    & $nssmExe set $ServiceName AppRotate 1
    & $nssmExe set $ServiceName AppRestartDelay 5000
    & $nssmExe start $ServiceName
    Write-Host "Service installed and started via nssm: $ServiceName"
} else {
    Write-Host "nssm not found; falling back to sc.exe + batch wrapper."
    $batchPath = Join-Path $projRoot 'scripts\service-task-loop-runner.bat'
    $batchContent = @"
@echo off
cd /d "$projRoot"
"$pythonCmd" -m agent_private_i.task_loop >> "$logPath" 2>&1
"@
    if (-not (Test-Path $batchPath)) {
        Set-Content -Path $batchPath -Value $batchContent -Encoding ASCII
    }

    $cmdExe = Join-Path $env:windir 'System32\cmd.exe'
    # build a properly quoted binPath for sc.exe: "C:\Windows\System32\cmd.exe" /c "C:\path\to\script.bat"
    $binPath = '"' + $cmdExe + '" /c "' + $batchPath + '"'

    Write-Host "Creating service $ServiceName via sc.exe (binPath= $binPath)"

    # Use argument array to avoid PowerShell tokenization surprises and capture output for diagnostics.
    $createArgs = @('create', $ServiceName, 'binPath=', $binPath, 'DisplayName=', $DisplayName, 'start=', $StartType)
    $createOut = & sc.exe @createArgs 2>&1
    $createCode = $LASTEXITCODE
    if ($createCode -ne 0) {
      Write-Error "sc.exe create failed (exit=$createCode). Output:`n$($createOut -join "`n")"
      Write-Host "Full command used: sc.exe $($createArgs -join ' ')"
      Write-Host "Check Event Viewer (Windows Logs → System) for service start errors and verify the service binary path is valid."
      exit $createCode
    }

    # set description (capture output for debugging)
    $descOut = & sc.exe description $ServiceName $Description 2>&1
    $descCode = $LASTEXITCODE
    if ($descCode -ne 0) { Write-Warning "Failed to set service description: $($descOut -join '`n')" }

    Start-Sleep -Seconds 1
    $startOut = & sc.exe start $ServiceName 2>&1
    $startCode = $LASTEXITCODE
    if ($startCode -ne 0) {
      Write-Warning "sc.exe start returned exit=$startCode. Output:`n$($startOut -join "`n")"
      Write-Host "If the service fails to remain running, check:"
      Write-Host " - The created batch wrapper: $batchPath"
      Write-Host " - That the Python executable path ($pythonCmd) is accessible to the service account"
      Write-Host " - Windows Event Viewer → Windows Logs → System for Service Control Manager errors"
    } else {
      Write-Host "Service created and start attempted via sc.exe: $ServiceName"
      Write-Host "Logs: $logPath"
    }
    # Always print a service query snapshot for diagnostics
    Start-Sleep -Milliseconds 250
    $queryOut = & sc.exe query $ServiceName 2>&1
    Write-Host "sc.exe query output:`n$($queryOut -join "`n")"
}
