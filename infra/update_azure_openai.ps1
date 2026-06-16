# ============================================================================
# Update Container Apps with New Azure OpenAI Settings
# ============================================================================
# This script updates the agent container apps with Azure OpenAI settings read
# from a local .env file. The API key is stored as a Container Apps secret and
# referenced from the AZURE_OPENAI_API_KEY environment variable.
#
# Usage:
#   .\infra\update_azure_openai.ps1 `
#     -ResourceGroup "<resource-group>" `
#     -AgentsAppName "<agents-app-name>" `
#     -AgentsMcpAppName "<agents-mcp-app-name>" `
#     -AgentsAppUrl "https://<agents-app-fqdn>"
# ============================================================================

param(
    [Parameter(Mandatory = $true)]
    [string]$ResourceGroup,

    [Parameter(Mandatory = $true)]
    [string]$AgentsAppName,

    [Parameter(Mandatory = $true)]
    [string]$AgentsMcpAppName,

    [Parameter(Mandatory = $true)]
    [string]$AgentsAppUrl,

    [string]$EnvFile = "$PSScriptRoot\..\\.env"
)

$ErrorActionPreference = "Stop"

Write-Host "`n========================================"
Write-Host " Updating Container Apps with New Azure OpenAI"
Write-Host "========================================`n"

# Ensure logged in
$account = az account show 2>$null | ConvertFrom-Json
if (-not $account) {
    Write-Host "Not logged in. Running az login..." -ForegroundColor Yellow
    az login --output none
}
Write-Host "Subscription: $($account.name) ($($account.id))" -ForegroundColor Cyan

# Load .env file
Write-Host "`n[1/4] Loading environment variables from .env..."
if (-not (Test-Path $EnvFile)) {
    Write-Host "ERROR: .env file not found at $EnvFile" -ForegroundColor Red
    exit 1
}

$envVars = @{}
Get-Content $EnvFile | Where-Object { $_ -match '^\s*AZURE_OPENAI' } | ForEach-Object {
    $line = $_.Trim()
    if ($line -and -not $line.StartsWith("#")) {
        $parts = $line -split "=", 2
        if ($parts.Count -eq 2) {
            $envVars[$parts[0]] = $parts[1]
        }
    }
}

$endpoint = $envVars["AZURE_OPENAI_ENDPOINT"]
$deployment = $envVars["AZURE_OPENAI_DEPLOYMENT"]
$apiKey = $envVars["AZURE_OPENAI_API_KEY"]

if (-not $endpoint -or -not $deployment -or -not $apiKey) {
    Write-Host "ERROR: Missing Azure OpenAI credentials in .env" -ForegroundColor Red
    exit 1
}

Write-Host "  AZURE_OPENAI_ENDPOINT: $endpoint" -ForegroundColor Cyan
Write-Host "  AZURE_OPENAI_DEPLOYMENT: $deployment" -ForegroundColor Cyan
Write-Host "  AZURE_OPENAI_API_KEY: <loaded from local .env; not displayed>" -ForegroundColor Cyan
Write-Host "  Done." -ForegroundColor Green

# Update agents container app
Write-Host "`n[2/4] Updating '$AgentsAppName' container app environment variables..."

try {
    az containerapp secret set `
        --name $AgentsAppName `
        --resource-group $ResourceGroup `
        --secrets azure-openai-api-key=$apiKey `
        --output none

    az containerapp update `
        --name $AgentsAppName `
        --resource-group $ResourceGroup `
        --set-env-vars `
            AZURE_OPENAI_ENDPOINT=$endpoint `
            AZURE_OPENAI_DEPLOYMENT=$deployment `
            AZURE_OPENAI_API_KEY=secretref:azure-openai-api-key `
        --output none
    Write-Host "  Done." -ForegroundColor Green
} catch {
    Write-Host "  ERROR: $_" -ForegroundColor Red
    exit 1
}

# Update agents-mcp container app (if it also uses Azure OpenAI)
Write-Host "`n[3/4] Updating '$AgentsMcpAppName' container app environment variables..."
try {
    az containerapp secret set `
        --name $AgentsMcpAppName `
        --resource-group $ResourceGroup `
        --secrets azure-openai-api-key=$apiKey `
        --output none

    az containerapp update `
        --name $AgentsMcpAppName `
        --resource-group $ResourceGroup `
        --set-env-vars `
            AZURE_OPENAI_ENDPOINT=$endpoint `
            AZURE_OPENAI_DEPLOYMENT=$deployment `
            AZURE_OPENAI_API_KEY=secretref:azure-openai-api-key `
        --output none
    Write-Host "  Done." -ForegroundColor Green
} catch {
    Write-Host "  WARNING: $AgentsMcpAppName update failed (may not require these vars): $_" -ForegroundColor Yellow
}

# Wait for changes to take effect
Write-Host "`n[4/4] Waiting for container apps to redeploy with new settings (30 seconds)..."
Start-Sleep -Seconds 30

Write-Host "`nDeployment complete!" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "1. Test the /health endpoint:"
Write-Host "   Invoke-WebRequest -Uri '$AgentsAppUrl/health' -Method Get"
Write-Host ""
Write-Host "2. Test the /chat endpoint with a simple query:"
Write-Host "`$body = @{ query = 'health check: reply with one short sentence' } | ConvertTo-Json"
Write-Host "Invoke-RestMethod -Uri '$AgentsAppUrl/chat' -Method Post -ContentType 'application/json' -Body `$body -TimeoutSec 90"
Write-Host ""
Write-Host "3. In VS Code Agent mode, test demo-agents-mcp-ask_agent with a simple query"
Write-Host ""
