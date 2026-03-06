# MCP Server Configurations

This directory contains configuration templates for **official Microsoft MCP Servers** used in the demo scenarios.

## Files

| File | Description | Use With |
|------|-------------|----------|
| `copilot-enterprise-settings.json` | Full MCP server configuration (Azure MCP + Enterprise MCP) | Copilot / Any MCP Client |
| `vscode-mcp-settings.json` | VS Code-specific MCP config with input prompts | VS Code + GitHub Copilot |

## Official Microsoft MCP Servers

| Server | Endpoint / Package | Auth | Used In |
|--------|-------------------|------|---------|
| **Azure MCP Server** | `npx -y @azure/mcp@latest server start` | Entra ID / Azure Identity / RBAC | Scenario 1, 3, 5 |
| **MS Enterprise MCP** | `https://mcp.svc.cloud.microsoft/enterprise` | Delegated OAuth2 via VS Code | Scenario 1, 3 |

The Azure MCP Server is a **unified** server covering 50+ Azure services via tool namespaces: `monitor`, `cosmos`, `applicationinsights`, `keyvault`, `storage`, `appservice`, `functionapp`, `aks`, `role`, `deploy`, and more.

## Setup

### Option A: Copilot Enterprise / Generic MCP Client

1. Copy `copilot-enterprise-settings.json`
2. Replace `YOUR_SUBSCRIPTION_ID` and `YOUR_TENANT_ID` with your values
3. Apply to your MCP client's configuration

### Option B: VS Code + GitHub Copilot

1. Copy `vscode-mcp-settings.json` contents into your `.vscode/settings.json`
2. VS Code will prompt you for Subscription ID and Tenant ID on first use
3. For Enterprise MCP, use the [one-click install](https://vscode.dev/redirect/mcp/install?name=Microsoft%20MCP%20Server%20for%20Enterprise&config=%7b%22name%22:%22Microsoft%20MCP%20Server%20for%20Enterprise%22%2c%22type%22:%22http%22%2c%22url%22:%22https://mcp.svc.cloud.microsoft/enterprise%22%7d) (requires [tenant provisioning](../docs/DEMO_PLAN_REAL.md) first)

### Option C: Environment Variables

Set the values in your `.env` file (see `.env.example` in the repo root) and reference them in your MCP client config.

## Credential Requirements

### Azure MCP Server (all scenarios)

The Azure MCP Server uses **Entra ID / Azure Identity** — no keys or secrets needed. Ensure you are logged in:

```bash
az login
az account set --subscription YOUR_SUBSCRIPTION_ID
```

Required: `AZURE_SUBSCRIPTION_ID`, `AZURE_TENANT_ID`

### Enterprise MCP Server (Scenarios 1, 3)

Requires tenant provisioning (one-time):

```powershell
Install-Module Microsoft.Entra.Beta -Force -AllowClobber
Connect-Entra -Scopes 'Application.ReadWrite.All','Directory.Read.All','DelegatedPermissionGrant.ReadWrite.All'
Grant-EntraBetaMCPServerPermission -ApplicationName VisualStudioCode
```

### Scenario 3 — Multi-Agent (Semantic Kernel)

If running in real mode (`--real`), also requires:

- `AZURE_OPENAI_ENDPOINT` — Your Azure OpenAI endpoint
- `AZURE_OPENAI_DEPLOYMENT` — Deployment name (e.g., `gpt-4o`)

See the [demos/README.md](../demos/README.md) for full setup instructions.