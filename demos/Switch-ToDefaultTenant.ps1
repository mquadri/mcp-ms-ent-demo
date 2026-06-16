<#
.SYNOPSIS
Restores Azure CLI context to your default tenant after a demo session.

.EXAMPLE
.\Switch-ToDefaultTenant.ps1 -TenantId "<tenant-id>" -SubscriptionId "<subscription-id>"
#>

param(
    [Parameter(Mandatory = $true)]
    [string]$TenantId,

    [Parameter(Mandatory = $true)]
    [string]$SubscriptionId
)

Write-Host "Switching back to default tenant..." -ForegroundColor Cyan

az login --tenant $TenantId --allow-no-subscriptions
az account set --subscription $SubscriptionId

$current = az account show --query "{name:name, tenantId:tenantId, subscriptionId:id}" -o json | ConvertFrom-Json
Write-Host ""
Write-Host "Active context:" -ForegroundColor Green
Write-Host "  Subscription : $($current.name) ($($current.subscriptionId))"
Write-Host "  Tenant       : $($current.tenantId)"
Write-Host ""
Write-Host "Default tenant restored." -ForegroundColor Green
