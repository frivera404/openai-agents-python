param(
  [string]$ProjectRoot = $PSScriptRoot + '\..'
)

# Resolve absolute project root
$projRoot = (Resolve-Path $ProjectRoot).Path
$envFile = Join-Path $projRoot '.env'

if (Test-Path $envFile) {
  Write-Output "Loading env from $envFile"
  Get-Content $envFile | ForEach-Object {
    if ($_ -match '^\s*$' -or $_ -match '^\s*#') { return }
    $parts = $_ -split '=',2
    if ($parts.Count -ge 2) {
      $name = $parts[0].Trim()
      $value = $parts[1]
      [System.Environment]::SetEnvironmentVariable($name, $value, 'Process')
      Write-Output "  Loaded $name"
    }
  }
} else {
  Write-Output "No .env file found at $envFile"
}

$serverPath = Join-Path $projRoot 'dist\server.cjs'
Write-Output "Starting server: $serverPath"
if (-not (Test-Path $serverPath)) {
  Write-Error "Server file not found: $serverPath"
  exit 1
}

# Start node in this foreground process so logs appear here
& node $serverPath

# Ensure LOGO_PATH is available in process env for UI consumption.
# If not present in .env, use the provided default path (if any).
try {
  $logo = [System.Environment]::GetEnvironmentVariable('LOGO_PATH', 'Process')
  if (-not $logo -or $logo -eq '') {
    # Default provided path (from user). Update here if you want to change.
    $defaultLogo = 'C:\Users\frive\OneDrive\Desktop\.Logo\966c7f12-08bd-46d0-afd9-fce03cd3b8b6.webp'
    if (Test-Path $defaultLogo) {
      [System.Environment]::SetEnvironmentVariable('LOGO_PATH', $defaultLogo, 'Process')
      Write-Output "LOGO_PATH set to default: $defaultLogo"
    } else {
      Write-Output "LOGO_PATH not set and default logo not found: $defaultLogo"
    }
  } else {
    Write-Output "LOGO_PATH already set: $logo"
  }
} catch {
  Write-Output "Failed to set LOGO_PATH: $($_.Exception.Message)"
}
