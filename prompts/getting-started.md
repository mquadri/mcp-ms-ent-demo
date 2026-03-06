# Getting Started Prompts - Microsoft Enterprise MCP Servers

These natural language prompts demonstrate Microsoft Enterprise MCP integrations
across Azure Monitor, Azure DevOps, Microsoft Graph, and Cosmos DB. Each prompt
includes the MCP servers it exercises and any data prerequisites.

---

## Scenario 1: Automated Incident Response

### Prompt 1 — Triage Critical Alerts

**MCP Servers**: Azure Monitor  
**Prerequisites**: Run `python demos/setup_scenario_1.py` to seed alerts

> "Our monitoring is alerting on the CheckoutService. Fetch all active critical
> alerts from Azure Monitor for the contoso-monitoring resource group. For each
> alert, extract the service name, error code, and affected resources. Summarize
> the incident timeline showing when each alert fired."

---

### Prompt 2 — Correlate Logs and Create Incident

**MCP Servers**: Azure Monitor, Azure DevOps  
**Prerequisites**: Run `python demos/setup_scenario_1.py`

> "Pull the last 10 ERROR-level application logs from the CheckoutService in
> Azure Monitor. Identify the root cause error pattern. Then create a Severity 1
> bug in the ContosoApp Azure DevOps project with the title 'CRITICAL:
> CheckoutService DB Connection Timeout', include the error stack trace in the
> description, and tag it with 'incident' and 'auto-generated'."

---

### Prompt 3 — Identify On-Call and Assign

**MCP Servers**: Microsoft Graph, Azure DevOps  
**Prerequisites**: Run `python demos/setup_scenario_1.py`

> "Look up who is on the Platform Engineering team using Microsoft Graph. Find
> the current on-call engineer and assign the open critical incident ticket in
> Azure DevOps to them. Send a Teams notification to the engineer with the
> incident summary."

---

### Prompt 4 — Full Incident Response Chain

**MCP Servers**: Azure Monitor, Azure DevOps, Microsoft Graph  
**Prerequisites**: Run `python demos/setup_scenario_1.py`

> "We have a production incident. First, fetch all critical alerts from Azure
> Monitor for the last hour. Then look at the application error logs to identify
> the root cause. Create a Severity 1 incident ticket in Azure DevOps with all
> relevant details. Finally, find the on-call Platform engineer via Microsoft
> Graph and assign the ticket to them."

---

## Scenario 5: Development Velocity Analysis

### Prompt 5 — Sprint Velocity Report

**MCP Servers**: Azure DevOps  
**Prerequisites**: Run `python demos/setup_scenario_5.py`

> "Pull the sprint metrics for Sprints 22, 23, and 24 from Azure DevOps for the
> ContosoApp project. Show me the velocity trend (points completed vs. planned)
> across all three sprints. Is the team accelerating or decelerating?"

---

### Prompt 6 — Build & Deployment Health

**MCP Servers**: Azure Monitor  
**Prerequisites**: Run `python demos/setup_scenario_5.py`

> "Query Azure Monitor for the ContosoApp-CI build pipeline metrics over the
> last 30 days. Calculate the average build duration, success rate, and test pass
> rate. Then pull deployment logs and tell me the deployment frequency and
> rollback rate for production."

---

### Prompt 7 — Code Review Cycle Analysis

**MCP Servers**: Azure DevOps  
**Prerequisites**: Run `python demos/setup_scenario_5.py`

> "Analyze the ContosoApp repository metrics in Azure DevOps. What is the
> average PR review time? How many PRs are merged per day? What is the current
> branch coverage? Identify any bottlenecks in the code review process."

---

### Prompt 8 — Historical Trend Forecasting

**MCP Servers**: Cosmos DB, Azure DevOps  
**Prerequisites**: Run `python demos/setup_scenario_5.py`

> "Read the velocity trend documents from the dev_analytics Cosmos DB database
> (velocity_metrics container). Plot the 12-week velocity trajectory and
> completion rate. Based on the trend, forecast next sprint's expected velocity
> and identify any concerning patterns."

---

### Prompt 9 — Full Velocity Dashboard

**MCP Servers**: Azure DevOps, Azure Monitor, Cosmos DB  
**Prerequisites**: Run `python demos/setup_scenario_5.py`

> "Build me a comprehensive development velocity report. Pull sprint data from
> Azure DevOps, build/deployment metrics from Azure Monitor, and historical
> trends from Cosmos DB. Summarize: (1) current velocity vs. target, (2) build
> stability, (3) deployment cadence, (4) code review efficiency. Recommend 3
> specific actions to improve team throughput."

---

### Prompt 10 — Cross-Scenario: Incident Impact on Velocity

**MCP Servers**: Azure Monitor, Azure DevOps, Cosmos DB  
**Prerequisites**: Run both `setup_scenario_1.py` and `setup_scenario_5.py`

> "We had a critical incident last sprint. Correlate the incident alerts from
> Azure Monitor with the sprint velocity data in Azure DevOps. Did the incident
> cause a velocity dip? Check Cosmos DB historical trends to see if this is a
> recurring pattern. Recommend process improvements to minimize incident impact
> on delivery velocity."
