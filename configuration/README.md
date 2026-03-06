# MCP Server Configurations

This directory contains configuration templates for Microsoft Enterprise MCP Servers used in the demo scenarios.

## Files

| File | Description | Use With |
|------|-------------|----------|
| `copilot-enterprise-settings.json` | Full MCP server configuration with all 4 servers | Copilot / Any MCP Client |
| `vscode-mcp-settings.json` | VS Code-specific MCP config with input prompts | VS Code + GitHub Copilot |

## Available MCP Servers

| Server | Endpoint | Auth | Used In |
|--------|----------|------|---------|
| Azure Monitor | `@azure/mcp-server-monitor` | Azure Identity / Managed Identity | Scenario 1, 5 |
| Azure DevOps | `@azure/mcp-server-devops` | Personal Access Token (PAT) | Scenario 1, 5 |
| Microsoft Graph | `@azure/mcp-server-graph` | OAuth2 (Client Credentials) | Scenario 1 |
| Azure Cosmos DB | `@azure/mcp-server-cosmos` | Cosmos DB Key / Azure Identity | Scenario 5 |

## Setup

### Option A: Copilot Enterprise / Generic MCP Client

1. Copy `copilot-enterprise-settings.json`
2. Replace all `YOUR_*` placeholder values with your actual credentials
3. Apply to your MCP client's configuration

### Option B: VS Code + GitHub Copilot

1. Copy `vscode-mcp-settings.json` contents into your `.vscode/settings.json`
2. VS Code will prompt you for each credential value on first use
3. Secrets (PAT, client secret, Cosmos key) are masked in the prompt

### Option C: Environment Variables

Set the values in your `.env` file (see `.env.example` in the repo root) and reference them in your MCP client config.

## Credential Requirements by Scenario

### Scenario 1: Automated Incident Response
- `AZURE_SUBSCRIPTION_ID` + `LOG_ANALYTICS_WORKSPACE_ID` — for Azure Monitor
- `AZURE_DEVOPS_ORG_URL` + `AZURE_DEVOPS_PAT` — for Azure DevOps
- `AZURE_TENANT_ID` + `AZURE_CLIENT_ID` + `AZURE_CLIENT_SECRET` — for Microsoft Graph

### Scenario 5: Development Velocity Analysis
- `AZURE_DEVOPS_ORG_URL` + `AZURE_DEVOPS_PAT` — for Azure DevOps
- `AZURE_SUBSCRIPTION_ID` + `LOG_ANALYTICS_WORKSPACE_ID` — for Azure Monitor
- `COSMOS_DB_ENDPOINT` + `COSMOS_DB_KEY` — for Cosmos DB

See the [demos/README.md](../demos/README.md) for full setup instructions.