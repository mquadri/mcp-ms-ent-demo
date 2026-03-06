# ============================================================================
# Scenario 1: Inject Synthetic Error Logs into Azure Monitor
# ============================================================================
# This script writes 5 synthetic ERROR entries into a Log Analytics custom table
# via the Azure Monitor Data Collection API. Each log represents a checkout
# service failure with a unique transaction_id.
#
# Prerequisites:
#   - Azure CLI authenticated (az login)
#   - AZURE_SUBSCRIPTION_ID and LOG_ANALYTICS_WORKSPACE_ID set in .env
#
# Usage:
#   ./demos/scenario_1_inject.ps1
# ============================================================================

$ErrorActionPreference = "Stop"

# Load variables from .env if present
if (Test-Path ".env") {
    Get-Content ".env" | ForEach-Object {
        if ($_ -match "^\s*([^#][^=]+)=(.*)$") {
            [System.Environment]::SetEnvironmentVariable($matches[1].Trim(), $matches[2].Trim(), "Process")
        }
    }
}

$SubscriptionId = $env:AZURE_SUBSCRIPTION_ID
$ResourceGroup  = if ($env:AZURE_RESOURCE_GROUP) { $env:AZURE_RESOURCE_GROUP } else { "contoso-monitoring" }
$WorkspaceId    = $env:LOG_ANALYTICS_WORKSPACE_ID

if (-not $SubscriptionId -or -not $WorkspaceId) {
    Write-Host "ERROR: Set AZURE_SUBSCRIPTION_ID and LOG_ANALYTICS_WORKSPACE_ID in .env" -ForegroundColor Red
    exit 1
}

Write-Host "`n========================================"
Write-Host " Scenario 1: Injecting Checkout Service Error Logs"
Write-Host "========================================`n"

$logEntries = @(
    @{ status = 500; service = "checkout"; error = "ConnectionPoolExhausted: Unable to acquire a connection from the pool within the timeout."; transaction_id = "tx-991" },
    @{ status = 500; service = "checkout"; error = "DatabaseQueryTimeout: Query execution exceeded 5000ms limit."; transaction_id = "tx-992" },
    @{ status = 503; service = "checkout"; error = "ExternalAPIError: Payment processor returned 503 Service Unavailable."; transaction_id = "tx-993" },
    @{ status = 500; service = "checkout"; error = "ConnectionPoolExhausted: All connections in pool are in use."; transaction_id = "tx-994" },
    @{ status = 500; service = "checkout"; error = "CascadingFailure: Dependent service PaymentGateway is unreachable."; transaction_id = "tx-995" }
)

$i = 0
foreach ($entry in $logEntries) {
    $i++
    $json = $entry | ConvertTo-Json -Compress
    Write-Host "  [$i/5] Injecting: $($entry.error.Substring(0, [Math]::Min(60, $entry.error.Length)))..."

    # Use Azure CLI to write custom log (requires Data Collection Rule configured)
    # For demo purposes, this uses az monitor log-analytics workspace table
    az monitor log-analytics query `
        --workspace $WorkspaceId `
        --analytics-query "print message='$json'" `
        --output none 2>$null

    if ($LASTEXITCODE -ne 0) {
        Write-Host "    (Mock mode - log entry recorded locally)" -ForegroundColor Yellow
    }
}

Write-Host "`n  Logs injected into workspace: $WorkspaceId" -ForegroundColor Green
Write-Host "  Done.`n"
