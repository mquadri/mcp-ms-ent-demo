# System Architecture

## Overview

Microsoft Enterprise MCP Servers integrate AI agents with Microsoft cloud services through the Model Context Protocol. This repo uses two official Microsoft MCP servers plus the Semantic Kernel Agent Framework for multi-agent orchestration.

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    AI Agent (GitHub Copilot)                    │
│                                                                 │
│   User Prompt ──► Tool Selection ──► Orchestration              │
└────────────┬────────────────────────────────┬───────────────────┘
             │                                │
       MCP Protocol (stdio)           MCP Protocol (HTTP)
             │                                │
    ┌────────▼──────────┐          ┌──────────▼───────────────┐
    │  Azure MCP Server │          │  MS Enterprise MCP Server│
    │  @azure/mcp       │          │  mcp.svc.cloud.microsoft │
    │                   │          │  .com/enterprise          │
    │  Namespaces:      │          │                          │
    │  • monitor        │          │  Tools:                  │
    │  • cosmos         │          │  • graph_suggest_queries │
    │  • appinsights    │          │  • graph_get             │
    │  • keyvault       │          │  • graph_list_properties │
    │  • storage        │          └──────────┬───────────────┘
    │  • appservice     │                     │
    │  • functionapp    │              ┌──────▼──────┐
    │  • aks            │              │  Entra ID / │
    │  • role / deploy  │              │  MS Graph   │
    │  • + 15 more...   │              │  API        │
    └────────┬──────────┘              └─────────────┘
             │
    ┌────────▼──────────┐
    │  Azure Services   │
    │  (via Azure       │
    │   Identity/RBAC)  │
    │                   │
    │  Log Analytics    │
    │  Cosmos DB        │
    │  App Insights     │
    │  Key Vault        │
    │  Storage          │
    │  App Service      │
    │  AKS, etc.        │
    └───────────────────┘
```

## Scenario 1: Automated Incident Response

Single-agent, multi-tool orchestration. Copilot fans out across Azure MCP Server namespaces and the Enterprise MCP.

```
User: "Fetch critical alerts and create an incident ticket"
  │
  ├──► Azure MCP Server (monitor namespace)
  │      └─ fetch_critical_alerts()  → Returns 3 alerts
  │      └─ get_error_logs()         → Returns correlated logs
  │
  ├──► Azure DevOps REST API (via agent plugin)
  │      └─ create_work_item()       → Creates Sev1 bug #54321
  │
  ├──► Enterprise MCP Server (Microsoft Graph)
  │      └─ microsoft_graph_get()    → Resolves Platform team
  │      └─ microsoft_graph_get()    → Returns on-call engineer
  │
  └──► Azure DevOps REST API
         └─ assign_work_item()       → Assigns to Ahmed Hassan
```

### Data Flow

1. **Alert Detection**: Azure MCP Server → monitor namespace detects critical alerts
2. **Log Correlation**: Azure MCP Server → monitor/appinsights namespace correlates logs
3. **Ticket Creation**: Azure DevOps work item created with full incident context
4. **On-Call Resolution**: Enterprise MCP → Microsoft Graph resolves the on-call engineer
5. **Assignment**: Work item assigned with notification

## Scenario 3: Multi-Agent Incident Remediation (Handoff Pattern)

This scenario uses the **Semantic Kernel Handoff Orchestration** pattern. Three specialized agents form a chain, each able to hand off context to the next.

```
┌─────────────────────────────────────────────────────────────────┐
│                  Semantic Kernel Runtime                        │
│               (HandoffOrchestration)                            │
│                                                                 │
│  ┌──────────────┐    ┌──────────────────┐    ┌──────────────┐  │
│  │ TriageAgent  │───►│ DiagnosticsAgent │───►│ Remediation  │  │
│  │              │    │                  │    │ Agent        │  │
│  │ Classifies   │    │ Root-cause       │    │ Creates WI,  │  │
│  │ severity,    │    │ analysis via     │    │ finds on-call│  │
│  │ blast radius │    │ logs & traces    │    │ assigns      │  │
│  └──────┬───────┘    └────────┬─────────┘    └──────┬───────┘  │
│         │                     │                     │          │
│  ┌──────▼───────┐    ┌───────▼──────────┐  ┌───────▼───────┐  │
│  │ Azure MCP    │    │ Azure MCP        │  │ Enterprise    │  │
│  │ (monitor)    │    │ (appinsights,    │  │ MCP (Graph)   │  │
│  │              │    │  monitor, kusto) │  │ + ADO API     │  │
│  └──────────────┘    └──────────────────┘  └───────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

### Agent Handoff Flow

1. **TriageAgent** receives the incident, queries Azure Monitor for active alerts, classifies severity (Sev1), identifies blast radius
2. **TriageAgent → DiagnosticsAgent** handoff: passes alert data + classification
3. **DiagnosticsAgent** queries Application Insights for traces, identifies root cause (DB connection pool exhaustion)
4. **DiagnosticsAgent → RemediationAgent** handoff: passes root cause + recommended fix
5. **RemediationAgent** creates work item, queries Enterprise MCP for on-call engineer, assigns ticket

## Scenario 5: Multi-Agent Development Velocity Analysis (Sequential Pattern)

This scenario uses the **Semantic Kernel Sequential Orchestration** pattern — a different pattern from Scenario 3's Handoff. Three agents form a fixed data pipeline.

```
┌─────────────────────────────────────────────────────────────────┐
│               Semantic Kernel Runtime                           │
│            (SequentialOrchestration)                             │
│                                                                 │
│  ┌──────────────┐    ┌──────────────────┐    ┌──────────────┐  │
│  │  Metrics     │───►│   Trend          │───►│   Advisor    │  │
│  │  Collector   │    │   Analyst         │    │   Agent      │  │
│  │  Agent       │    │   Agent           │    │              │  │
│  │              │    │                   │    │  Generates   │  │
│  │  Gathers     │    │  Analyzes trends, │    │  exec summary│  │
│  │  5 data      │    │  detects anomaly, │    │  assigns     │  │
│  │  sources     │    │  forecasts        │    │  owners      │  │
│  └──────┬───────┘    └───────────────────┘    └──────┬───────┘  │
│         │                                            │          │
│  ┌──────▼───────────────────┐                 ┌──────▼───────┐  │
│  │ Azure MCP Server         │                 │ Enterprise   │  │
│  │ (monitor, cosmos)        │                 │ MCP (Graph)  │  │
│  │ + Azure DevOps REST API  │                 └──────────────┘  │
│  └──────────────────────────┘                                   │
└─────────────────────────────────────────────────────────────────┘
```

### Sequential Pipeline Flow

1. **MetricsCollectorAgent** gathers data from 5 sources:
   - Azure DevOps → sprint metrics (velocity, completion, test pass rate)
   - Azure DevOps → repo statistics (commits, PRs, review times)
   - Azure MCP Server (monitor) → 30-day build logs
   - Azure MCP Server (monitor) → 30-day deployment logs
   - Azure MCP Server (cosmos) → 12-week historical velocity trends
2. **MetricsCollectorAgent → TrendAnalystAgent**: passes raw data bundle
3. **TrendAnalystAgent** performs analysis:
   - Velocity trend (accelerating/decelerating)
   - Build stability scoring
   - Deployment cadence and rollback rates
   - Anomaly detection (thresholds exceeded)
   - Sprint 25 velocity forecast
4. **TrendAnalystAgent → AdvisorAgent**: passes analysis + anomalies + forecast
5. **AdvisorAgent** generates executive report:
   - Queries Enterprise MCP for engineering leadership
   - Produces prioritized recommendations with owners
   - Creates improvement roadmap

## Authentication

| MCP Server / Service | Auth Method | Notes |
|---------------------|-------------|-------|
| Azure MCP Server | Entra ID / `DefaultAzureCredential` / RBAC | Auto-refreshed; no keys needed |
| Enterprise MCP Server | Delegated OAuth2 via VS Code | Requires `Grant-EntraBetaMCPServerPermission` |
| Azure DevOps | Azure Identity or PAT | PAT for setup scripts; identity for MCP |

## Mock vs. Real Mode

- **Mock Mode** (`USE_MOCK_DATA=true`): All tool calls return synthetic data. No Azure resources required.
- **Real Mode** (`USE_MOCK_DATA=false`): MCP servers connect to actual Azure services. For Scenario 3 real mode, also requires Azure OpenAI for Semantic Kernel agents.
