# ============================================================================
# Scenario 1: Deploy Azure infrastructure via Bicep
# ============================================================================
# Creates: Resource Group, Log Analytics Workspace, Custom Table, DCE, DCR
#
# Usage:
#   .\infra\deploy_scenario1.ps1
#   .\infra\deploy_scenario1.ps1 -ResourceGroup "my-rg" -Location "westus2"
# ============================================================================

param(
    [string]$ResourceGroup = "mcp-demo-rg",
    [string]$Location = "eastus",
    [string]$BicepFile = "$PSScriptRoot\scenario1.bicep",
    [string]$ParamFile = "$PSScriptRoot\scenario1.bicepparam"
)

$ErrorActionPreference = "Stop"

Write-Host "`n========================================"
Write-Host " Scenario 1: Deploying Azure Infrastructure"
Write-Host "========================================`n"

# Ensure logged in
$account = az account show 2>$null | ConvertFrom-Json
if (-not $account) {
    Write-Host "Not logged in. Running az login..." -ForegroundColor Yellow
    az login --output none
}
Write-Host "Subscription: $($account.name) ($($account.id))" -ForegroundColor Cyan

# Create resource group
Write-Host "`n[1/2] Creating resource group '$ResourceGroup' in '$Location'..."
az group create --name $ResourceGroup --location $Location --output none
Write-Host "  Done." -ForegroundColor Green

# Deploy Bicep
Write-Host "`n[2/2] Deploying Bicep template..."
$deployment = az deployment group create `
    --resource-group $ResourceGroup `
    --template-file $BicepFile `
    --parameters $ParamFile `
    --parameters location=$Location `
    --output json | ConvertFrom-Json

if ($LASTEXITCODE -ne 0) {
    Write-Host "Deployment failed." -ForegroundColor Red
    exit 1
}

# Extract outputs
$outputs = $deployment.properties.outputs
$workspaceId       = $outputs.workspaceId.value
$workspaceName     = $outputs.workspaceName.value
$dceEndpoint       = $outputs.dceEndpoint.value
$dcrImmutableId    = $outputs.dcrImmutableId.value
$dcrId             = $outputs.dcrId.value
$customTableName   = $outputs.customTableName.value

Write-Host "`n========================================"
Write-Host " Deployment Complete"
Write-Host "========================================" -ForegroundColor Green
Write-Host "  Resource Group:    $ResourceGroup"
Write-Host "  Workspace Name:    $workspaceName"
Write-Host "  Workspace ID:      $workspaceId"
Write-Host "  DCE Endpoint:      $dceEndpoint"
Write-Host "  DCR Immutable ID:  $dcrImmutableId"
Write-Host "  Custom Table:      $customTableName"

# Update .env with deployment outputs
$envFile = Join-Path $PSScriptRoot ".." ".env"
if (-not (Test-Path $envFile)) {
    Copy-Item (Join-Path $PSScriptRoot ".." ".env.example") $envFile
}

# Helper to set or update a key in .env
function Set-EnvValue([string]$File, [string]$Key, [string]$Value) {
    $content = Get-Content $File -Raw
    if ($content -match "(?m)^$Key=.*$") {
        $content = $content -replace "(?m)^$Key=.*$", "$Key=$Value"
    } else {
        $content += "`n$Key=$Value"
    }
    Set-Content $File $content -NoNewline
}

$subId = $account.id
Set-EnvValue $envFile "AZURE_SUBSCRIPTION_ID" $subId
Set-EnvValue $envFile "AZURE_RESOURCE_GROUP" $ResourceGroup
Set-EnvValue $envFile "LOG_ANALYTICS_WORKSPACE_ID" $workspaceId
Set-EnvValue $envFile "DCE_ENDPOINT" $dceEndpoint
Set-EnvValue $envFile "DCR_IMMUTABLE_ID" $dcrImmutableId
Set-EnvValue $envFile "DCR_ID" $dcrId

Write-Host "`n.env updated with deployment values." -ForegroundColor Green

# Assign Metrics Publisher role so the inject script can write logs
Write-Host "`nAssigning 'Monitoring Metrics Publisher' role to your identity..."
$userId = az ad signed-in-user show --query id -o tsv
az role assignment create `
    --assignee $userId `
    --role "Monitoring Metrics Publisher" `
    --scope $dcrId `
    --output none 2>$null
Write-Host "  Done." -ForegroundColor Green

Write-Host "`n Next step: inject sample logs"
Write-Host "  .\infra\inject_scenario1_logs.ps1`n"
