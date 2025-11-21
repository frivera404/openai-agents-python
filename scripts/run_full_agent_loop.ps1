$proj = "C:\Users\frive\MCP Servers\client\openai-agents-python-main"
Set-Location $proj

$file = Join-Path $proj 'server.ts'
$lines = Get-Content $file

$startLineObj = $lines | Select-String -Pattern 'const agentInstructions' -SimpleMatch | Select-Object -First 1
$endLineObj = $lines | Select-String -Pattern 'const agentAssistantIds' -SimpleMatch | Select-Object -First 1
if (-not $startLineObj -or -not $endLineObj) {
    Write-Error "Could not locate agentInstructions or agentAssistantIds in server.ts"
    exit 1
}
$start = $startLineObj.LineNumber
$end = $endLineObj.LineNumber

# Extract the block lines containing the instructions mapping
$block = $lines[$start..($end - 2)]

$agentIds = @()
foreach ($line in $block) {
    if ($line -match "'([a-z0-9-]+)'\s*:") {
        $agentIds += $matches[1]
    }
}

if ($agentIds.Count -eq 0) {
    Write-Error "No agent IDs found in agentInstructions block"
    exit 1
}

$results = @()

foreach ($id in $agentIds) {
    Write-Output "Launching agent: $id"
    try {
        $body = @{ agentId = $id; prompt = "sanity check"; model = "gpt-4.1"; temperature = 0.9 } | ConvertTo-Json -Depth 5
        $resp = Invoke-RestMethod -Method Post -Uri 'http://localhost:3001/api/agent/launch' -Body $body -ContentType 'application/json' -TimeoutSec 120
        $results += @{ endedAt = (Get-Date).ToString('o'); startedAt = (Get-Date).AddSeconds(-1).ToString('o'); agentId = $id; success = $true; response = $resp }
    } catch {
        $errMsg = $_.Exception.Message
        Write-Warning "Agent $id failed: $errMsg"
        $results += @{ endedAt = (Get-Date).ToString('o'); startedAt = (Get-Date).AddSeconds(-1).ToString('o'); agentId = $id; success = $false; error = $errMsg }
    }
}

$results | ConvertTo-Json -Depth 10 | Out-File -FilePath (Join-Path $proj 'agent_launch_results.json') -Encoding utf8
Write-Output "Saved results to agent_launch_results.json"
