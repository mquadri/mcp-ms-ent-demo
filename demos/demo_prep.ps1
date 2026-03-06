# ============================================================================
# Demo Day Prep Script — Provisions all Azure resources and seeds data
# ============================================================================
# Run this BEFORE your demo to set up everything from scratch.
#
# Prerequisites:
#   - Azure CLI authenticated (az login)
#   - Entra PowerShell module installed (see docs/DEMO_PLAN_REAL.md Phase 1)
#   - Python 3.9+ with venv activated
#   - .env file configured with real values
#
# Usage:
#   .\demos\demo_prep.ps1 -ResourceGroup "contoso-monitoring" -Location "eastus"
# ============================================================================

param(
    [string]$ResourceGroup = "contoso-monitoring",
    [string]$Location = "eastus",
    [string]$CosmosAccount = "contoso-analytics",
    [string]$WorkspaceName = "contoso-logs",
    [switch]$SkipResourceCreation,
    [switch]$SeedDataOnly
)

$ErrorActionPreference = "Stop"

Write-Host "`n========================================"
Write-Host " MCP Enterprise Demo — Prep Script"
Write-Host "========================================`n" -ForegroundColor Cyan

# --- Load .env ---
if (Test-Path ".env") {
    Get-Content ".env" | ForEach-Object {
        if ($_ -match "^\s*([^#][^=]+)=(.*)$") {
            [System.Environment]::SetEnvironmentVariable($matches[1].Trim(), $matches[2].Trim(), "Process")
        }
    }
    Write-Host "[OK] Loaded .env" -ForegroundColor Green
} else {
    Write-Host "[WARN] No .env file found. Copy .env.example to .env and fill in values." -ForegroundColor Yellow
}

# --- Verify Azure CLI ---
$account = az account show --query "{sub:id, name:name, tenant:tenantId}" -o json 2>$null | ConvertFrom-Json
if (-not $account) {
    Write-Host "[ERROR] Not logged in to Azure CLI. Run 'az login' first." -ForegroundColor Red
    exit 1
}
Write-Host "[OK] Azure CLI: $($account.name) ($($account.sub))" -ForegroundColor Green
Write-Host "     Tenant: $($account.tenant)"

if (-not $SkipResourceCreation -and -not $SeedDataOnly) {

    # --- Step 1: Resource Group ---
    Write-Host "`n--- Step 1: Resource Group ---" -ForegroundColor Yellow
    $rgExists = az group exists --name $ResourceGroup 2>$null
    if ($rgExists -eq "true") {
        Write-Host "[OK] Resource group '$ResourceGroup' already exists" -ForegroundColor Green
    } else {
        az group create --name $ResourceGroup --location $Location --output none
        Write-Host "[OK] Created resource group '$ResourceGroup'" -ForegroundColor Green
    }

    # --- Step 2: Log Analytics Workspace ---
    Write-Host "`n--- Step 2: Log Analytics Workspace ---" -ForegroundColor Yellow
    $wsExists = az monitor log-analytics workspace show -g $ResourceGroup -n $WorkspaceName --query customerId -o tsv 2>$null
    if ($wsExists) {
        Write-Host "[OK] Log Analytics workspace exists: $wsExists" -ForegroundColor Green
    } else {
        az monitor log-analytics workspace create -g $ResourceGroup -n $WorkspaceName --location $Location --output none
        $wsExists = az monitor log-analytics workspace show -g $ResourceGroup -n $WorkspaceName --query customerId -o tsv
        Write-Host "[OK] Created Log Analytics workspace: $wsExists" -ForegroundColor Green
    }
    Write-Host "     Set LOG_ANALYTICS_WORKSPACE_ID=$wsExists in .env"

    # --- Step 3: Cosmos DB Account ---
    Write-Host "`n--- Step 3: Cosmos DB (Serverless) ---" -ForegroundColor Yellow
    $cosmosExists = az cosmosdb show --name $CosmosAccount -g $ResourceGroup --query documentEndpoint -o tsv 2>$null
    if ($cosmosExists) {
        Write-Host "[OK] Cosmos DB account exists: $cosmosExists" -ForegroundColor Green
    } else {
        Write-Host "     Creating Cosmos DB (serverless) — this takes a few minutes..."
        az cosmosdb create -g $ResourceGroup -n $CosmosAccount --kind GlobalDocumentDB --capabilities EnableServerless --locations regionName=$Location --output none
        $cosmosExists = az cosmosdb show --name $CosmosAccount -g $ResourceGroup --query documentEndpoint -o tsv
        Write-Host "[OK] Created Cosmos DB: $cosmosExists" -ForegroundColor Green
    }

    # Create database + container
    az cosmosdb sql database create -a $CosmosAccount -g $ResourceGroup -n dev_analytics --output none 2>$null
    az cosmosdb sql container create -a $CosmosAccount -g $ResourceGroup -d dev_analytics -n velocity_metrics --partition-key-path "/id" --output none 2>$null
    Write-Host "[OK] Database 'dev_analytics' / container 'velocity_metrics' ready"

    $cosmosKey = az cosmosdb keys list --name $CosmosAccount -g $ResourceGroup --query primaryMasterKey -o tsv
    Write-Host "     Set COSMOS_DB_ENDPOINT=$cosmosExists in .env"
    Write-Host "     Set COSMOS_DB_KEY=$($cosmosKey.Substring(0,8))... in .env"
}

# --- Step 4: Verify ADO access ---
Write-Host "`n--- Step 4: Azure DevOps ---" -ForegroundColor Yellow
$adoOrg = $env:AZURE_DEVOPS_ORG_URL
$adoProject = $env:AZURE_DEVOPS_PROJECT
$adoPat = $env:AZURE_DEVOPS_PAT

if ($adoOrg -and $adoPat) {
    Write-Host "[OK] ADO Org: $adoOrg" -ForegroundColor Green
    Write-Host "     Project: $adoProject"
} else {
    Write-Host "[WARN] AZURE_DEVOPS_ORG_URL or AZURE_DEVOPS_PAT not set in .env" -ForegroundColor Yellow
}

# --- Step 5: Seed demo data ---
Write-Host "`n--- Step 5: Seeding Demo Data ---" -ForegroundColor Yellow
$env:USE_MOCK_DATA = "false"

Write-Host "`n  Running Scenario 1 setup..."
python demos/setup_scenario_1.py
if ($LASTEXITCODE -ne 0) {
    Write-Host "  [WARN] Scenario 1 setup had errors (may be expected in real mode)" -ForegroundColor Yellow
}

Write-Host "`n  Running Scenario 5 setup..."
python demos/setup_scenario_5.py
if ($LASTEXITCODE -ne 0) {
    Write-Host "  [WARN] Scenario 5 setup had errors (may be expected in real mode)" -ForegroundColor Yellow
}

Write-Host "`n  Injecting logs into Log Analytics..."
& .\demos\scenario_1_inject.ps1

# --- Summary ---
Write-Host "`n========================================"
Write-Host " PREP COMPLETE"
Write-Host "========================================" -ForegroundColor Green
Write-Host @"

Next Steps:
  1. Open VS Code with this repo
  2. Verify MCP servers are connected (Copilot Chat > MCP panel)
  3. Test: "How many users are in my tenant?"
  4. Run through the demo prompts in docs/DEMO_PLAN_REAL.md

Azure Resources:
  Resource Group:   $ResourceGroup
  Log Analytics:    $WorkspaceName
  Cosmos DB:        $CosmosAccount
  ADO Project:      $adoProject

"@
