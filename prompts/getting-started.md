# Getting Started Prompts - Microsoft Enterprise MCP Servers

These natural language prompts demonstrate official Microsoft MCP integrations
using the **Azure MCP Server** (`@azure/mcp`) and the **Microsoft MCP Server
for Enterprise**. Scenario 3 also demonstrates the **Semantic Kernel Agent
Framework** (Handoff Orchestration). Each prompt includes the MCP servers it
exercises and any data prerequisites.

---

## Scenario 1: Automated Incident Response

### Prompt 1 — Triage Critical Alerts

**MCP Servers**: Azure MCP Server (monitor namespace)  
**Prerequisites**: Run `python demos/setup_scenario_1.py` to seed alerts

> "Our monitoring is alerting on the CheckoutService. Fetch all active critical
> alerts from Azure Monitor for the contoso-monitoring resource group. For each
> alert, extract the service name, error code, and affected resources. Summarize
> the incident timeline showing when each alert fired."

---

### Prompt 2 — Correlate Logs and Create Incident

**MCP Servers**: Azure MCP Server (monitor, appinsights namespaces)  
**Prerequisites**: Run `python demos/setup_scenario_1.py`

> "Pull the last 10 ERROR-level application logs from the CheckoutService in
> Azure Monitor. Identify the root cause error pattern. Then create a Severity 1
> bug in the ContosoApp Azure DevOps project with the title 'CRITICAL:
> CheckoutService DB Connection Timeout', include the error stack trace in the
> description, and tag it with 'incident' and 'auto-generated'."

---

### Prompt 3 — Identify On-Call and Assign

**MCP Servers**: Enterprise MCP (Microsoft Graph), Azure DevOps  
**Prerequisites**: Run `python demos/setup_scenario_1.py`

> "Look up who is on the Platform Engineering team using the Enterprise MCP
> Server (Microsoft Graph). Find the current on-call engineer and assign the
> open critical incident ticket in Azure DevOps to them."

---

### Prompt 4 — Full Incident Response Chain

**MCP Servers**: Azure MCP Server (monitor), Enterprise MCP (Graph)  
**Prerequisites**: Run `python demos/setup_scenario_1.py`

> "We have a production incident. First, fetch all critical alerts from Azure
> Monitor via the Azure MCP Server for the last hour. Then look at the
> application error logs to identify the root cause. Create a Severity 1
> incident ticket in Azure DevOps with all relevant details. Finally, find the
> on-call Platform engineer via the Enterprise MCP Server and assign the ticket
> to them."

---

## Scenario 3: Multi-Agent Incident Remediation (Handoff)

### Prompt 5 — Run Multi-Agent Orchestration

**Framework**: Semantic Kernel Handoff Orchestration  
**Prerequisites**: Run `python demos/setup_scenario_3.py`

> "Run the multi-agent incident remediation workflow. A TriageAgent should
> classify the CheckoutService database timeout as Sev1 and identify the blast
> radius. Then hand off to a DiagnosticsAgent for root-cause analysis using
> Application Insights logs. Finally, hand off to a RemediationAgent to create
> an Azure DevOps ticket and assign the on-call engineer."

---

### Prompt 6 — Agent-to-Agent Handoff Demonstration

**Framework**: Semantic Kernel Handoff Orchestration  
**Prerequisites**: Run `python demos/setup_scenario_3.py`

> "Demonstrate the Handoff orchestration pattern: have a TriageAgent analyze
> current Azure Monitor alerts, then hand off its findings to a Diagnostics
> Agent that correlates Application Insights traces. The DiagnosticsAgent should
> then hand off to a RemediationAgent that creates work items and assigns engineers."

---

## Scenario 5: Development Velocity Analysis

### Prompt 7 — Sprint Velocity Report

**MCP Servers**: Azure DevOps  
**Prerequisites**: Run `python demos/setup_scenario_5.py`

> "Pull the sprint metrics for Sprints 22, 23, and 24 from Azure DevOps for the
> ContosoApp project. Show me the velocity trend (points completed vs. planned)
> across all three sprints. Is the team accelerating or decelerating?"

---

### Prompt 8 — Build & Deployment Health

**MCP Servers**: Azure MCP Server (monitor namespace)  
**Prerequisites**: Run `python demos/setup_scenario_5.py`

> "Query Azure Monitor for the ContosoApp-CI build pipeline metrics over the
> last 30 days. Calculate the average build duration, success rate, and test pass
> rate. Then pull deployment logs and tell me the deployment frequency and
> rollback rate for production."

---

### Prompt 9 — Code Review Cycle Analysis

**MCP Servers**: Azure DevOps  
**Prerequisites**: Run `python demos/setup_scenario_5.py`

> "Analyze the ContosoApp repository metrics in Azure DevOps. What is the
> average PR review time? How many PRs are merged per day? What is the current
> branch coverage? Identify any bottlenecks in the code review process."

---

### Prompt 10 — Historical Trend Forecasting

**MCP Servers**: Azure MCP Server (cosmos namespace), Azure DevOps  
**Prerequisites**: Run `python demos/setup_scenario_5.py`

> "Read the velocity trend documents from the dev_analytics Cosmos DB database
> (velocity_metrics container). Plot the 12-week velocity trajectory and
> completion rate. Based on the trend, forecast next sprint's expected velocity
> and identify any concerning patterns."

---

### Prompt 11 — Multi-Agent Velocity Analysis Pipeline

**Framework**: Semantic Kernel Sequential Orchestration  
**Prerequisites**: Run `python demos/setup_scenario_5.py`

> "Run the multi-agent velocity analysis pipeline. Have the MetricsCollectorAgent
> gather sprint data from Azure DevOps, build/deployment logs from Azure Monitor,
> and 12-week trends from Cosmos DB. Pass the data to TrendAnalystAgent for
> trend analysis, anomaly detection, and forecasting. Finally, have AdvisorAgent
> generate an executive report with prioritized recommendations and assigned
> engineering owners."

---

### Prompt 12 — Sequential vs. Handoff Comparison

**Framework**: Semantic Kernel Sequential Orchestration  
**Prerequisites**: Run `python demos/setup_scenario_5.py`

> "Demonstrate the Sequential orchestration pattern by running MetricsCollectorAgent,
> TrendAnalystAgent, and AdvisorAgent in a fixed pipeline. Compare this approach
> with the Handoff pattern from Scenario 3 — explain why a fixed pipeline works
> better for data analytics workflows."

---

### Prompt 13 — Full Velocity Dashboard

**MCP Servers**: Azure MCP Server (monitor, cosmos namespaces), Azure DevOps  
**Prerequisites**: Run `python demos/setup_scenario_5.py`

> "Build me a comprehensive development velocity report. Pull sprint data from
> Azure DevOps, build/deployment metrics from Azure Monitor (via Azure MCP
> Server), and historical trends from Cosmos DB (via Azure MCP Server). Summarize:
> (1) current velocity vs. target, (2) build stability, (3) deployment cadence,
> (4) code review efficiency. Recommend 3 specific actions to improve throughput."

---

## Cross-Scenario

### Prompt 14 — Incident Impact on Velocity

**MCP Servers**: Azure MCP Server (monitor, cosmos namespaces), Azure DevOps  
**Prerequisites**: Run both `setup_scenario_1.py` and `setup_scenario_5.py`

> "We had a critical incident last sprint. Correlate the incident alerts from
> the Azure MCP Server (monitor namespace) with the sprint velocity data in
> Azure DevOps. Did the incident cause a velocity dip? Check Cosmos DB
> historical trends (via Azure MCP Server) to see if this is a recurring
> pattern. Recommend process improvements to minimize incident impact on
> delivery velocity."
