# System Architecture

## Overview

Microsoft Enterprise MCP Servers integrate AI agents with Microsoft cloud services through the Model Context Protocol. The architecture enables multi-tool orchestration where a single AI prompt can fan out to multiple backend services.

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    AI Agent (Copilot)                    │
│                                                         │
│   User Prompt ──► Tool Selection ──► Orchestration      │
└──────────┬──────────┬──────────┬──────────┬─────────────┘
           │          │          │          │
     MCP Protocol  MCP Protocol MCP Protocol MCP Protocol
           │          │          │          │
    ┌──────▼───┐ ┌────▼────┐ ┌──▼───┐ ┌────▼─────┐
    │  Azure   │ │  Azure  │ │ MS   │ │  Azure   │
    │ Monitor  │ │ DevOps  │ │Graph │ │ Cosmos   │
    │  Server  │ │ Server  │ │Server│ │ DB Server│
    └──────┬───┘ └────┬────┘ └──┬───┘ └────┬─────┘
           │          │         │           │
    ┌──────▼───┐ ┌────▼────┐ ┌──▼───┐ ┌────▼─────┐
    │   Log    │ │ DevOps  │ │Azure │ │ Cosmos   │
    │Analytics │ │  REST   │ │  AD  │ │   DB     │
    │Workspace │ │  APIs   │ │Graph │ │ Database │
    └──────────┘ └─────────┘ └──────┘ └──────────┘
```

## Scenario 1: Automated Incident Response

```
User: "Fetch critical alerts and create an incident ticket"
  │
  ├──► Azure Monitor MCP Server
  │      └─ fetch_critical_alerts()  → Returns 3 alerts
  │      └─ get_error_logs()         → Returns correlated logs
  │
  ├──► Azure DevOps MCP Server
  │      └─ create_work_item()       → Creates Sev1 bug #54321
  │
  ├──► Microsoft Graph MCP Server
  │      └─ get_team_info()          → Resolves Platform team
  │      └─ get_user_info()          → Returns on-call engineer
  │
  └──► Azure DevOps MCP Server
         └─ assign_work_item()       → Assigns to Ahmed Hassan
```

### Data Flow

1. **Alert Detection**: Azure Monitor detects critical alerts across services
2. **Log Correlation**: Error logs are queried and correlated with alerts
3. **Ticket Creation**: Incident ticket auto-created in Azure DevOps with full context
4. **On-Call Resolution**: Microsoft Graph resolves the on-call engineer
5. **Assignment**: Work item assigned to the engineer with notification

## Scenario 5: Development Velocity Analysis

```
User: "Analyze our development velocity over the last 12 weeks"
  │
  ├──► Azure DevOps MCP Server
  │      └─ get_sprint_metrics()     → Sprint 22, 23, 24 data
  │      └─ get_repo_statistics()    → Commits, PRs, reviews
  │
  ├──► Azure Monitor MCP Server
  │      └─ query_log_analytics()    → 30-day build logs
  │      └─ query_log_analytics()    → 30-day deployment logs
  │
  └──► Cosmos DB MCP Server
         └─ query_documents()        → 12-week velocity trends
         └─ read_document()          → Individual trend analysis
```

### Data Flow

1. **Sprint Data**: Azure DevOps provides velocity points, completion rates, test pass rates
2. **Build Metrics**: Azure Monitor yields build duration, success rate, coverage
3. **Deployment Metrics**: Deployment frequency, rollback rate, time-to-production
4. **Historical Trends**: Cosmos DB stores 12 weeks of trend data for forecasting
5. **Analysis**: AI synthesizes all data into recommendations

## Authentication

| MCP Server | Auth Method | Token Lifetime |
|------------|-------------|----------------|
| Azure Monitor | `DefaultAzureCredential` / Managed Identity | Auto-refreshed |
| Azure DevOps | Personal Access Token (PAT) | Configurable (30-365 days) |
| Microsoft Graph | OAuth2 Client Credentials | 1 hour (auto-refreshed) |
| Cosmos DB | Primary Key / `DefaultAzureCredential` | Key: no expiry; Token: auto-refreshed |

## Mock vs. Real Mode

The architecture supports two operating modes:

- **Mock Mode** (`USE_MOCK_DATA=true`): All MCP server calls return synthetic data. No Azure resources or credentials required. Ideal for local development and testing.
- **Real Mode** (`USE_MOCK_DATA=false`): MCP servers connect to actual Azure services. Requires provisioned resources and valid credentials.
