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

## Scenario 5: Development Velocity Analysis

```
User: "Analyze our development velocity over the last 12 weeks"
  │
  ├──► Azure DevOps REST API
  │      └─ get_sprint_metrics()     → Sprint 22, 23, 24 data
  │      └─ get_repo_statistics()    → Commits, PRs, reviews
  │
  ├──► Azure MCP Server (monitor namespace)
  │      └─ query_log_analytics()    → 30-day build logs
  │      └─ query_log_analytics()    → 30-day deployment logs
  │
  └──► Azure MCP Server (cosmos namespace)
         └─ query_documents()        → 12-week velocity trends
         └─ read_document()          → Individual trend analysis
```

### Data Flow

1. **Sprint Data**: Azure DevOps provides velocity points, completion rates, test pass rates
2. **Build Metrics**: Azure MCP Server (monitor) yields build duration, success rate, coverage
3. **Deployment Metrics**: Deployment frequency, rollback rate, time-to-production
4. **Historical Trends**: Azure MCP Server (cosmos) reads 12 weeks of trend data
5. **Analysis**: AI synthesizes all data into recommendations

## Authentication

| MCP Server / Service | Auth Method | Notes |
|---------------------|-------------|-------|
| Azure MCP Server | Entra ID / `DefaultAzureCredential` / RBAC | Auto-refreshed; no keys needed |
| Enterprise MCP Server | Delegated OAuth2 via VS Code | Requires `Grant-EntraBetaMCPServerPermission` |
| Azure DevOps | Azure Identity or PAT | PAT for setup scripts; identity for MCP |

## Mock vs. Real Mode

- **Mock Mode** (`USE_MOCK_DATA=true`): All tool calls return synthetic data. No Azure resources required.
- **Real Mode** (`USE_MOCK_DATA=false`): MCP servers connect to actual Azure services. For Scenario 3 real mode, also requires Azure OpenAI for Semantic Kernel agents.
