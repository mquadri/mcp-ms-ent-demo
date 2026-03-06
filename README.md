# Microsoft Enterprise MCP Servers

A collection of resources for working with **Microsoft Enterprise MCP Servers**. This repository contains configuration files, demo scenarios, and sample prompts to help you integrate AI agents (GitHub Copilot, VS Code, and other MCP clients) with Microsoft cloud services through the [Model Context Protocol (MCP)](https://modelcontextprotocol.io/).

## What are Microsoft Enterprise MCP Servers?

Microsoft Enterprise MCP Servers expose Azure and Microsoft 365 services as tools that AI agents can call. Using MCP, you can give AI agents the ability to query Azure Monitor alerts, create Azure DevOps work items, look up users in Microsoft Graph, read Cosmos DB documents, and more — all from natural language prompts.

## Repository Structure

```
.
├── README.md                                # This file
├── .env.example                             # Environment variables template
├── .gitignore                               # Git ignore rules
├── Contribution.md                          # Contributing guidelines
├── configuration/
│   ├── README.md                            # Configuration guide
│   ├── copilot-enterprise-settings.json     # Full MCP server configuration
│   └── vscode-mcp-settings.json             # VS Code-specific MCP config
├── demos/
│   ├── README.md                            # Full setup guide & scenario catalog
│   ├── requirements.txt                     # Python dependencies
│   ├── mock_data_generator.py               # Mock data generation utility
│   ├── scenario_1_inject.ps1                # Inject sample logs (Scenario 1)
│   ├── setup_scenario_1.py                  # Setup data for Scenario 1
│   ├── setup_scenario_5.py                  # Setup data for Scenario 5
│   └── SETUP_SUMMARY.md                     # Setup summary
├── docs/
│   └── architecture.md                      # System architecture
└── prompts/
    └── getting-started.md                   # 10 sample prompts across scenarios
```

## Available MCP Servers

| Server | Description | Auth |
|--------|-------------|------|
| **Azure Monitor** | Query alerts, error logs, performance metrics, Log Analytics | Azure Identity / Managed Identity |
| **Azure DevOps** | Create/update work items, query sprints, repo stats, build pipelines | Personal Access Token (PAT) |
| **Microsoft Graph** | User info, team lookups, org hierarchy, Teams notifications | OAuth2 (Client Credentials) |
| **Azure Cosmos DB** | Query documents, read/write items, list databases/containers | Cosmos DB Key / Azure Identity |

## Prerequisites

- **Azure Subscription** with the relevant services provisioned
- **Azure CLI** installed and authenticated:
  ```bash
  az login
  az account set --subscription YOUR_SUBSCRIPTION_ID
  ```
- **Node.js 18+** (for MCP server packages via `npx`)
- **Python 3.9+** (for demo setup scripts)
- **Git**

### Required Azure Resources by Scenario

| Resource | Scenario 1 | Scenario 5 |
|----------|:----------:|:----------:|
| Log Analytics Workspace | ✅ | ✅ |
| Azure DevOps Organization + Project | ✅ | ✅ |
| Azure AD App Registration (Graph) | ✅ | |
| Cosmos DB Account | | ✅ |

> **Mock mode**: All setup scripts support `USE_MOCK_DATA=true` (the default) which requires **no Azure credentials**. This is ideal for exploring the scenarios locally.

## Configuration

The [configuration/](configuration/) directory provides ready-to-use templates for configuring MCP servers.

**For VS Code + GitHub Copilot**: Copy the contents of `configuration/vscode-mcp-settings.json` into your `.vscode/settings.json`.

**For other MCP clients**: Use `configuration/copilot-enterprise-settings.json` and replace the `YOUR_*` placeholders.

### Quick Configuration

```json
{
  "mcpServers": {
    "azure-monitor": {
      "command": "npx",
      "args": ["-y", "@azure/mcp-server-monitor"],
      "env": {
        "AZURE_SUBSCRIPTION_ID": "YOUR_SUBSCRIPTION_ID",
        "LOG_ANALYTICS_WORKSPACE_ID": "YOUR_WORKSPACE_ID"
      }
    },
    "azure-devops": {
      "command": "npx",
      "args": ["-y", "@azure/mcp-server-devops"],
      "env": {
        "AZURE_DEVOPS_ORG_URL": "https://dev.azure.com/YOUR_ORG",
        "AZURE_DEVOPS_PROJECT": "YOUR_PROJECT",
        "AZURE_DEVOPS_PAT": "YOUR_PAT"
      }
    }
  }
}
```

See [configuration/README.md](configuration/README.md) for full details.

## Demo Scenarios

| # | Scenario | MCP Servers Used |
|---|----------|-----------------|
| **1** | Automated Incident Response | Azure Monitor, Azure DevOps, Microsoft Graph |
| **5** | Development Velocity Analysis | Azure DevOps, Azure Monitor, Cosmos DB |

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

# 3. Run a scenario (mock mode by default)
python demos/setup_scenario_1.py
python demos/setup_scenario_5.py
```

See the full setup guide and prompt catalog in [demos/README.md](demos/README.md).

## Getting Started Prompts

The [prompts/getting-started.md](prompts/getting-started.md) file contains 10 natural language queries that demonstrate multi-tool MCP orchestration across:

- 🚨 **Incident Response** — Alert triage, log correlation, ticket creation, on-call assignment
- 📊 **Velocity Analytics** — Sprint metrics, build health, deployment cadence, trend forecasting
- 🔄 **Cross-Scenario** — Correlating incidents with velocity impact

## Comparison with Google MCP Servers

This repo is the Microsoft counterpart to [rominirani/google-mcp-servers](https://github.com/rominirani/google-mcp-servers), which demonstrates Google Cloud MCP integrations (BigQuery, Firestore, Cloud Logging, etc.) with Gemini CLI.

| Aspect | This Repo (Microsoft) | Google MCP Servers |
|--------|----------------------|-------------------|
| AI Agent | GitHub Copilot / VS Code | Gemini CLI |
| Monitoring | Azure Monitor / Log Analytics | Cloud Logging / Cloud Monitoring |
| Work Tracking | Azure DevOps | — |
| Identity | Microsoft Graph | — |
| Database | Cosmos DB | Firestore, BigQuery |
| Auth | Azure Identity, PAT, OAuth2 | Google Credentials, API Keys |

## Contributing

Contributions are welcome! See [Contribution.md](Contribution.md) for guidelines.

## License

Apache License 2.0