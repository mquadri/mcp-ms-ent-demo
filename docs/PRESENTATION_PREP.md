# Presentation Preparation

## Session Title

How I Implemented an Agent Framework with Azure MCP, VS Code, and Semantic Kernel

## Audience

Mixed technical audience: architects, developers, managers, platform engineers, and AI-curious stakeholders.

## Session Promise

This is a learn-by-showing session. The audience will see a real Azure + VS Code demo, then understand how the implementation works underneath.

## Resources To Show

| Resource | URL | How to use it in the session |
|---|---|---|
| ResonateHub AI Learn | `https://www.resonatehubai.com/learn/index.html` | Learning entry point for agent concepts |
| Getting Started lesson | `https://lemon-mud-0ea992703.4.azurestaticapps.net/lesson/getting-started` | Beginner-friendly introduction before showing the repo |
| This repo | Local repo in VS Code | Real implementation and demo source |
| Architecture diagram | `docs/architecture.drawio` | Editable visual for the demo architecture |

## 60-Minute Flow

| Time | Segment | Goal |
|---|---|---|
| 0:00-0:05 | Personal intro and goal | Explain what you built and what the audience will learn |
| 0:05-0:10 | Learning resources | Anchor the session in beginner-friendly references |
| 0:10-0:18 | Concepts | Explain agents, tools, MCP, and orchestration |
| 0:18-0:25 | Repo and architecture walkthrough | Show the real implementation structure |
| 0:25-0:36 | Demo 1: VS Code real Azure MCP incident flow | Show one agent using enterprise tools |
| 0:36-0:48 | Demo 2: Multi-agent handoff | Show specialist agents collaborating |
| 0:48-0:55 | Demo 3: Sequential velocity analysis | Show a fixed agent pipeline |
| 0:55-1:00 | Recap and Q&A | Reinforce the learning path |

## Opening Script

Today I am going to show how I implemented an agent framework using Azure, MCP, VS Code, and Semantic Kernel. This is not just a chatbot demo. The goal is to show how an agent can use real enterprise tools, reason over live context, and move work forward.

I will start with the learning resources, then move into my repo. We will go from the simplest pattern, one agent using tools, to a multi-agent handoff workflow, and then to a sequential multi-agent analytics pipeline.

## Core Explanation

Use this simple mental model:

```text
User request
  -> Agent reasoning
  -> Tool selection
  -> MCP endpoint
  -> Azure / Graph / DevOps data
  -> Agent action or summary
```

Say this clearly:

MCP is the tool bridge. Semantic Kernel is the agent workflow engine.

## Key Terms

| Term | Plain-language explanation |
|---|---|
| Agent | An AI system with instructions, tools, and a goal |
| Tool | Something the agent can call to get data or take action |
| MCP | A standard protocol for connecting agents to tools |
| Azure MCP | MCP access to Azure services such as Monitor and logs |
| Enterprise/Graph context | Tenant, user, team, role, and ownership data |
| Handoff | One specialist agent passes context to another |
| Sequential | Agents run in a fixed pipeline |

## Demo Message For Mixed Audience

For leaders:

This reduces manual triage and turns signals into assigned engineering work.

For developers:

This is a practical pattern for connecting LLM reasoning to tools without hardcoding every workflow into one script.

For platform engineers:

This keeps identity, permissions, and cloud access behind standard enterprise boundaries.

For architects:

This separates user experience, protocol, tool access, and orchestration into clear layers.

## Files To Keep Open In VS Code

- `README.md`
- `docs/architecture.md`
- `docs/architecture.drawio`
- `docs/REAL_AZURE_VSCODE_DEMO_RUNBOOK.md`
- `agents/agent_definitions.yaml`
- `agents/incident_remediation.py`
- `agents/velocity_analysis.py`
- `prompts/getting-started.md`

## Closing Script

The main takeaway is that agents become useful when they can safely use tools. MCP gives us a standard way to expose those tools. Semantic Kernel gives us patterns for coordinating agents. In this repo, I used both to show three levels of implementation: one agent using tools, multiple agents handing off incident response, and a sequential pipeline for velocity analysis.

