# Microsoft Enterprise MCP Servers

A collection of resources for working with **official Microsoft MCP Servers** and the **Microsoft Semantic Kernel Agent Framework**. This repository contains configuration files, demo scenarios (including a multi-agent handoff demo), and sample prompts to help you integrate AI agents (GitHub Copilot, VS Code, and other MCP clients) with Microsoft cloud services through the [Model Context Protocol (MCP)](https://modelcontextprotocol.io/).

## What are Microsoft Enterprise MCP Servers?

Microsoft provides two official MCP servers that expose Azure and Microsoft 365 services as tools AI agents can call:

1. **[Azure MCP Server](https://learn.microsoft.com/en-us/azure/developer/azure-mcp-server/)** — A unified MCP server covering 50+ Azure services (Monitor, Cosmos DB, Application Insights, Key Vault, Storage, App Service, Functions, AKS, RBAC, Deploy, and more). Package: `@azure/mcp` (npm) / `Azure.Mcp` (NuGet) / `msmcp-azure` (PyPI).
2. **[Microsoft MCP Server for Enterprise](https://learn.microsoft.com/en-us/graph/mcp-server/overview)** — A hosted MCP server for Microsoft Graph and Entra ID queries, powered by RAG over 500+ API examples. Endpoint: `https://mcp.svc.cloud.microsoft/enterprise`.

This repo also demonstrates the **Microsoft Semantic Kernel Agent Framework** — specifically the [Handoff Orchestration](https://learn.microsoft.com/en-us/semantic-kernel/frameworks/agent/agent-orchestration/handoff) pattern — where multiple specialized agents collaborate by handing off context to each other.

## Repository Structure

```
.
├── README.md                                # This file
├── .env.example                             # Environment variables template
├── .gitignore                               # Git ignore rules
├── Contribution.md                          # Contributing guidelines
├── agents/
│   ├── README.md                            # Multi-agent architecture guide
│   ├── agent_definitions.yaml               # Agent configs (prompts, tools, handoffs)
│   └── incident_remediation.py              # Scenario 3 — Handoff orchestration
├── configuration/
│   ├── README.md                            # Configuration guide
│   ├── copilot-enterprise-settings.json     # Full MCP server configuration
│   └── vscode-mcp-settings.json             # VS Code-specific MCP config
├── demos/
│   ├── README.md                            # Full setup guide & scenario catalog
│   ├── requirements.txt                     # Python dependencies
│   ├── mock_data_generator.py               # Mock data generation utility
│   ├── setup_scenario_1.py                  # Setup data for Scenario 1
│   ├── setup_scenario_3.py                  # Setup data for Scenario 3
│   ├── setup_scenario_5.py                  # Setup data for Scenario 5
│   ├── demo_prep.ps1                        # One-script demo provisioning
│   └── SETUP_SUMMARY.md                     # Setup summary
├── docs/
│   ├── architecture.md                      # System architecture
│   └── DEMO_PLAN_REAL.md                    # 🔴 Real demo plan (Open Mic Friday)
└── prompts/
    └── getting-started.md                   # Sample prompts across all scenarios
```

## Official Microsoft MCP Servers

This repo uses **only** official Microsoft MCP servers — no third-party or fictitious packages.

| Server | Package / Endpoint | Description | Auth |
|--------|-------------------|-------------|------|
| **[Azure MCP Server](https://learn.microsoft.com/en-us/azure/developer/azure-mcp-server/)** | `npx -y @azure/mcp@latest server start` | Unified server: Azure Monitor, Cosmos DB, App Insights, Key Vault, Storage, App Service, Functions, AKS, RBAC, Deploy, Event Grid, Service Bus, AI Search, and more | Entra ID / Azure Identity / RBAC |
| **[MS Enterprise MCP](https://learn.microsoft.com/en-us/graph/mcp-server/overview)** | `https://mcp.svc.cloud.microsoft/enterprise` | Microsoft Graph & Entra ID queries via RAG — users, groups, apps, roles, PIM, compliance | Delegated (OAuth2 via VS Code) |

### Azure MCP Server Tool Namespaces

The Azure MCP Server exposes tools organized by namespace. Configure which namespaces to enable:

`monitor` · `cosmos` · `applicationinsights` · `keyvault` · `storage` · `appservice` · `functionapp` · `aks` · `role` · `advisor` · `deploy` · `eventgrid` · `eventhubs` · `servicebus` · `search` · `sql` · `postgres` · `mysql` · `redis` · `loadtesting` · `grafana` · `workbooks` · `bicepschema` · `resourcehealth` · `quota`

## Prerequisites

- **Azure Subscription** with the relevant services provisioned
- **Azure CLI** installed and authenticated:
  ```bash
  az login
  az account set --subscription YOUR_SUBSCRIPTION_ID
  ```
- **Node.js 18+** (for Azure MCP Server via `npx`)
- **Python 3.10+** (for demo setup scripts and Semantic Kernel agents)
- **Git**

### Required Azure Resources by Scenario

| Resource | Scenario 1 | Scenario 3 | Scenario 5 |
|----------|:----------:|:----------:|:----------:|
| Log Analytics Workspace | ✅ | ✅ | ✅ |
| Azure DevOps Organization + Project | ✅ | ✅ | ✅ |
| Cosmos DB Account | | | ✅ |
| Azure OpenAI Deployment | | ✅ (for real SK agents) | |
| Enterprise MCP Tenant Registration | | ✅ | |

> **Mock mode**: All setup scripts support `USE_MOCK_DATA=true` (the default) which requires **no Azure credentials**. This is ideal for exploring the scenarios locally.

## Configuration

The [configuration/](configuration/) directory provides ready-to-use templates for configuring MCP servers.

**For VS Code + GitHub Copilot**: Copy the contents of `configuration/vscode-mcp-settings.json` into your `.vscode/settings.json`.

**For other MCP clients**: Use `configuration/copilot-enterprise-settings.json` and replace the `YOUR_*` placeholders.

### Quick Configuration

```json
{
  "mcpServers": {
    "azure-mcp-server": {
      "command": "npx",
      "args": ["-y", "@azure/mcp@latest", "server", "start"],
      "env": {
        "AZURE_SUBSCRIPTION_ID": "YOUR_SUBSCRIPTION_ID",
        "AZURE_TENANT_ID": "YOUR_TENANT_ID"
      }
    }
  }
}
```

To add the Microsoft Enterprise MCP Server, use the [one-click install link](https://vscode.dev/redirect/mcp/install?name=Microsoft%20MCP%20Server%20for%20Enterprise&config=%7b%22name%22:%22Microsoft%20MCP%20Server%20for%20Enterprise%22%2c%22type%22:%22http%22%2c%22url%22:%22https://mcp.svc.cloud.microsoft/enterprise%22%7d) (requires [tenant provisioning](docs/DEMO_PLAN_REAL.md) first).

See [configuration/README.md](configuration/README.md) for full details.

## Demo Scenarios

| # | Scenario | Pattern | MCP Servers / Frameworks |
|---|----------|---------|--------------------------|
| **1** | Automated Incident Response | Single-agent, multi-tool | Azure MCP Server (monitor), Enterprise MCP (Graph) |
| **3** | Multi-Agent Incident Remediation | **Handoff Orchestration** (Semantic Kernel) | Azure MCP Server + Enterprise MCP + SK Agent Framework |
| **5** | Development Velocity Analysis | Single-agent, multi-tool | Azure MCP Server (monitor, cosmos, appinsights) |

### Quick Start (3 Steps)

```bash
# 1. Clone and enter the repo
git clone https://github.com/mquadri/mcp-ms-ent-demo.git
cd mcp-ms-ent-demo

# 2. Install Python dependencies
python -m venv mcp_env
mcp_env\Scripts\activate        # Windows
# source mcp_env/bin/activate   # macOS/Linux
pip install -r demos/requirements.txt

# 3. Run any scenario (mock mode by default)
python demos/setup_scenario_1.py
python demos/setup_scenario_3.py   # Seeds multi-agent data
python demos/setup_scenario_5.py

# Run the multi-agent orchestration
python agents/incident_remediation.py
```

See the full setup guide and prompt catalog in [demos/README.md](demos/README.md).

### Scenario 3: Multi-Agent Handoff (Agent-to-Agent)

Scenario 3 demonstrates the **Semantic Kernel Handoff Orchestration** pattern where three specialized agents collaborate:

```
TriageAgent → DiagnosticsAgent → RemediationAgent
```

Each agent has its own system prompt, tool access, and domain expertise. Agents dynamically decide when to hand off to the next specialist. This uses the **Microsoft Agent Framework** patterns documented in the [Azure Architecture Center](https://learn.microsoft.com/en-us/azure/architecture/ai-ml/guide/ai-agent-design-patterns).

See [agents/README.md](agents/README.md) for the full multi-agent architecture.

### Running a Real Demo

For a live demo with your real Azure environment, see the **[Real Demo Plan](docs/DEMO_PLAN_REAL.md)** which covers:

1. **Tenant provisioning** — Register the [Microsoft MCP Server for Enterprise](https://learn.microsoft.com/en-us/graph/mcp-server/overview) in your Entra tenant
2. **Azure resource creation** — Log Analytics, Cosmos DB, Azure DevOps project
3. **Azure MCP Server setup** — `npx -y @azure/mcp@latest server start`
4. **Data seeding** — Run `demos/demo_prep.ps1` to provision everything
5. **Multi-agent demo** — Run `agents/incident_remediation.py --real` with Azure OpenAI
6. **Demo runbook** — Exact prompts and talking points for each scenario

## Getting Started Prompts

The [prompts/getting-started.md](prompts/getting-started.md) file contains natural language queries that demonstrate MCP orchestration across:

- 🚨 **Incident Response** (Scenario 1) — Alert triage, log correlation, ticket creation
- 🤖 **Multi-Agent Handoff** (Scenario 3) — Agent-to-agent collaboration for end-to-end incident remediation
- 📊 **Velocity Analytics** (Scenario 5) — Sprint metrics, build health, trend forecasting
- 🔄 **Cross-Scenario** — Correlating incidents with velocity impact

## Microsoft Frameworks Used

| Framework | Purpose | Docs |
|-----------|---------|------|
| **Azure MCP Server** | Unified MCP server for 50+ Azure services | [learn.microsoft.com](https://learn.microsoft.com/en-us/azure/developer/azure-mcp-server/) |
| **MS Enterprise MCP Server** | Microsoft Graph / Entra ID via MCP | [learn.microsoft.com](https://learn.microsoft.com/en-us/graph/mcp-server/overview) |
| **Semantic Kernel Agent Framework** | Handoff orchestration for multi-agent scenarios | [learn.microsoft.com](https://learn.microsoft.com/en-us/semantic-kernel/frameworks/agent/agent-orchestration/) |
| **Azure Architecture — AI Agent Patterns** | Design patterns: Sequential, Concurrent, Handoff, Group Chat | [learn.microsoft.com](https://learn.microsoft.com/en-us/azure/architecture/ai-ml/guide/ai-agent-design-patterns) |

## Comparison with Google MCP Servers

This repo is the Microsoft counterpart to [rominirani/google-mcp-servers](https://github.com/rominirani/google-mcp-servers), which demonstrates Google Cloud MCP integrations (BigQuery, Firestore, Cloud Logging, etc.) with Gemini CLI.

| Aspect | This Repo (Microsoft) | Google MCP Servers |
|--------|----------------------|-------------------|
| AI Agent | GitHub Copilot / VS Code | Gemini CLI |
| MCP Server | Azure MCP Server (unified, 50+ services) | Individual Google Cloud MCP servers |
| Monitoring | Azure Monitor / App Insights / Log Analytics | Cloud Logging / Cloud Monitoring |
| Identity | Enterprise MCP (Graph / Entra ID) | — |
| Database | Cosmos DB (via Azure MCP) | Firestore, BigQuery |
| Multi-Agent | Semantic Kernel Handoff Orchestration | — |
| Auth | Entra ID / Azure Identity / RBAC | Google Credentials / API Keys |

## Contributing

Contributions are welcome! See [Contribution.md](Contribution.md) for guidelines.

## License

Apache License 2.0