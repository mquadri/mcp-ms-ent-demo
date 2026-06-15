# ============================================================================
# Scenario 1: Inject synthetic error logs via DCR Logs Ingestion API
# ============================================================================
# Sends 5 checkout-service error entries to the CheckoutErrors_CL custom table
# using the Data Collection Rule ingestion endpoint deployed by the Bicep template.
#
# Prerequisites:
#   - Run infra\deploy_scenario1.ps1 first (sets .env values)
#   - az login (your identity needs 'Monitoring Metrics Publisher' on the DCR)
#
# Usage:
#   .\infra\inject_scenario1_logs.ps1
# ============================================================================

$ErrorActionPreference = "Stop"

# Load .env
$envFile = Join-Path $PSScriptRoot ".." ".env"
if (Test-Path $envFile) {
    Get-Content $envFile | ForEach-Object {
        if ($_ -match "^\s*([^#][^=]+)=(.*)$") {
            [System.Environment]::SetEnvironmentVariable($matches[1].Trim(), $matches[2].Trim(), "Process")
        }
    }
}

$DceEndpoint    = $env:DCE_ENDPOINT
$DcrImmutableId = $env:DCR_IMMUTABLE_ID
$CustomTable    = "Custom-CheckoutErrors_CL"

if (-not $DceEndpoint -or -not $DcrImmutableId) {
    Write-Host "ERROR: DCE_ENDPOINT and DCR_IMMUTABLE_ID not set." -ForegroundColor Red
    Write-Host "  Run .\infra\deploy_scenario1.ps1 first." -ForegroundColor Yellow
    exit 1
}

Write-Host "`n========================================"
Write-Host " Scenario 1: Injecting Checkout Service Error Logs"
Write-Host "========================================`n"

# Get an AAD token for the ingestion endpoint
Write-Host "Acquiring Azure AD token..."
$token = az account get-access-token --resource "https://monitor.azure.com/" --query accessToken -o tsv
if ($LASTEXITCODE -ne 0 -or -not $token) {
    Write-Host "ERROR: Could not acquire token. Run 'az login' first." -ForegroundColor Red
    exit 1
}

$now = [datetime]::UtcNow

$logEntries = @(
    @{
        TimeGenerated  = ($now.AddMinutes(-15)).ToString("o")
        status         = 500
        service        = "CheckoutService"
        error          = "ConnectionPoolExhausted: Unable to acquire a connection from the pool within the timeout."
        transaction_id = "tx-991"
        severity       = "Critical"
        stack_trace    = "at CheckoutService.ProcessOrder (line 234)`n  at DbConnectionPool.Acquire (line 89)`n  at SqlClient.ExecuteQuery (line 156)"
    },
    @{
        TimeGenerated  = ($now.AddMinutes(-14)).ToString("o")
        status         = 500
        service        = "CheckoutService"
        error          = "DatabaseQueryTimeout: Query execution exceeded 5000ms limit."
        transaction_id = "tx-992"
        severity       = "Critical"
        stack_trace    = "at CheckoutService.ProcessOrder (line 234)`n  at SqlClient.ExecuteQuery (line 156)"
    },
    @{
        TimeGenerated  = ($now.AddMinutes(-12)).ToString("o")
        status         = 503
        service        = "PaymentGateway"
        error          = "ExternalAPIError: Payment processor returned 503 Service Unavailable."
        transaction_id = "tx-993"
        severity       = "Critical"
        stack_trace    = "at PaymentGateway.Execute (line 78)`n  at StripeClient.Charge (line 44)"
    },
    @{
        TimeGenerated  = ($now.AddMinutes(-10)).ToString("o")
        status         = 500
        service        = "CheckoutService"
        error          = "ConnectionPoolExhausted: All connections in pool are in use."
        transaction_id = "tx-994"
        severity       = "Error"
        stack_trace    = "at CheckoutService.ProcessOrder (line 234)`n  at DbConnectionPool.Acquire (line 89)"
    },
    @{
        TimeGenerated  = ($now.AddMinutes(-8)).ToString("o")
        status         = 500
        service        = "CheckoutService"
        error          = "CascadingFailure: Dependent service PaymentGateway is unreachable."
        transaction_id = "tx-995"
        severity       = "Error"
        stack_trace    = "at CheckoutService.ProcessOrder (line 234)`n  at PaymentGateway.HealthCheck (line 12)"
    }
)

$body = $logEntries | ConvertTo-Json -AsArray -Depth 5
$uri  = "$DceEndpoint/dataCollectionRules/$DcrImmutableId/streams/${CustomTable}?api-version=2023-01-01"

$headers = @{
    "Authorization" = "Bearer $token"
    "Content-Type"  = "application/json"
}

$i = 0
foreach ($entry in $logEntries) {
    $i++
    $shortErr = $entry.error.Substring(0, [Math]::Min(60, $entry.error.Length))
    Write-Host "  [$i/5] $shortErr..."
}

Write-Host "`nSending batch to DCR ingestion endpoint..."
try {
    Invoke-RestMethod -Uri $uri -Method Post -Headers $headers -Body $body
    Write-Host "`n  All 5 logs ingested successfully." -ForegroundColor Green
} catch {
    $status = $_.Exception.Response.StatusCode.value__
    $detail = $_.ErrorDetails.Message
    Write-Host "`n  Ingestion failed (HTTP $status): $detail" -ForegroundColor Red
    exit 1
}

Write-Host "`nLogs will appear in Log Analytics within ~5 minutes."
Write-Host "Query: CheckoutErrors_CL | order by TimeGenerated desc | take 10"
Write-Host "Done.`n"
