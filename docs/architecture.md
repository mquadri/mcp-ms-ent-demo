# System Architecture

This document describes the real Azure + VS Code demo architecture for this repo. The diagrams are maintained as draw.io assets so they can be opened, edited, exported, and reused in slides.

## Editable Diagrams

- [architecture.drawio](architecture.drawio) - editable draw.io source with three pages:
  - `Real Azure MCP Demo`
  - `Scenario 3 Handoff`
  - `Scenario 5 Sequential`

To edit the diagrams, open `docs/architecture.drawio` in diagrams.net or the VS Code draw.io extension.

## Deployed Azure Container Apps

The real demo uses Azure Container Apps deployed in East US:

| Service | URL | Purpose |
|---|---|---|
| Agent MCP endpoint | `https://agents-mcp.agreeablepond-fb125b6b.eastus.azurecontainerapps.io/mcp` | MCP-facing endpoint for agent/tool integration |
| Agent app endpoint | `https://agents.agreeablepond-fb125b6b.eastus.azurecontainerapps.io` | Agent application endpoint |
| Azure MCP endpoint | `https://azure-mcp.internal.agreeablepond-fb125b6b.eastus.azurecontainerapps.io` | Internal Azure MCP endpoint inside the Container Apps environment |

The Azure Portal screenshot shows the relevant Container Apps in resource group `rg-mcp-agent-stack`, Container Apps environment `mcp-dev-env`, region `East US`:

- `agents`
- `agents-mcp`
- `azure-mcp`
- `infra-mcp`
- `research-mcp`

## High-Level Flow

1. Presenter uses VS Code and GitHub Copilot Chat in Agent mode.
2. Copilot connects to configured MCP endpoints.
3. The deployed agent/MCP services run in Azure Container Apps.
4. Azure MCP tools retrieve operational context from Azure services.
5. Enterprise/Graph tooling resolves users, teams, roles, and ownership.
6. The agent workflow creates or updates Azure DevOps work items.
7. Semantic Kernel orchestrates multi-agent handoff and sequential workflows.

## Conceptual Layers

| Layer | What the audience should understand | Demo evidence |
|---|---|---|
| User experience | The presenter asks for an outcome in natural language | VS Code Copilot Agent mode |
| Agent reasoning | The agent decomposes the task and selects tools | Copilot tool calls and terminal output |
| MCP tool layer | MCP standardizes access to enterprise systems | Azure MCP / agent MCP endpoints |
| Enterprise systems | Azure and Microsoft Graph provide real context | Alerts, logs, users, assignments |
| Orchestration | Semantic Kernel coordinates specialist agents | `incident_remediation.py`, `velocity_analysis.py` |

## Scenario 1: Single-Agent Incident Response

This flow demonstrates one agent using multiple tools:

1. Query Azure Monitor for active critical alerts.
2. Correlate logs through Azure MCP.
3. Create a severity 1 Azure DevOps work item.
4. Resolve the on-call owner through Graph/Enterprise context.
5. Assign the work item and summarize the incident.

Use this scenario to explain MCP as the bridge between an AI agent and enterprise tools.

## Scenario 3: Handoff Orchestration

This flow demonstrates Semantic Kernel handoff orchestration:

```text
TriageAgent -> DiagnosticsAgent -> RemediationAgent
```

Use this scenario to explain specialization:

- `TriageAgent` classifies severity and blast radius.
- `DiagnosticsAgent` correlates logs and identifies root cause.
- `RemediationAgent` creates or updates work, resolves owners, and summarizes next steps.

Handoff orchestration is best for investigative or non-linear workflows where the next best step depends on what the previous agent discovered.

## Scenario 5: Sequential Orchestration

This flow demonstrates Semantic Kernel sequential orchestration:

```text
MetricsCollectorAgent -> TrendAnalystAgent -> AdvisorAgent
```

Use this scenario to explain pipelines:

- `MetricsCollectorAgent` gathers sprint, repository, build, deployment, and historical trend data.
- `TrendAnalystAgent` analyzes trends, detects anomalies, and forecasts the next sprint.
- `AdvisorAgent` creates executive recommendations and assigns owners.

Sequential orchestration is best for analytics, reporting, and repeatable workflows where each stage feeds the next.

## Authentication And Trust Boundaries

| Component | Authentication / boundary |
|---|---|
| VS Code and Copilot | User-authenticated session |
| Azure MCP / Container Apps | Azure-hosted service boundary |
| Azure resources | Entra ID and Azure RBAC |
| Enterprise/Graph context | Delegated tenant permissions |
| Azure DevOps | PAT, Azure DevOps auth, or configured connector identity |
| Semantic Kernel agents | Application runtime plus Azure OpenAI configuration for real mode |

## Speaker Notes

For a mixed audience, keep the explanation at two levels:

- Business level: "The agent turns an incident signal into assigned engineering work."
- Technical level: "The agent selects MCP tools, retrieves real cloud context, and Semantic Kernel coordinates specialist agents."
