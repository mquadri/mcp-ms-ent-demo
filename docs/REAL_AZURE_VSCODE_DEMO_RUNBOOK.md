# Real Azure VS Code Demo Runbook

This runbook is for the live Azure + VS Code version of the demo. It assumes the MCP and agent services are already deployed to Azure Container Apps.

## Deployed Endpoints

| Name | URL |
|---|---|
| Agents MCP | `https://agents-mcp.agreeablepond-fb125b6b.eastus.azurecontainerapps.io` |
| Agents app | `https://agents.agreeablepond-fb125b6b.eastus.azurecontainerapps.io` |
| Azure MCP internal | `https://azure-mcp.internal.agreeablepond-fb125b6b.eastus.azurecontainerapps.io` |

## VS Code MCP Configuration For The Demo

Use the workspace MCP config at `.github/mcp.json` for the live demo. This keeps the demo endpoints tied to this repo instead of relying only on your global VS Code user config.

Configured demo servers:

| Server name in VS Code | Type | Purpose |
|---|---|---|
| `demo-agents-mcp` | HTTP | Your deployed MCP endpoint in Azure Container Apps |
| `microsoft-enterprise-mcp` | HTTP | Microsoft Graph / Entra context |
| `azure-devops-mquadri` | stdio | Azure DevOps MCP for the demo organization |

The `azure-mcp.internal...` endpoint is intentionally not configured directly in VS Code because it is an internal Container Apps endpoint. It is reachable from services inside the Container Apps environment, not from your local laptop unless you add private network access, a tunnel, or public ingress.

If VS Code shows around 50 configured tools, that usually means the Azure MCP server is exposing many Azure tool namespaces. That is normal. For this demo, make sure the server list includes your custom `demo-agents-mcp` entry in addition to the standard Microsoft and Azure DevOps entries.

### Workspace MCP Config

The repo contains this config in `.github/mcp.json`:

```json
{
  "inputs": [],
  "servers": {
    "demo-agents-mcp": {
      "type": "http",
      "url": "https://agents-mcp.agreeablepond-fb125b6b.eastus.azurecontainerapps.io"
    },
    "microsoft-enterprise-mcp": {
      "type": "http",
      "url": "https://mcp.svc.cloud.microsoft/enterprise"
    },
    "azure-devops-mquadri": {
      "type": "stdio",
      "command": "npx",
      "args": ["-y", "@azure-devops/mcp", "mquadri-msmenv"]
    }
  }
}
```

After editing MCP config:

1. Reload VS Code.
2. Open Copilot Chat.
3. Switch to Agent mode.
4. Open MCP/server tools and confirm `demo-agents-mcp` is listed.
5. Ask Copilot to list the available MCP tools and use a read-only tool from `demo-agents-mcp`.

## Azure Environment

| Item | Value |
|---|---|
| Tenant display | `Contoso (MngEnv399036.onmicrosoft.com)` |
| Resource group | `rg-mcp-agent-stack` |
| Region | `East US` |
| Container Apps environment | `mcp-dev-env` |
| Environment type | `Consumption only` |
| Container Apps | `agents`, `agents-mcp`, `azure-mcp`, `infra-mcp`, `research-mcp` |

## Pre-Demo Checklist

Complete this before the session starts:

- Open this repo in VS Code.
- Open Copilot Chat in Agent mode.
- Confirm MCP endpoints are configured and reachable from the demo environment.
- Confirm Azure sign-in is the correct tenant and subscription.
- Confirm the Container Apps are running in `rg-mcp-agent-stack`.
- Confirm the deployed agent endpoint opens or returns a health response.
- Confirm the MCP endpoint is available to the client that will use it.
- Confirm Azure DevOps organization and project are reachable.
- Confirm any required PAT or identity-based DevOps access is valid.
- Keep `docs/architecture.drawio` ready for architecture explanation.
- Keep terminal open at the repo root.

## Smoke Tests

### Azure identity

```powershell
az account show
```

Expected result: the active subscription and tenant match the demo environment.

### Container Apps inventory

```powershell
az containerapp list --resource-group rg-mcp-agent-stack --query "[].{name:name, state:properties.runningStatus, fqdn:properties.configuration.ingress.fqdn}" -o table
```

Expected result: the app list includes `agents`, `agents-mcp`, `azure-mcp`, `infra-mcp`, and `research-mcp`.

### Agent endpoint

```powershell
Invoke-WebRequest -Uri "https://agents.agreeablepond-fb125b6b.eastus.azurecontainerapps.io" -Method Head
```

Expected result: HTTP response proves the deployed app endpoint is reachable.

### MCP endpoint

```powershell
Invoke-WebRequest -Uri "https://agents-mcp.agreeablepond-fb125b6b.eastus.azurecontainerapps.io" -Method Head
```

Expected result: HTTP response proves the MCP-facing endpoint is reachable.

### Python demo fallback

```powershell
python agents/incident_remediation.py
python agents/velocity_analysis.py
```

Expected result: both mock-mode demos run even if a live connector has an issue.

## Live Demo Flow

### Demo 1: Real Azure MCP from VS Code

Prompt:

```text
We have a production incident. Use the configured MCP tools to inspect current Azure service health, alerts, and relevant logs. Summarize the likely root cause, impacted resources, and recommended next step.
```

Narration:

The agent is using the MCP layer to get real operational context. This is the bridge from natural language to Azure systems.

### Demo 2: Incident To Work Item

Prompt:

```text
Create a severity 1 Azure DevOps bug from the incident summary. Include the impacted resources, timeline, evidence, root cause, recommended fix, and tags for incident, ai-generated, and mcp-demo.
```

Narration:

The output becomes operational work. The value is not only the summary; it is the handoff to the engineering system of record.

### Demo 3: Multi-Agent Handoff

Command:

```powershell
python agents/incident_remediation.py
```

Narration:

This demonstrates the handoff pattern. TriageAgent classifies the incident, DiagnosticsAgent identifies root cause, and RemediationAgent drives the next action.

### Demo 4: Sequential Velocity Pipeline

Command:

```powershell
python agents/velocity_analysis.py
```

Narration:

This demonstrates a fixed pipeline. Metrics are gathered, analyzed, and converted into recommendations.

## Backup Plan

If VS Code MCP is slow or unavailable:

1. Show the Azure Portal Container Apps view.
2. Open `docs/architecture.drawio`.
3. Run `python agents/incident_remediation.py`.
4. Run `python agents/velocity_analysis.py`.
5. Explain that the Python demos preserve the same orchestration patterns while avoiding live dependency risk.

## Success Criteria

- Audience sees the real Azure Container Apps deployment.
- Audience sees VS Code as the demo control plane.
- Audience understands MCP as the tool bridge.
- Audience understands Semantic Kernel as the orchestration layer.
- Audience sees at least one live agent/tool interaction and one fallback orchestration.
