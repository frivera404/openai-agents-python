<#
.SYNOPSIS
  Uninstalls the task-loop Windows service installed by `install-task-loop-service.ps1`.

.DESCRIPTION
  If the service was installed with nssm, this script will attempt to use nssm to remove it. If nssm
  is not available it will use `sc.exe delete` to remove the service and will remove the generated
  batch wrapper if present.

.PARAMETER ServiceName
  Name of the service to remove.

.EXAMPLE
  .\uninstall-task-loop-service.ps1
#>

param(
    [string]$ServiceName = "OpenAIAgentsTaskLoop",
    [string]$NssmPath = ""
)

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
$batchPath = Join-Path $projRoot 'scripts\service-task-loop-runner.bat'

# detect nssm
$nssmExe = $null
if ($NssmPath) { if (Test-Path $NssmPath) { $nssmExe = (Resolve-Path $NssmPath).Path } }
if (-not $nssmExe) { $nssmCmd = Get-Command nssm -ErrorAction SilentlyContinue; if ($nssmCmd) { $nssmExe = $nssmCmd.Source } }

if ($nssmExe) {
    Write-Host "Stopping and removing service via nssm: $ServiceName"
    & $nssmExe stop $ServiceName 2>$null
    & $nssmExe remove $ServiceName confirm
    Write-Host "Removed $ServiceName via nssm"
} else {
    Write-Host "Removing service via sc.exe: $ServiceName"
    sc.exe stop $ServiceName 2>$null | Out-Null
    sc.exe delete $ServiceName | Out-Null
    Write-Host "Service deletion requested via sc.exe: $ServiceName"
    if (Test-Path $batchPath) {
        try { Remove-Item $batchPath -Force; Write-Host "Removed wrapper: $batchPath" } catch { }
    }
}
