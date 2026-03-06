# Multi-Agent Orchestration

This directory contains two multi-agent scenarios demonstrating **different** orchestration patterns from the **Microsoft Semantic Kernel Agent Framework**:

| Scenario | Pattern | Agents | Script |
|----------|---------|--------|--------|
| **3** — Incident Remediation | **Handoff** (agents decide when to hand off) | TriageAgent → DiagnosticsAgent → RemediationAgent | `incident_remediation.py` |
| **5** — Velocity Analysis | **Sequential** (fixed pipeline order) | MetricsCollectorAgent → TrendAnalystAgent → AdvisorAgent | `velocity_analysis.py` |

---

## Scenario 3: Handoff Orchestration — Incident Remediation

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
    │Azure MCP  │       │Azure MCP   │      │Enterprise  │
    │(monitor)  │       │(appinsights│      │MCP (Graph) │
    └───────────┘       │ monitor)   │      │+ DevOps API│
                        └────────────┘      └────────────┘
```

**Key**: Agents *dynamically decide* when to hand off. DiagnosticsAgent can escalate back to TriageAgent if more data is needed.

| Agent | Role | MCP Tools | Hands Off To |
|-------|------|-----------|------|
| **TriageAgent** | Classifies severity, determines blast radius | Azure MCP Server → `monitor`, `resourcehealth` | DiagnosticsAgent |
| **DiagnosticsAgent** | Root-cause analysis via logs & traces | Azure MCP Server → `applicationinsights`, `monitor`, `kusto` | RemediationAgent (or back to TriageAgent) |
| **RemediationAgent** | Creates work items, assigns on-call | Enterprise MCP → Graph, Azure DevOps REST API | (terminal) |

```bash
# Mock mode
python agents/incident_remediation.py

# Custom incident
python agents/incident_remediation.py --incident "PaymentGateway is returning 503 errors"

# Real mode (requires Azure OpenAI)
python agents/incident_remediation.py --real
```

---

## Scenario 5: Sequential Orchestration — Velocity Analysis

```
                  ┌───────────────────────────┐
                  │  SequentialOrchestrator    │
                  │  (Semantic Kernel)         │
                  └─────────────┬─────────────┘
                                │
         ┌──────────────────────┼─────────────────────┐
         │                      │                     │
   ┌─────▼──────┐        ┌──────▼──────┐       ┌──────▼──────┐
   │  Metrics   │───────►│   Trend     │──────►│  Advisor    │
   │ Collector  │        │  Analyst    │       │   Agent     │
   │   Agent    │        │   Agent     │       │             │
   └─────┬──────┘        └─────────────┘       └──────┬──────┘
         │                                            │
   ┌─────▼──────────────┐                      ┌──────▼──────┐
   │ Azure MCP Server   │                      │ Enterprise  │
   │ (monitor, cosmos)  │                      │ MCP (Graph) │
   │ + DevOps REST API  │                      └─────────────┘
   └────────────────────┘
```

**Key**: Agents execute in a *fixed pipeline order*. Each agent's output becomes the next agent's input.

| Agent | Role | MCP Tools | Output |
|-------|------|-----------|--------|
| **MetricsCollectorAgent** | Gathers sprint, build, deploy, trend data from 5 sources | Azure MCP Server → `monitor`, `cosmos`; Azure DevOps REST API | Raw metrics bundle |
| **TrendAnalystAgent** | Trend analysis, anomaly detection, forecasting | (none — analysis only) | Analysis + anomalies + forecast |
| **AdvisorAgent** | Executive summary, prioritized recommendations, owner assignment | Enterprise MCP → Graph | Executive report |

```bash
# Mock mode
python agents/velocity_analysis.py

# Real mode (requires Azure OpenAI)
python agents/velocity_analysis.py --real
```

---

## Orchestration Patterns Compared

| Aspect | Handoff (Scenario 3) | Sequential (Scenario 5) |
|--------|---------------------|------------------------|
| **Agent order** | Dynamic — agents decide | Fixed pipeline |
| **Backtracking** | Yes (DiagnosticsAgent → TriageAgent) | No |
| **SK class** | `HandoffOrchestration` | `SequentialOrchestration` |
| **Best for** | Non-linear workflows, escalation | Data pipelines, ETL-style flows |
| **Agent count** | 3 | 3 |

Both patterns are part of the [Semantic Kernel Agent Orchestration](https://learn.microsoft.com/en-us/semantic-kernel/frameworks/agent/agent-orchestration/) framework.

## Files

| File | Description |
|------|-------------|
| `incident_remediation.py` | Scenario 3 — Handoff orchestration |
| `velocity_analysis.py` | Scenario 5 — Sequential orchestration |
| `agent_definitions.yaml` | Agent configs for both scenarios |
| `README.md` | This file |

## Prerequisites

- Python 3.10+
- `semantic-kernel[agents]` package (for real mode)
- Azure OpenAI deployment (for agent LLM reasoning in real mode)
- Azure MCP Server running (`npx -y @azure/mcp@latest server start`)
- Microsoft MCP Server for Enterprise (for Graph queries)

## References

- [Semantic Kernel Agent Orchestration](https://learn.microsoft.com/en-us/semantic-kernel/frameworks/agent/agent-orchestration/)
- [Handoff Orchestration Pattern](https://learn.microsoft.com/en-us/semantic-kernel/frameworks/agent/agent-orchestration/handoff)
- [Sequential Orchestration Pattern](https://learn.microsoft.com/en-us/semantic-kernel/frameworks/agent/agent-orchestration/sequential)
- [Azure AI Agent Design Patterns](https://learn.microsoft.com/en-us/azure/architecture/ai-ml/guide/ai-agent-design-patterns)
- [Microsoft Agent Framework](https://github.com/microsoft/agent-framework)
