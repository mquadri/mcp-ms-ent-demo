# Multi-Agent Orchestration — Scenario 3

This directory contains **Scenario 3: Multi-Agent Incident Remediation**, which demonstrates agent-to-agent handoff using the **Microsoft Semantic Kernel Agent Framework** with the **Handoff Orchestration** pattern.

## Architecture

```
                    ┌─────────────────────┐
                    │  HandoffOrchestrator │
                    │  (Semantic Kernel)   │
                    └──────────┬──────────┘
                               │
          ┌────────────────────┼────────────────────┐
          │                    │                    │
    ┌─────▼─────┐       ┌─────▼──────┐      ┌─────▼──────┐
    │  Triage   │──────►│ Diagnostics│─────►│ Remediation│
    │   Agent   │       │   Agent    │      │   Agent    │
    └─────┬─────┘       └─────┬──────┘      └─────┬──────┘
          │                   │                    │
    ┌─────▼─────┐       ┌─────▼──────┐      ┌─────▼──────┐
    │Azure MCP  │       │Azure MCP   │      │Azure MCP   │
    │(Monitor)  │       │(AppInsights│      │(DevOps API)│
    └───────────┘       │ LogAnalytics)     └────────────┘
                        └────────────┘
```

## Agents

| Agent | Role | MCP Tools Used | Hands Off To |
|-------|------|----------------|--------------|
| **TriageAgent** | Receives incident alert, classifies severity, determines blast radius | Azure MCP Server → `monitor_*` tools | DiagnosticsAgent |
| **DiagnosticsAgent** | Runs deep root-cause analysis; correlates logs, metrics, traces | Azure MCP Server → `applicationinsights_*`, `monitor_*` | RemediationAgent |
| **RemediationAgent** | Creates work items, proposes fix, assigns on-call engineer | Azure DevOps REST API, Enterprise MCP → Graph queries | (terminal) |

## Handoff Pattern

This scenario uses **Semantic Kernel Handoff Orchestration** — each agent can:

1. Process its portion of the task
2. Decide dynamically which agent should handle the next step
3. Pass full context (incident data, analysis results) to the next agent
4. Each agent has its own specialized system prompt, MCP tool access, and domain expertise

## Files

| File | Description |
|------|-------------|
| `incident_remediation.py` | Full Scenario 3 multi-agent orchestration |
| `agent_definitions.yaml` | Agent configs (system prompts, tools, handoff rules) |
| `README.md` | This file |

## Prerequisites

- Python 3.10+
- `semantic-kernel[agents]` package
- Azure OpenAI deployment (for agent LLM reasoning)
- Azure MCP Server running (`npx -y @azure/mcp@latest server start`)
- Microsoft MCP Server for Enterprise (for Graph queries)

## Usage

```bash
# From repo root
python agents/incident_remediation.py

# Or with a custom incident description
python agents/incident_remediation.py --incident "CheckoutService is returning 500 errors and database connections are timing out"
```

## References

- [Semantic Kernel Agent Orchestration](https://learn.microsoft.com/en-us/semantic-kernel/frameworks/agent/agent-orchestration/)
- [Handoff Orchestration Pattern](https://learn.microsoft.com/en-us/semantic-kernel/frameworks/agent/agent-orchestration/handoff)
- [Azure AI Agent Design Patterns](https://learn.microsoft.com/en-us/azure/architecture/ai-ml/guide/ai-agent-design-patterns)
- [Microsoft Agent Framework](https://github.com/microsoft/agent-framework)
