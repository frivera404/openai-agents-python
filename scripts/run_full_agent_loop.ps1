$proj = "C:\Users\frive\MCP Servers\client\openai-agents-python-main"
Set-Location $proj

$serverUrl = 'http://localhost:3001'
$healthEndpoint = "$serverUrl/api/health"
$serverProcess = $null
$serverStartedByScript = $false

function Test-ServerAvailable {
    param (
        [string]$Url
    )

    try {
        Invoke-RestMethod -Method Get -Uri $Url -TimeoutSec 3 | Out-Null
        return $true
    } catch {
        return $false
    }
}

function Start-BackendServer {
    param (
        [string]$WorkingDirectory
    )

    Write-Host "Backend server not detected. Starting npm run dev:server..."
    $process = Start-Process -FilePath "npm.cmd" -ArgumentList "run", "dev:server" -WorkingDirectory $WorkingDirectory -WindowStyle Hidden -PassThru
    return $process
}

try {
    if (-not (Test-ServerAvailable -Url $healthEndpoint)) {
        $serverProcess = Start-BackendServer -WorkingDirectory $proj
        $serverStartedByScript = $true

        $maxAttempts = 30
        $serverReady = $false
        for ($attempt = 1; $attempt -le $maxAttempts; $attempt++) {
            Start-Sleep -Seconds 1
            if (Test-ServerAvailable -Url $healthEndpoint) {
                $serverReady = $true
                Write-Output "Backend server is ready."
                break
            }
        }

        if (-not $serverReady) {
            throw "Backend server failed to start within $maxAttempts seconds."
        }
    } else {
        Write-Output "Backend server already running."
    }

    $file = Join-Path $proj 'server.ts'
    $lines = Get-Content $file

    $startLineObj = $lines | Select-String -Pattern 'const agentInstructions' -SimpleMatch | Select-Object -First 1
    $endLineObj = $lines | Select-String -Pattern 'const agentAssistantIds' -SimpleMatch | Select-Object -First 1
    if (-not $startLineObj -or -not $endLineObj) {
        throw "Could not locate agentInstructions or agentAssistantIds in server.ts"
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
        throw "No agent IDs found in agentInstructions block"
    }

    $results = @()

    foreach ($id in $agentIds) {
        Write-Output "Launching agent: $id"
        $startTimestamp = Get-Date
        try {
            $body = @{ agentId = $id; prompt = "sanity check"; model = "gpt-4.1"; temperature = 0.9 } | ConvertTo-Json -Depth 5
            $resp = Invoke-RestMethod -Method Post -Uri "$serverUrl/api/agent/launch" -Body $body -ContentType 'application/json' -TimeoutSec 120
            $results += @{ endedAt = (Get-Date).ToString('o'); startedAt = $startTimestamp.ToString('o'); agentId = $id; success = $true; response = $resp }
        } catch {
            $errMsg = $_.Exception.Message
            Write-Warning "Agent $id failed: $errMsg"
            $results += @{ endedAt = (Get-Date).ToString('o'); startedAt = $startTimestamp.ToString('o'); agentId = $id; success = $false; error = $errMsg }
        }
    }

    $results | ConvertTo-Json -Depth 10 | Out-File -FilePath (Join-Path $proj 'agent_launch_results.json') -Encoding utf8
    Write-Output "Saved results to agent_launch_results.json"
} finally {
    if ($serverStartedByScript -and $serverProcess -and -not $serverProcess.HasExited) {
        Write-Output "Stopping backend server..."
        try {
            Stop-Process -Id $serverProcess.Id -Force
        } catch {
            Write-Warning "Failed to stop backend server process: $($_.Exception.Message)"
        }
    }
}
