# Microsoft Enterprise MCP Servers - Demo Scenarios

This directory contains end-to-end scenarios demonstrating **Microsoft Enterprise MCP Servers** with real-world use cases. Each scenario includes setup scripts to populate sample data and prompts for testing with GitHub Copilot or other AI agents.

## Scenario Overview

| Scenario | Focus | MCP Servers Used |
|----------|-------|-----------------|
| **1** | Automated Incident Response | Azure Monitor, Azure DevOps, Microsoft Graph |
| **5** | Development Velocity Analysis | Azure DevOps, Azure Monitor, Cosmos DB |

---

## Project Setup

Follow these steps to configure your environment and enable the necessary MCP servers.

### 1. Prerequisites

- **Azure Subscription** with billing enabled (not required for mock mode)
- **Azure CLI** installed and authenticated:
  ```bash
  az login
  az account set --subscription YOUR_SUBSCRIPTION_ID
  ```
- **Python 3.9+**
- **Node.js 18+** (for MCP server packages via `npx`)
- **Git**

### 2. Required Azure Resources

Provision these resources in your Azure subscription. Skip this section if using mock mode (`USE_MOCK_DATA=true`).

#### Scenario 1: Automated Incident Response

| Resource | Purpose | How to Create |
|----------|---------|---------------|
| **Log Analytics Workspace** | Store and query application logs & alerts | `az monitor log-analytics workspace create -g contoso-monitoring -n contoso-logs` |
| **Azure DevOps Organization** | Incident ticket creation & tracking | [Create at dev.azure.com](https://dev.azure.com) |
| **Azure DevOps Project** | Project named `ContosoApp` | `az devops project create --name ContosoApp --org https://dev.azure.com/YOUR_ORG` |
| **Azure AD App Registration** | Microsoft Graph access for user/team lookups | See [App Registration Steps](#app-registration-for-microsoft-graph) below |
| **DevOps PAT** | Authentication token for DevOps API | [Create PAT](https://dev.azure.com/_usersSettings/tokens) — scopes: `Work Items: Read & Write` |

#### Scenario 5: Development Velocity Analysis

| Resource | Purpose | How to Create |
|----------|---------|---------------|
| **Azure DevOps** (same as above) | Sprint metrics, repo stats, pipeline runs | Same as Scenario 1 |
| **Log Analytics Workspace** (same) | Build and deployment performance logs | Same as Scenario 1 |
| **Cosmos DB Account** | Historical velocity trend storage | `az cosmosdb create -g contoso-monitoring -n contoso-analytics --kind GlobalDocumentDB` |
| **Cosmos DB Database** | `dev_analytics` database | `az cosmosdb sql database create -a contoso-analytics -g contoso-monitoring -n dev_analytics` |
| **Cosmos DB Container** | `velocity_metrics` container | `az cosmosdb sql container create -a contoso-analytics -g contoso-monitoring -d dev_analytics -n velocity_metrics --partition-key-path "/id"` |

### 3. App Registration for Microsoft Graph

Scenario 1 uses Microsoft Graph to look up on-call engineers. Create an App Registration:

```bash
# Create the app registration
az ad app create --display-name "MCP-Enterprise-Demo" \
  --sign-in-audience AzureADMyOrg

# Note the appId from the output, then create a service principal
az ad sp create --id YOUR_APP_ID

# Create a client secret (note the value — it won't be shown again)
az ad app credential reset --id YOUR_APP_ID --append

# Grant API permissions (User.Read.All, Group.Read.All)
az ad app permission add --id YOUR_APP_ID \
  --api 00000003-0000-0000-c000-000000000000 \
  --api-permissions df021288-bdef-4463-88db-98f22de89214=Role \
                    5b567255-7703-4780-807c-7be8301ae99b=Role

# Admin consent
az ad app permission admin-consent --id YOUR_APP_ID
```

Record the Tenant ID, Client ID, and Client Secret in your `.env` file.

### 4. Environment Configuration

```bash
# Copy the template
cp .env.example .env

# Edit with your values
# For mock mode (no Azure needed), only USE_MOCK_DATA=true is required
```

Key variables:

| Variable | Required For | Description |
|----------|-------------|-------------|
| `USE_MOCK_DATA` | All | Set `true` for mock mode, `false` for real Azure |
| `AZURE_SUBSCRIPTION_ID` | All (real mode) | Your Azure subscription ID |
| `LOG_ANALYTICS_WORKSPACE_ID` | Scenario 1, 5 | Log Analytics workspace ID |
| `AZURE_DEVOPS_ORG_URL` | Scenario 1, 5 | e.g., `https://dev.azure.com/contoso-org` |
| `AZURE_DEVOPS_PROJECT` | Scenario 1, 5 | e.g., `ContosoApp` |
| `AZURE_DEVOPS_PAT` | Scenario 1, 5 | Personal Access Token |
| `AZURE_TENANT_ID` | Scenario 1 | Azure AD tenant ID |
| `AZURE_CLIENT_ID` | Scenario 1 | App Registration client ID |
| `AZURE_CLIENT_SECRET` | Scenario 1 | App Registration client secret |
| `COSMOS_DB_ENDPOINT` | Scenario 5 | e.g., `https://contoso-analytics.documents.azure.com:443/` |
| `COSMOS_DB_KEY` | Scenario 5 | Cosmos DB primary key |

### 5. Local Python Environment

```bash
# Create and activate virtual environment
python -m venv mcp_env

# Windows
mcp_env\Scripts\activate

# macOS / Linux
# source mcp_env/bin/activate

# Install dependencies
pip install -r demos/requirements.txt
```

### 6. MCP Server Configuration

#### Option A: VS Code + GitHub Copilot (Recommended)

Copy `configuration/vscode-mcp-settings.json` contents into your `.vscode/settings.json`. VS Code will prompt you for credential values on first use.

#### Option B: Manual JSON Configuration

Add the following to your MCP client's settings. Replace placeholders with your actual values.

```json
{
  "mcpServers": {
    "azure-monitor": {
      "command": "npx",
      "args": ["-y", "@azure/mcp-server-monitor"],
      "env": {
        "AZURE_SUBSCRIPTION_ID": "YOUR_SUBSCRIPTION_ID",
        "AZURE_RESOURCE_GROUP": "contoso-monitoring",
        "LOG_ANALYTICS_WORKSPACE_ID": "YOUR_WORKSPACE_ID"
      }
    },
    "azure-devops": {
      "command": "npx",
      "args": ["-y", "@azure/mcp-server-devops"],
      "env": {
        "AZURE_DEVOPS_ORG_URL": "https://dev.azure.com/YOUR_ORG",
        "AZURE_DEVOPS_PROJECT": "ContosoApp",
        "AZURE_DEVOPS_PAT": "YOUR_PAT"
      }
    },
    "microsoft-graph": {
      "command": "npx",
      "args": ["-y", "@azure/mcp-server-graph"],
      "env": {
        "AZURE_TENANT_ID": "YOUR_TENANT_ID",
        "AZURE_CLIENT_ID": "YOUR_CLIENT_ID",
        "AZURE_CLIENT_SECRET": "YOUR_CLIENT_SECRET"
      }
    },
    "azure-cosmos": {
      "command": "npx",
      "args": ["-y", "@azure/mcp-server-cosmos"],
      "env": {
        "COSMOS_DB_ENDPOINT": "YOUR_COSMOS_ENDPOINT",
        "COSMOS_DB_KEY": "YOUR_COSMOS_KEY"
      }
    }
  }
}
```

#### Verify Configuration

In VS Code with GitHub Copilot, open the MCP panel to verify your servers are connected. Each server should show a green status indicator.

---

## Scenario Catalog

### 1. Automated Incident Response (DevOps)

**Use Case**: A sudden spike in checkout service errors triggers alerts. The AI agent pulls critical alerts from Azure Monitor, correlates error logs, creates an incident ticket in Azure DevOps, looks up the on-call engineer via Microsoft Graph, and assigns the ticket.

**MCP Servers**: Azure Monitor, Azure DevOps, Microsoft Graph

**Setup**:

This setup script populates mock (or real) data across three Microsoft services:

- **Azure Monitor**: Seeds 3 critical alerts (CheckoutService DB timeout, PaymentGateway 503 errors, NotificationService queue overflow) and 3 correlated error log entries with stack traces and request IDs.
- **Azure DevOps**: Creates a Severity 1 bug work item in the ContosoApp project with full incident description, tagged `incident;auto-generated;critical`.
- **Microsoft Graph**: Resolves the on-call engineer for the Platform team (Ahmed Hassan) and assigns the work item to them.

```bash
# Run the full setup (mock mode by default)
python demos/setup_scenario_1.py

# Or inject logs into real Azure Monitor (requires Azure CLI auth)
./demos/scenario_1_inject.ps1
```

**Expected Output**:
```
======================================================================
🚨 SCENARIO 1: AUTOMATED INCIDENT RESPONSE - SETUP
======================================================================
Mode: MOCK DATA

📊 Seeding Azure Monitor with critical alerts...
   ✓ Alert alert-001: CheckoutService - Database connection timeout
   ✓ Alert alert-002: PaymentGateway - Payment processor API returning 503 errors
   ✓ Alert alert-003: NotificationService - Email queue backing up

📋 Seeding application error logs...
   ✓ CheckoutService: Database query timeout after 5000ms
   ✓ PaymentGateway: External API unreachable: Stripe gateway returns 503
   ✓ CheckoutService: Connection pool exhausted

✅ [MOCK] Created DevOps work item: #54321 - CRITICAL: Checkout Service - Database Connection Timeout

📞 On-call engineer: Ahmed Hassan (ahmed.hassan@contoso.com)

✅ [MOCK] Assigned work item 54321 to ahmed.hassan@contoso.com

======================================================================
✅ SCENARIO 1 SETUP COMPLETE
======================================================================
```

**Copilot Prompts**:

> "Our monitoring is alerting on the CheckoutService. Fetch all active critical alerts from Azure Monitor for the contoso-monitoring resource group. For each alert, extract the service name, error code, and affected resources. Summarize the incident timeline."

> "Pull the last 10 ERROR-level application logs from CheckoutService. Identify the root cause. Create a Severity 1 bug in Azure DevOps with the error details, then find the on-call Platform engineer via Microsoft Graph and assign the ticket to them."

---

### 5. Migration Performance Validation / Development Velocity Analysis (Ops/Eng)

**Use Case**: The engineering team needs a comprehensive view of development velocity — sprint metrics, build/deployment performance, code review efficiency, and 12-week historical trends — to identify bottlenecks and drive improvements.

**MCP Servers**: Azure DevOps, Azure Monitor, Cosmos DB

**Setup**:

This setup script populates data across three services for velocity analysis:

- **Azure DevOps**: Seeds 3 sprints (22, 23, 24) with work item counts, velocity points, completion percentages, and test pass rates. Also populates repository metrics (commits/day, PR merge rate, review time, branch coverage).
- **Azure Monitor**: Generates 30 days of build logs (3–5 builds/day with duration, test pass/fail, coverage) and deployment logs (1–3 deploys/day across Staging/Production with success/rollback rates).
- **Cosmos DB**: Stores 12 weeks of historical velocity trend documents (velocity points, completion rate, bug escape rate, deployment frequency, mean time to recovery, team size).

```bash
python demos/setup_scenario_5.py
```

**Expected Output**:
```
======================================================================
📊 SCENARIO 5: DEVELOPMENT VELOCITY ANALYSIS - SETUP
======================================================================
Mode: MOCK DATA

📊 Azure DevOps Sprint Metrics:
   Sprint 24:
      Velocity: 156 / 160 points
      Completion: 90.5%
      Test Pass Rate: 96.2%
   Sprint 23:
      Velocity: 152 / 155 points
      Completion: 95.0%
   Sprint 22:
      Velocity: 148 / 150 points
      Completion: 94.7%

📈 Repository Metrics:
   Commits/Day: 42
   PRs Merged/Day: 8
   Avg PR Review Time: 3.2 hours
   Branch Coverage: 87.3%

🔨 Build Performance Logs (Last 30 Days):
   Total Builds: ~120
   Success Rate: ~85%

🚀 Deployment Logs (Last 30 Days):
   Total Deployments: ~60
   Production Deployments: ~30

📊 Cosmos DB Velocity Trends (12 Weeks):
   Documents Stored: 12

======================================================================
✅ SCENARIO 5 SETUP COMPLETE
======================================================================
```

**Copilot Prompts**:

> "Pull sprint metrics for Sprints 22–24 from Azure DevOps. Show the velocity trend and tell me if the team is accelerating or decelerating."

> "Query Azure Monitor for 30-day build pipeline metrics. Calculate average build duration, success rate, and test pass rate. Then pull deployment logs and report deployment frequency and rollback rate."

> "Read the velocity trend documents from Cosmos DB (dev_analytics / velocity_metrics). Plot the 12-week trajectory and forecast next sprint's expected velocity."

> "Build me a comprehensive development velocity report combining sprint data from DevOps, build metrics from Azure Monitor, and historical trends from Cosmos DB. Recommend 3 actions to improve throughput."

---

## Mock Data Generator

The `mock_data_generator.py` utility generates realistic sample data for both scenarios without requiring Azure credentials:

```bash
python demos/mock_data_generator.py
```

This creates JSON files:
- `mock_data_scenario_1.json` — Alerts, error logs, ticket details
- `mock_data_scenario_5.json` — Sprint metrics, build/deployment logs

---

## Files

| File | Description |
|------|-------------|
| `setup_scenario_1.py` | Full Scenario 1 setup (alerts, logs, ticket, on-call) |
| `setup_scenario_5.py` | Full Scenario 5 setup (sprints, builds, deployments, trends) |
| `scenario_1_inject.ps1` | PowerShell script to inject logs into real Azure Monitor |
| `mock_data_generator.py` | Standalone mock data generator |
| `requirements.txt` | Python dependencies |
| `SETUP_SUMMARY.md` | Summary of generated files |

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| `ModuleNotFoundError: azure.identity` | Run `pip install -r demos/requirements.txt` |
| `AZURE_SUBSCRIPTION_ID not set` | Copy `.env.example` to `.env` and fill in values |
| Mock mode not working | Ensure `USE_MOCK_DATA=true` is set (default) |
| DevOps ticket creation fails | Verify PAT has `Work Items: Read & Write` scope |
| Graph API 403 Forbidden | Run `az ad app permission admin-consent --id YOUR_APP_ID` |
| Cosmos DB 401 Unauthorized | Check endpoint URL and key in `.env` |