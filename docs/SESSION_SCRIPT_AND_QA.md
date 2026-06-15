# Session Script And Q&A

## One-Minute Opening

Hi everyone. In this session I am going to show how I implemented an agent framework using Azure, MCP, VS Code, and Semantic Kernel.

This will be demo-first. I will use learning resources to explain the foundation, then I will show the real repo and a real Azure deployment. The goal is that by the end, you understand how an AI agent can move from a natural-language request to real enterprise action.

## Explain The Learning Path

Start with the two web resources:

- `https://www.resonatehubai.com/learn/index.html`
- `https://lemon-mud-0ea992703.4.azurestaticapps.net/lesson/getting-started`

Script:

These resources are useful for the basics. They help explain what agents are and how to start thinking about agent workflows. My repo is the applied version: it shows how those concepts become a real Azure and VS Code demo.

## Explain The Architecture

Script:

The architecture has four layers. First, VS Code is the user experience. Second, the agent reasons over the request and decides what it needs. Third, MCP exposes tools and services in a standard way. Fourth, Azure, Microsoft Graph, and Azure DevOps provide the real enterprise data and actions.

The simplest phrase is: MCP is the tool bridge. Semantic Kernel is the agent workflow engine.

## Demo 1 Script: Real Azure MCP In VS Code

Prompt:

```text
We have a production incident. Use the configured MCP tools to inspect current Azure service health, alerts, and relevant logs. Summarize the likely root cause, impacted resources, and recommended next step.
```

Talk track:

Here I am asking for an outcome, not telling the agent every API call. The agent uses MCP tools to retrieve real context. For a business audience, the important thing is faster incident understanding. For a technical audience, the important thing is that tool access is standardized and governed.

## Demo 2 Script: Handoff Orchestration

Command:

```powershell
python agents/incident_remediation.py
```

Talk track:

This is the handoff pattern. The TriageAgent owns severity and blast radius. The DiagnosticsAgent owns root cause. The RemediationAgent owns the work item, owner assignment, and final summary.

This is similar to a real incident response team. Each agent has a specific job, and context is passed forward.

## Demo 3 Script: Sequential Orchestration

Command:

```powershell
python agents/velocity_analysis.py
```

Talk track:

This is the sequential pattern. It is less dynamic than handoff, but perfect for analytics. The first agent collects data, the second analyzes it, and the third turns it into recommendations.

The key design decision is this: use handoff when the workflow is investigative, and use sequential when the workflow is a pipeline.

## Recap

Script:

Today we saw three levels. First, one agent using tools. Second, multiple agents handing work to each other. Third, multiple agents running as a fixed pipeline.

The implementation pattern is reusable. Define the workflow, expose the right tools through MCP, give each agent a clear responsibility, and choose the orchestration pattern that fits the job.

## Expected Questions

### What is MCP?

MCP is the Model Context Protocol. It gives agents a standard way to discover and call tools. In this demo, MCP connects the agent to Azure and enterprise services.

### What is the difference between MCP and Semantic Kernel?

MCP exposes tools. Semantic Kernel orchestrates agents. MCP is how the agent reaches systems. Semantic Kernel is how the agent workflow is structured.

### Why use Azure Container Apps?

Container Apps gives us a managed way to host the agent and MCP services. It is a good fit for HTTP services, containerized workloads, scale-to-zero demos, and environment-level networking.

### Why are some endpoints internal?

Internal endpoints are used when a service should only be reachable inside the Container Apps environment. That reduces exposure and keeps service-to-service traffic inside the environment boundary.

### What is the difference between `agents` and `agents-mcp`?

`agents` is the application endpoint for the agent experience. `agents-mcp` is the MCP-facing endpoint that exposes tool capabilities to MCP clients.

### Why split agents into Triage, Diagnostics, and Remediation?

Each role has a different responsibility. Splitting them makes the workflow easier to understand, easier to test, and safer to govern.

### When should I use handoff?

Use handoff when the next step depends on what the previous agent found. Incident response, support escalation, and investigations are good examples.

### When should I use sequential orchestration?

Use sequential orchestration when the workflow has a stable order. Analytics, reporting, enrichment, and review pipelines are good examples.

### Is the demo using real Azure?

Yes. The demo is designed for real Azure and VS Code. The repo also includes mock-mode scripts as a fallback and teaching aid.

### Is mock mode still useful?

Yes. Mock mode proves the orchestration pattern without depending on live services. It is also useful for teaching, testing, and fallback during presentations.

### How are permissions handled?

Permissions are handled through Azure identity, RBAC, Graph permissions, DevOps credentials, and MCP server configuration. The agent can only do what the configured tools and identities allow.

### Can this modify production?

It can if the identity and tools allow it. For production, use least privilege, approval gates, environment separation, and clear logging.

### How do you prevent the agent from doing the wrong thing?

Use scoped tools, least-privilege identities, structured prompts, validation, human approval for risky actions, and logging. For demos, keep destructive actions out of scope.

### What is the most important implementation lesson?

Start with the workflow, not the model. Decide what outcome you want, what tools are needed, which agent owns each decision, and which orchestration pattern fits.

### What would you improve next?

Add stronger health checks, structured output schemas, tracing across agent handoffs, approval steps for production changes, and dashboards for tool usage and success rates.

## Short Answers For Executives

### What value does this create?

It reduces manual triage, speeds up incident response, and turns enterprise data into assigned engineering action.

### Is this replacing engineers?

No. It helps engineers move faster by gathering context, summarizing evidence, and preparing the next action.

### Why now?

The tooling has matured. MCP standardizes tool access, and frameworks like Semantic Kernel make multi-agent workflows practical.

## Short Answers For Developers

### Where do I start in the repo?

Start with `README.md`, then `agents/README.md`, then run `python agents/incident_remediation.py`.

### Where are agent responsibilities defined?

Agent responsibilities are documented in `agents/agent_definitions.yaml` and implemented in the Python scripts.

### How do I add another agent?

Define the role, tools, input, output, and handoff or pipeline position. Then add it to the orchestration.

