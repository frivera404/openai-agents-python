# ============================================================
# set-stripe-key.ps1 — Set STRIPE_SECRET_KEY on bristoltalks-site worker
# Run from C:\Users\frive\Downloads\files
# Usage: .\set-stripe-key.ps1
# ============================================================

Write-Host ""
Write-Host "=== Set STRIPE_SECRET_KEY on bristoltalks-site ===" -ForegroundColor Yellow
Write-Host ""
Write-Host "  Paste your Stripe Secret Key when prompted." -ForegroundColor White
Write-Host "  (Live key starts with 'sk_live_...' | Test key starts with 'sk_test_...')" -ForegroundColor Gray
Write-Host ""

$rawKey = Read-Host "  STRIPE_SECRET_KEY"
$cleanKey = $rawKey.Trim()

if (-not ($cleanKey.StartsWith("sk_live_") -or $cleanKey.StartsWith("sk_test_"))) {
    Write-Host ""
    Write-Host "  WARNING: Key doesn't look like a Stripe key (expected sk_live_ or sk_test_)" -ForegroundColor Yellow
    Write-Host "  Proceeding anyway. Verify in Stripe dashboard if payments fail." -ForegroundColor Yellow
}

# Read OAuth token from wrangler config
$wranglerConfig = "$env:USERPROFILE\.wrangler\config\default.toml"
$cfToken = ""
if (Test-Path $wranglerConfig) {
    $cfToken = [regex]::Match((Get-Content $wranglerConfig -Raw), 'oauth_token\s*=\s*"([^"]+)"').Groups[1].Value
}
if (-not $cfToken) {
    Write-Host ""
    Write-Host "  ERROR: Could not read Cloudflare token from wrangler config." -ForegroundColor Red
    Write-Host "  Run 'wrangler login' first, then retry this script." -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "  Setting secret via Cloudflare REST API..." -ForegroundColor Cyan

$secretBody = @{ name = "STRIPE_SECRET_KEY"; text = $cleanKey; type = "secret_text" } | ConvertTo-Json -Compress
$secretFile = "$env:TEMP\stripe_secret_$([System.Guid]::NewGuid().ToString('N')).json"
[System.IO.File]::WriteAllText($secretFile, $secretBody, (New-Object System.Text.UTF8Encoding $false))

$apiResult = curl.exe -s -X PUT `
    "https://api.cloudflare.com/client/v4/accounts/8cdcf88f537f86831975b2dc03cc617a/workers/scripts/bristoltalks-site/secrets" `
    -H "Authorization: Bearer $cfToken" `
    -H "Content-Type: application/json" `
    --data-binary "@$secretFile"

Remove-Item $secretFile -Force -ErrorAction SilentlyContinue

$apiJson = $apiResult | ConvertFrom-Json
if ($apiJson.success) {
    Write-Host "  STRIPE_SECRET_KEY set successfully." -ForegroundColor Green
    Write-Host ""
    Write-Host "  Next: Create a Stripe Payment Link in your Stripe dashboard" -ForegroundColor Yellow
    Write-Host "  Stripe Dashboard > Payment Links > Create new link" -ForegroundColor Gray
    Write-Host "  Product: 'BristolBot AI Chat' | Price: \$97/month recurring" -ForegroundColor Gray
} else {
    Write-Host "  ERROR setting secret: $($apiJson.errors | ConvertTo-Json)" -ForegroundColor Red
    exit 1
}

Write-Host ""
