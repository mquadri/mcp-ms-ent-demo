# Quick Start: Technical Session Review Demo

This guide is designed for a high-impact technical demo of the **Microsoft Enterprise MCP Servers**. It focuses on getting the environment ready in under 5 minutes using **Mock Mode** (no Azure credentials required) while providing the path for **Real Mode**.

---

## 🚀 One-Minute Setup (Mock Mode)

Mock mode allows you to demonstrate the full multi-agent orchestration without needing live Azure resources.

```bash
# 1. Clone the repo (if not already done)
git clone https://github.com/mquadri/mcp-ms-ent-demo.git
cd mcp-ms-ent-demo

# 2. Create and activate a Python environment
python -m venv mcp_env
# Windows:
mcp_env\Scripts\activate
# macOS/Linux:
# source mcp_env/bin/activate

# 3. Install dependencies
pip install -r demos/requirements.txt

# 4. Initialize mock data
python demos/setup_scenario_1.py
python demos/setup_scenario_3.py
python demos/setup_scenario_5.py
```

---

## 💻 VS Code Configuration

To demo the **Azure MCP Server** and **Enterprise MCP Server** inside VS Code:

1. **Install GitHub Copilot Extension**: Ensure you have the GitHub Copilot and GitHub Copilot Chat extensions installed.
2. **Open Settings (JSON)**: `Ctrl+Shift+P` -> `Preferences: Open User Settings (JSON)`.
3. **Add MCP Servers**: Copy the content from `configuration/vscode-mcp-settings.json` into your settings.
   - *Note: In Mock Mode, the VS Code extension will still try to connect to the MCP server. For a UI-only demo of Copilot Chat, you can simply show the configuration.*
4. **Enable Agent Mode**: Open Copilot Chat and ensure "Agent Mode" is active to see the MCP tool icons.

---

## 🏃‍♂️ Executing the Modules

### Scenario 1: Single Agent (Copilot Chat)
Open Copilot Chat and ask:
> "Fetch all active critical alerts from Azure Monitor for the contoso-monitoring resource group. Summarize the incident and identify the on-call engineer via Graph."

### Scenario 3: Multi-Agent Handoff (The "Star" of the Demo)
This demonstrates specialized agents (Triage → Diagnostics → Remediation) collaborating.
```bash
python agents/incident_remediation.py
```

### Scenario 5: Sequential Pipeline (Analytics)
This demonstrates a fixed data pipeline (Collector → Analyst → Advisor).
```bash
python agents/velocity_analysis.py
```

---

## 🔍 Environment Health Check

Run this utility to ensure your demo environment is ready:
```bash
python demos/demo_health_check.py
```

---

## 💡 Key Talking Points for your Review

1. **Model Context Protocol (MCP)**: Explain that MCP is an open standard that allows AI models to safely access local and remote tools/data.
2. **Official Servers**: Emphasize these use the **official** Microsoft Azure and Enterprise MCP servers.
3. **Orchestration Patterns**: Highlight the difference between **Handoff** (dynamic) and **Sequential** (fixed) patterns in Semantic Kernel.
4. **Mock vs Real**: Mention that the entire demo can run against real Azure resources by setting `USE_MOCK_DATA=false` in `.env`.
