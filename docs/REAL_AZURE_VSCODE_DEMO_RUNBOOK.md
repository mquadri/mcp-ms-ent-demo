# Real Azure VS Code Demo Runbook

This runbook is for the live Azure + VS Code version of the demo. It assumes the MCP and agent services are already deployed to Azure Container Apps.

## Deployed Endpoints

| Name | URL |
|---|---|
| Agents MCP | `https://agents-mcp.agreeablepond-fb125b6b.eastus.azurecontainerapps.io/mcp` |
| Agents app | `https://agents.agreeablepond-fb125b6b.eastus.azurecontainerapps.io` |
| Azure MCP internal | `https://azure-mcp.internal.agreeablepond-fb125b6b.eastus.azurecontainerapps.io` |

## VS Code MCP Configuration For The Demo

Use the workspace MCP config at `.github/mcp.json` for the live demo. This keeps the demo endpoints tied to this repo instead of relying only on your global VS Code user config.

Configured demo servers:

| Server name in VS Code | Type | Purpose |
|---|---|---|
| `demo-agents-mcp` | HTTP | Your deployed MCP endpoint in Azure Container Apps at `/mcp` |
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
      "url": "https://agents-mcp.agreeablepond-fb125b6b.eastus.azurecontainerapps.io/mcp"
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

## Demo: Show The Deployed MCP Agent In VS Code

Use this section when `demo-agents-mcp` is connected in VS Code Agent mode.

Expected server status:

| MCP server | Status | Tools exposed |
|---|---|---|
| `demo-agents-mcp` | Connected | `demo-agents-mcp-agent_health`, `demo-agents-mcp-ask_agent`, `demo-agents-mcp-ask_agent_stream` |

### Step 1: Show The Connected MCP Server

In VS Code:

1. Open Copilot Chat.
2. Switch to Agent mode.
3. Select Configure Tools.
4. Show `demo-agents-mcp`.
5. Show the exposed tools:
   - `demo-agents-mcp-agent_health`
   - `demo-agents-mcp-ask_agent`
   - `demo-agents-mcp-ask_agent_stream`

Talk track:

```text
This proves Copilot is connected to my deployed MCP server running in Azure Container Apps. The agent tools are not local mock functions; they are exposed by the deployed demo MCP endpoint.
```

### Step 2: Confirm Agent Health

Prompt in Copilot Agent mode:

```text
Use demo-agents-mcp-agent_health to check whether the deployed agent service is healthy. Summarize the result.
```

Talk track:

```text
I am starting with a health check because it proves the path from VS Code to the deployed MCP server is working before I ask the agent to do anything more complex.
```

What to show:

- Copilot selects the `agent_health` tool.
- The response indicates the deployed agent service is reachable.
- The status can be summarized in plain English for the audience.

### Step 3: Ask What The Agent Can Do

Prompt in Copilot Agent mode:

```text
Use demo-agents-mcp-ask_agent to ask the deployed agent: What capabilities are available in this MCP demo environment?
```

Talk track:

```text
Now Copilot is not answering by itself. It is calling my deployed MCP agent endpoint and asking the agent service what it can do.
```

What to show:

- The `ask_agent` tool call.
- A capability summary from the deployed agent.
- The difference between Copilot as the user interface and the deployed agent as the backend capability.

### Step 4: Run The Incident Triage Demo

Prompt in Copilot Agent mode:

```text
Use demo-agents-mcp-ask_agent to ask the deployed agent to investigate a production incident: CheckoutService is returning 500 errors and database connections are timing out. Ask it to identify likely root cause, impacted resources, and recommended remediation steps.
```

Talk track:

```text
This is the core workflow. I give the system an incident in natural language. Copilot routes the request through MCP to the deployed agent service, and the agent produces an operational triage summary.
```

What to show:

- Root cause or likely root cause.
- Impacted service or resources.
- Recommended remediation steps.
- Any evidence or assumptions the agent includes.

### Step 5: Use Streaming For A More Visual Demo

Prompt in Copilot Agent mode:

```text
Use demo-agents-mcp-ask_agent_stream to ask the deployed agent for a step-by-step incident triage plan for CheckoutService database timeout errors.
```

Talk track:

```text
The streaming tool is useful in a live demo because the audience can watch the agent produce the answer step by step instead of waiting for one final response.
```

What to show:

- The streamed response.
- The agent's triage sequence.
- How the response becomes easier to follow during a live presentation.

### Step 6: Generate An Azure DevOps-Ready Bug Summary

Prompt in Copilot Agent mode:

```text
Use demo-agents-mcp-ask_agent to create an Azure DevOps-ready bug summary for this incident. Include title, severity, description, root cause, evidence, acceptance criteria, tags, and recommended owner. Do not actually create the work item yet.
```

Talk track:

```text
This turns investigation into execution-ready work. I am asking for an Azure DevOps-ready bug summary, but I am explicitly saying not to create the work item yet. That keeps the demo safe while still showing the business value.
```

What to show:

- A clear title.
- Severity.
- Description.
- Root cause.
- Evidence.
- Acceptance criteria.
- Tags.
- Recommended owner.

### Step 7: Connect The Demo Back To The Repo

Open these files in VS Code:

- `docs/architecture.md`
- `docs/architecture.drawio`
- `agents/agent_definitions.yaml`
- `agents/incident_remediation.py`

Talk track:

```text
What we just saw in Copilot is the deployed version of this architecture. The repo documents the same pattern: VS Code is the control plane, MCP is the tool bridge, the deployed agent service handles the backend capability, and Semantic Kernel-style orchestration gives us repeatable agent workflows.
```

### Short Version For A Live Demo

If time is tight, run only these four prompts:

```text
Use demo-agents-mcp-agent_health to check whether the deployed agent service is healthy. Summarize the result.
```

```text
Use demo-agents-mcp-ask_agent to ask the deployed agent: What capabilities are available in this MCP demo environment?
```

```text
Use demo-agents-mcp-ask_agent to ask the deployed agent to investigate a production incident: CheckoutService is returning 500 errors and database connections are timing out. Ask it to identify likely root cause, impacted resources, and recommended remediation steps.
```

```text
Use demo-agents-mcp-ask_agent to create an Azure DevOps-ready bug summary for this incident. Include title, severity, description, root cause, evidence, acceptance criteria, tags, and recommended owner. Do not actually create the work item yet.
```

Closing line:

```text
Running containers prove the services exist. The connected MCP server proves VS Code can reach the deployed tool layer. The Copilot tool calls prove the agent workflow is actually usable from Agent mode.
```

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
Invoke-WebRequest -Uri "https://agents-mcp.agreeablepond-fb125b6b.eastus.azurecontainerapps.io/mcp" -Method Head
```

Expected result: an HTTP response proves the MCP-facing endpoint is reachable. A normal browser-style request can return `406` on `/mcp`; that still proves the route exists. VS Code performs the actual MCP handshake with the correct headers.

## Troubleshooting: SSE 404 During MCP Handshake

Symptom:

```text
Connection state: Error 404 status connecting ... as SSE: Not Found
Endpoint involved: https://agents-mcp.agreeablepond-fb125b6b.eastus.azurecontainerapps.io/
```

Likely cause:

The service health endpoint is healthy, but the MCP client is negotiating against the wrong transport URL. The base `/` path returns `404`; the MCP transport endpoint is `/mcp`.

Correct VS Code configuration:

```json
{
  "servers": {
    "demo-agents-mcp": {
      "type": "http",
      "url": "https://agents-mcp.agreeablepond-fb125b6b.eastus.azurecontainerapps.io/mcp"
    }
  }
}
```

If VS Code logs still show the base `/` endpoint after the config uses `/mcp`, do this:

1. Run `MCP: List Servers`.
2. Stop `demo-agents-mcp`.
3. Open `MCP: Open Workspace Folder Configuration`.
4. Confirm the URL ends with `/mcp`.
5. Check the user config at `%APPDATA%\Code\User\mcp.json` and remove any old `demo-agents-mcp` entry that points to the base URL.
6. Run `Developer: Reload Window`.
7. Run `MCP: List Servers` again.
8. Start `demo-agents-mcp`.
9. Confirm the logs now reference `/mcp`, not `/`.

Validation commands:

```powershell
$base = "https://agents-mcp.agreeablepond-fb125b6b.eastus.azurecontainerapps.io"
Invoke-WebRequest -Uri "$base/" -Method Get -SkipHttpErrorCheck
Invoke-WebRequest -Uri "$base/mcp" -Method Get -SkipHttpErrorCheck
```

Expected validation pattern:

| Path | Expected result | Meaning |
|---|---|---|
| `/` | `404` | Base route is not an MCP transport endpoint |
| `/mcp` | `406` or MCP handshake response | MCP route exists; plain GET may not be accepted |

Runbook note:

Health checks and MCP handshakes are different. A healthy service can still fail MCP negotiation if the client is configured to the wrong path or transport.

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
