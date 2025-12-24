<#
.SYNOPSIS
  Encrypts or decrypts an environment file using Windows DPAPI (ProtectedData).

.DESCRIPTION
  This script provides a simple way to store a project's `.env` securely on disk by encrypting
  its contents to a Base64 file using the Windows Data Protection API (DPAPI). The encrypted
  file is only decryptable by the same user (default) or the same machine when using `-Scope LocalMachine`.

.PARAMETER Action
  `encrypt` or `decrypt`.

.PARAMETER Input
  Input file path (default: .env for encrypt, .env.secure for decrypt).

.PARAMETER Output
  Output file path (default: .env.secure for encrypt, .env for decrypt).

.PARAMETER Scope
  `CurrentUser` (default) or `LocalMachine` determines DPAPI scope.

.EXAMPLE
  # Encrypt .env -> .env.secure (CurrentUser)
  .\secure-env.ps1 -Action encrypt

  # Decrypt .env.secure -> .env
  .\secure-env.ps1 -Action decrypt
#>

param(
  [ValidateSet('encrypt','decrypt')][string]$Action = 'encrypt',
  [string]$Input = '',
  [string]$Output = '',
  [ValidateSet('CurrentUser','LocalMachine')][string]$Scope = 'CurrentUser'
)

function Get-ScopeEnum {
  param([string]$s)
  if ($s -eq 'LocalMachine') { return [System.Security.Cryptography.DataProtectionScope]::LocalMachine }
  return [System.Security.Cryptography.DataProtectionScope]::CurrentUser
}

if ($Action -eq 'encrypt') {
  if (-not $Input -or $Input -eq '') { $Input = '.env' }
  if (-not $Output -or $Output -eq '') { $Output = '.env.secure' }
  if (-not (Test-Path $Input)) { Write-Error "Input file not found: $Input"; exit 2 }

  $plain = Get-Content -Raw -Path $Input
  $bytes = [System.Text.Encoding]::UTF8.GetBytes($plain)
  $scopeEnum = Get-ScopeEnum -s $Scope
  $enc = [System.Security.Cryptography.ProtectedData]::Protect($bytes, $null, $scopeEnum)
  $b64 = [Convert]::ToBase64String($enc)
  Set-Content -Path $Output -Value $b64 -Encoding ASCII
  Write-Host "Encrypted $Input -> $Output (Scope=$Scope)"
  Write-Host "Ensure $Output and .env are protected and/or listed in .gitignore."
  exit 0
}

if ($Action -eq 'decrypt') {
  if (-not $Input -or $Input -eq '') { $Input = '.env.secure' }
  if (-not $Output -or $Output -eq '') { $Output = '.env' }
  if (-not (Test-Path $Input)) { Write-Error "Input file not found: $Input"; exit 2 }

  $b64 = Get-Content -Raw -Path $Input
  try {
    $enc = [Convert]::FromBase64String($b64)
  } catch {
    Write-Error "Invalid encrypted data in $Input"; exit 3
  }
  $scopeEnum = Get-ScopeEnum -s $Scope
  $bytes = [System.Security.Cryptography.ProtectedData]::Unprotect($enc, $null, $scopeEnum)
  $plain = [System.Text.Encoding]::UTF8.GetString($bytes)
  Set-Content -Path $Output -Value $plain -Encoding UTF8
  Write-Host "Decrypted $Input -> $Output"
  exit 0
}

Write-Error "Unknown action: $Action"
exit 1
