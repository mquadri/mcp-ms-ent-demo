# Open Mic Friday — Real Demo Plan

## Microsoft Enterprise MCP Servers + Multi-Agent Handoff

This document is your step-by-step plan to run a **live** demo of Scenarios 1, 3, and 5 using your real Azure subscription and Azure DevOps environment, powered by the official [Azure MCP Server](https://learn.microsoft.com/en-us/azure/developer/azure-mcp-server/) and [Microsoft MCP Server for Enterprise](https://learn.microsoft.com/en-us/graph/mcp-server/overview), plus the **Semantic Kernel Handoff Orchestration** pattern for multi-agent demos.

---

## Pre-Demo Checklist (Do These Before Friday)

### Phase 1: Tenant-Level Setup (One-Time, ~15 min)

These steps register the official Microsoft MCP Server for Enterprise in your Entra tenant and grant VS Code permission to call it. You need **Application Administrator** or **Cloud Application Administrator** role.

#### Step 1 — Install the Entra PowerShell Module

```powershell
# Run PowerShell as Administrator
Install-Module Microsoft.Entra.Beta -Force -AllowClobber
```

> If you have the Microsoft Graph PowerShell SDK installed and hit conflicts:
> ```powershell
> Install-Module Uninstall-Graph
> Uninstall-Graph -All
> ```

#### Step 2 — Authenticate to Your Tenant

```powershell
Connect-Entra -Scopes 'Application.ReadWrite.All', 'Directory.Read.All', 'DelegatedPermissionGrant.ReadWrite.All'
```

Verify you're in the right tenant:
```powershell
Get-EntraContext
```

#### Step 3 — Register the MCP Server & Grant VS Code Permissions

```powershell
Grant-EntraBetaMCPServerPermission -ApplicationName VisualStudioCode
```

This does two things:
1. Creates a service principal for the Microsoft MCP Server for Enterprise (`AppId: e8c77dc2-69b3-43f4-bc51-3213c9d915b4`)
2. Grants VS Code (`AppId: aebc6443-996d-45c2-90f0-388ff96faa56`) all MCP.* delegated scopes

#### Step 4 — Verify Registration

```powershell
# Both should return results
Get-EntraBetaServicePrincipal -Filter "AppId eq 'e8c77dc2-69b3-43f4-bc51-3213c9d915b4'" | Select-Object DisplayName, AppId
Get-EntraBetaServicePrincipal -Filter "AppId eq 'aebc6443-996d-45c2-90f0-388ff96faa56'" | Select-Object DisplayName, AppId
```

Expected output:
| DisplayName | AppId |
|-------------|-------|
| Microsoft MCP Server for Enterprise | `e8c77dc2-69b3-43f4-bc51-3213c9d915b4` |
| Visual Studio Code | `aebc6443-996d-45c2-90f0-388ff96faa56` |

---

### Phase 2: Azure Resources Setup (~20 min)

#### Step 5 — Create Resource Group

```powershell
az group create --name contoso-monitoring --location eastus
```

#### Step 6 — Create Log Analytics Workspace (Scenarios 1 & 5)

```powershell
az monitor log-analytics workspace create `
  --resource-group contoso-monitoring `
  --workspace-name contoso-logs `
  --location eastus

# Get the workspace ID — save this
az monitor log-analytics workspace show `
  --resource-group contoso-monitoring `
  --workspace-name contoso-logs `
  --query customerId -o tsv
```

#### Step 7 — Create Cosmos DB Account + Database + Container (Scenario 5)

```powershell
# Create the Cosmos DB account (serverless to minimize cost)
az cosmosdb create `
  --resource-group contoso-monitoring `
  --name contoso-analytics `
  --kind GlobalDocumentDB `
  --capabilities EnableServerless `
  --locations regionName=eastus

# Create database
az cosmosdb sql database create `
  --account-name contoso-analytics `
  --resource-group contoso-monitoring `
  --name dev_analytics

# Create container
az cosmosdb sql container create `
  --account-name contoso-analytics `
  --resource-group contoso-monitoring `
  --database-name dev_analytics `
  --name velocity_metrics `
  --partition-key-path "/id"

# Get the endpoint and key — save these
az cosmosdb show --name contoso-analytics -g contoso-monitoring --query documentEndpoint -o tsv
az cosmosdb keys list --name contoso-analytics -g contoso-monitoring --query primaryMasterKey -o tsv
```

#### Step 8 — Azure DevOps Setup

Your ADO org already exists. Verify/create the project:

```powershell
# Set your org URL
az devops configure --defaults organization=https://dev.azure.com/YOUR_ORG

# Create project if it doesn't exist
az devops project create --name ContosoApp --description "MCP Demo Project"

# Create a PAT at: https://dev.azure.com/YOUR_ORG/_usersSettings/tokens
# Required scopes: Work Items (Read & Write), Code (Read), Build (Read)
```

---

### Phase 3: Configure MCP Servers in VS Code (~10 min)

#### Step 9a — Install Azure MCP Server

The Azure MCP Server runs locally via npx:

```powershell
# Test that it runs
npx -y @azure/mcp@latest server start

# Add to .vscode/settings.json (or copy from configuration/vscode-mcp-settings.json)
```

Configuration in `.vscode/settings.json`:

```json
{
  "mcpServers": {
    "azure-mcp-server": {
      "command": "npx",
      "args": ["-y", "@azure/mcp@latest", "server", "start"],
      "env": {
        "AZURE_SUBSCRIPTION_ID": "<your-sub-id>",
        "AZURE_TENANT_ID": "<your-tenant-id>"
      }
    }
  }
}
```

#### Step 9b — Install Microsoft Enterprise MCP Server in VS Code

**Option A — One-click install (recommended for demo):**

Click this link to install: [Install Microsoft MCP Server for Enterprise](https://vscode.dev/redirect/mcp/install?name=Microsoft%20MCP%20Server%20for%20Enterprise&config=%7b%22name%22:%22Microsoft%20MCP%20Server%20for%20Enterprise%22%2c%22type%22:%22http%22%2c%22url%22:%22https://mcp.svc.cloud.microsoft/enterprise%22%7d)

This adds the following to your VS Code MCP settings:
```json
{
  "name": "Microsoft MCP Server for Enterprise",
  "type": "http",
  "url": "https://mcp.svc.cloud.microsoft/enterprise"
}
```

**Option B — Manual `.vscode/settings.json`:**

Copy the contents of `configuration/copilot-enterprise-settings.json` into `.vscode/settings.json` in this repo.

#### Step 10 — Configure Environment Variables

```powershell
# Copy and fill in your .env
Copy-Item .env.example .env

# Edit .env — set these to your real values:
# USE_MOCK_DATA=false
# AZURE_SUBSCRIPTION_ID=<your-sub-id>
# LOG_ANALYTICS_WORKSPACE_ID=<from step 6>
# AZURE_DEVOPS_ORG_URL=https://dev.azure.com/YOUR_ORG
# AZURE_DEVOPS_PROJECT=ContosoApp
# AZURE_DEVOPS_PAT=<from step 8>
# AZURE_TENANT_ID=<your-tenant-id>
# COSMOS_DB_ENDPOINT=<from step 7>
# COSMOS_DB_KEY=<from step 7>
```

#### Step 11 — Seed Data for the Demo

```powershell
# Activate Python environment
mcp_env\Scripts\activate

# Seed Scenario 1 data (alerts, logs, tickets)
$env:USE_MOCK_DATA = "false"
python demos/setup_scenario_1.py

# Seed Scenario 3 data (multi-agent orchestration metadata)
python demos/setup_scenario_3.py

# Seed Scenario 5 data (sprints, builds, deployments, trends)
python demos/setup_scenario_5.py

# Inject sample logs into real Log Analytics
.\demos\scenario_1_inject.ps1
```

#### Step 12 — Verify MCP Servers Are Connected

1. Open VS Code
2. Open GitHub Copilot Chat (Agent mode)
3. You should see the MCP servers listed — click to verify each one is green
4. Test with a simple query: *"How many users are in my tenant?"*

---

## Demo Day Runbook

### Before You Go On Stage

- [ ] VS Code open with this repo
- [ ] Copilot Chat panel open in Agent mode
- [ ] MCP servers all showing green
- [ ] Terminal with `mcp_env` activated
- [ ] `.env` configured with real credentials, `USE_MOCK_DATA=false`
- [ ] Run both setup scripts fresh (data seeded within the last hour)

---

### Demo Flow: Scenario 1 — Automated Incident Response (~8 min)

**Story**: *"Imagine it's 2 AM and our checkout service is down. Let me show you how AI + the Azure MCP Server can drive the entire incident response."*

#### Act 1: Triage (Azure MCP Server → monitor namespace)

Ask Copilot:
> "Our monitoring is alerting on the CheckoutService. Fetch all active critical alerts from Azure Monitor for the contoso-monitoring resource group. Show me the service name, error code, affected resources, and incident timeline."

**What the audience sees**: Copilot calls the Azure MCP Server's monitor tools, pulls back real alerts, and summarizes the incident.

#### Act 2: Root Cause (Azure MCP Server → monitor/appinsights)

Ask Copilot:
> "Pull the last 10 ERROR-level application logs from the CheckoutService. Correlate them with the alerts and identify the root cause error pattern."

**What the audience sees**: Copilot digs into Log Analytics via the Azure MCP Server, finds the `ConnectionPoolExhausted` errors, and explains the cascading failure.

#### Act 3: Create Ticket (Azure DevOps)

Ask Copilot:
> "Create a Severity 1 bug in the ContosoApp Azure DevOps project titled 'CRITICAL: CheckoutService DB Connection Timeout'. Include the error stack trace and affected resources in the description. Tag it with 'incident' and 'auto-generated'."

**What the audience sees**: A real work item gets created in ADO — you can open the link to show it.

#### Act 4: Identify On-Call (Microsoft Graph via Enterprise MCP)

Ask Copilot:
> "Who are the members of the Platform Engineering team? Who should handle this incident?"

**What the audience sees**: The Enterprise MCP server queries Microsoft Graph using RAG-generated API calls, returns real user info from your tenant.

#### Act 5: Assign (Azure DevOps)

Ask Copilot:
> "Assign that critical incident ticket to [name from Act 4]."

**What the audience sees**: Work item gets assigned in real-time in ADO.

---

### Demo Flow: Scenario 3 — Multi-Agent Handoff (~10 min)

**Story**: *"Now let me show you something cutting edge — the Microsoft Semantic Kernel Agent Framework. Instead of one AI agent doing everything, we have three specialized agents that hand off to each other like a real incident response team."*

#### Act 1: Explain the Architecture

Show the ASCII diagram from `agents/README.md` or slides:

```
TriageAgent → DiagnosticsAgent → RemediationAgent
```

**Talking points**:
- Each agent has a specialized system prompt and tool access
- Uses the Handoff Orchestration pattern from Semantic Kernel
- Agents dynamically decide when to hand off based on their analysis
- This is one of 5 orchestration patterns in the Microsoft Agent Framework (Sequential, Concurrent, Handoff, Group Chat, Magentic)

#### Act 2: Run the Mock Orchestration

In the terminal:
```powershell
python agents/incident_remediation.py
```

**What the audience sees**: Three agents execute in sequence:
1. **TriageAgent** classifies as Sev1, identifies 4 affected resources
2. **DiagnosticsAgent** correlates logs, finds DB connection pool exhaustion
3. **RemediationAgent** creates Bug #54321, assigns to Ahmed Hassan

#### Act 3: Run with Real Semantic Kernel (Optional)

If you have Azure OpenAI configured:
```powershell
$env:USE_MOCK_DATA = "false"
python agents/incident_remediation.py --real
```

**What the audience sees**: Real LLM-powered agents reasoning and handing off to each other, calling Azure MCP Server tools, and creating real work items.

#### Act 4: Highlight the Agent Definitions

Open `agents/agent_definitions.yaml` and show:
- Each agent's system prompt
- Tool bindings (Azure MCP Server namespaces, Enterprise MCP)
- Handoff targets (who can hand off to whom)

**Key message**: *"This is the Microsoft-approved way to build multi-agent systems — Semantic Kernel's Handoff Orchestration, running on Azure OpenAI, using official MCP servers for Azure and Graph."*

---

### Demo Flow: Scenario 5 — Development Velocity Analysis (~7 min)

**Story**: *"Now let me show you something for our engineering leadership — a full velocity dashboard powered by AI."*

#### Act 1: Sprint Health (Azure DevOps)

Ask Copilot:
> "Pull sprint metrics for our last 3 sprints from the ContosoApp project in Azure DevOps. What's our velocity trend — are we accelerating or decelerating?"

#### Act 2: Build & Deploy Health (Azure Monitor)

Ask Copilot:
> "Query Azure Monitor for 30-day build pipeline metrics for ContosoApp-CI. What's our average build time, success rate, and deployment frequency? Are there any concerning trends?"

#### Act 3: Historical Trends (Cosmos DB)

Ask Copilot:
> "Read the velocity trend documents from the dev_analytics database in Cosmos DB. Show me the 12-week trajectory and forecast next sprint's velocity."

#### Act 4: Executive Summary (Multi-Tool)

Ask Copilot:
> "Give me a comprehensive development velocity report. Pull sprint data from Azure DevOps, build metrics from Azure Monitor, and historical trends from Cosmos DB. Summarize: current velocity vs target, build stability, deployment cadence, code review efficiency. Recommend 3 specific improvements."

---

### Bonus: Microsoft Enterprise MCP Power Query

This uses the official Microsoft MCP Server for Enterprise to query Entra data:

> "Show me all users with the Global Administrator role in my tenant. Are any assigned via PIM eligible assignments?"

> "List all enterprise applications registered in the last 30 days. Do any have excessive permissions?"

> "What is the compliance status of devices in my organization? How many are non-compliant?"

---

## Architecture Diagram for Slides

```
┌─────────────────────────────────────────────────────────────────┐
│                     VS Code + GitHub Copilot                    │
│                          (Agent Mode)                           │
└───┬──────────────────────────────┬──────────────────────────────┘
    │                              │
    ▼                              ▼
┌──────────────────┐     ┌──────────────────────────┐
│  Azure MCP Server│     │  MS Enterprise MCP Server│
│  @azure/mcp      │     │  mcp.svc.cloud.microsoft │
│  (npx, stdio)    │     │  .com/enterprise (HTTP)  │
│                  │     │                          │
│  50+ Azure tools │     │  3 Graph/Entra tools     │
│  via namespaces  │     │  RAG-powered             │
└────────┬─────────┘     └──────────┬───────────────┘
         │                          │
         ▼                          ▼
┌──────────────────┐     ┌──────────────────────────┐
│ Azure Services   │     │  graph.microsoft.com     │
│ (via Entra/RBAC) │     │  Entra ID / Azure AD     │
│                  │     │                          │
│ Monitor          │     └──────────────────────────┘
│ Cosmos DB        │
│ App Insights     │
│ Key Vault        │
│ Storage          │     ┌──────────────────────────┐
│ App Service      │     │  Semantic Kernel         │
│ Functions        │     │  Handoff Orchestration   │
│ AKS              │     │  (Scenario 3)            │
│ Deploy           │     │                          │
│ + more...        │     │ Triage → Diagnostics     │
└──────────────────┘     │         → Remediation    │
                         └──────────────────────────┘

   Scenario 1: Azure MCP (monitor) → DevOps → Enterprise MCP (Graph)
   Scenario 3: SK Handoff: TriageAgent → DiagnosticsAgent → RemediationAgent
   Scenario 5: Azure MCP (monitor, cosmos) → DevOps
   Bonus:      Enterprise MCP → Entra ID (Identity & Security)
```

---

## Cleanup After Demo

```powershell
# Delete the resource group (removes Log Analytics + Cosmos DB)
az group delete --name contoso-monitoring --yes --no-wait

# Optionally disable the Enterprise MCP Server in your tenant
# (only if you don't want to keep it)
# Invoke-MgGraphRequest -Method PATCH `
#   -Uri "https://graph.microsoft.com/v1.0/servicePrincipals(appId='e8c77dc2-69b3-43f4-bc51-3213c9d915b4')" `
#   -Body '{"accountEnabled": false}'
```

---

## Estimated Costs

| Resource | Cost | Notes |
|----------|------|-------|
| Log Analytics Workspace | ~$0 for demo volume | First 5 GB/month free |
| Cosmos DB (Serverless) | ~$0 for demo volume | Pay per RU consumed |
| Azure DevOps | Free tier | 5 users free |
| Enterprise MCP Server | Free | No extra license |
| Total | **~$0** | Demo-scale data only |
