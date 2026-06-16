<#
.SYNOPSIS
Switches Azure CLI context to the MCP demo tenant for live demos.

.DESCRIPTION
Pass tenant and subscription values at runtime so repo history does not contain
environment-specific identifiers. Run Switch-ToDefaultTenant.ps1 when the demo is
done to restore your default context.

.EXAMPLE
.\Switch-ToDemoTenant.ps1 -DemoTenantId "<tenant-id>" -DemoSubscription "<subscription-id>"
#>

param(
    [Parameter(Mandatory = $true)]
    [string]$DemoTenantId,

    [Parameter(Mandatory = $true)]
    [string]$DemoSubscription
)

Write-Host "Switching to demo tenant..." -ForegroundColor Cyan

# Login to the demo tenant (browser prompt will open if not already cached)
az login --tenant $DemoTenantId --allow-no-subscriptions

# Set the demo subscription as active
az account set --subscription $DemoSubscription

# Confirm
$current = az account show --query "{name:name, tenantId:tenantId, subscriptionId:id}" -o json | ConvertFrom-Json
Write-Host ""
Write-Host "Active context:" -ForegroundColor Green
Write-Host "  Subscription : $($current.name) ($($current.subscriptionId))"
Write-Host "  Tenant       : $($current.tenantId)"
Write-Host ""
Write-Host "Demo tenant is active. Run Switch-ToDefaultTenant.ps1 when done." -ForegroundColor Yellow
