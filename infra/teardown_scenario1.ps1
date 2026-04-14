# ============================================================================
# Scenario 1: Tear down Azure infrastructure
# ============================================================================
# Deletes the entire resource group and all resources within it.
#
# Usage:
#   .\infra\teardown_scenario1.ps1
#   .\infra\teardown_scenario1.ps1 -ResourceGroup "my-rg"
# ============================================================================

param(
    [string]$ResourceGroup = "mcp-demo-rg"
)

$ErrorActionPreference = "Stop"

Write-Host "`n========================================"
Write-Host " Scenario 1: Tearing Down Infrastructure"
Write-Host "========================================`n"

# Check the group exists
$exists = az group exists --name $ResourceGroup | ConvertFrom-Json
if (-not $exists) {
    Write-Host "Resource group '$ResourceGroup' does not exist. Nothing to delete." -ForegroundColor Yellow
    exit 0
}

Write-Host "This will DELETE resource group '$ResourceGroup' and ALL resources inside it." -ForegroundColor Red
$confirm = Read-Host "Type the resource group name to confirm"

if ($confirm -ne $ResourceGroup) {
    Write-Host "Aborted. Name did not match." -ForegroundColor Yellow
    exit 0
}

Write-Host "`nDeleting resource group '$ResourceGroup'..."
az group delete --name $ResourceGroup --yes --no-wait
Write-Host "Deletion initiated (async). Resources will be removed in a few minutes." -ForegroundColor Green
Write-Host "Check status: az group show -n $ResourceGroup --query properties.provisioningState -o tsv`n"
