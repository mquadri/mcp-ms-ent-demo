# Phase 2 DevOps Agent Foundation

Phase 2 adds the foundation for an always-on DevOps agent while keeping the existing demo scenarios stable.

## What It Adds

| Capability | Implementation |
|---|---|
| Alert-triggered execution | `agents/phase2_devops_agent.py alert-cycle` starts a full investigation cycle from active alerts. |
| Always-on polling worker | `agents/phase2_devops_agent.py watch` runs repeated alert cycles with a configurable interval. |
| Persistent investigations | `agents/phase2/store.py` stores investigations, events, topology, and recommendations in SQLite. |
| Application topology | `agents/phase2/topology.py` maps services, resources, and relationships from alert context. |
| Human approval gates | `agents/phase2/approvals.py` blocks risky production remediation unless `--auto-approve` is used. |
| Prevention recommendations | `agents/phase2/prevention.py` analyzes persisted investigations and emits reliability work. |
| Real MCP integration seam | `agents/phase2/mcp_client.py` defines `DevOpsToolClient`; `RealMcpClient` is the next wiring point. |

## Run Locally

```bash
python agents/phase2_devops_agent.py alert-cycle
python agents/phase2_devops_agent.py watch --cycles 1
python agents/phase2_devops_agent.py store-summary
python agents/phase2_devops_agent.py prevention-cycle
```

The default mode is mock mode. It writes generated state to:

```text
agents/.data/phase2_devops_agent.db
```

Use a disposable database during tests:

```bash
python agents/phase2_devops_agent.py alert-cycle --db-path /tmp/phase2_agent.db
```

Run a bounded polling worker:

```bash
python agents/phase2_devops_agent.py watch --cycles 3 --interval-seconds 60
```

## Safety Model

By default, work-item creation is a dry run and production-impacting remediation remains approval-gated. The agent marks remediation as pending when the mitigation plan includes actions such as deploy, scale, restart, failover, delete, or rotate.

To simulate an approved run:

```bash
python agents/phase2_devops_agent.py alert-cycle --auto-approve --execute
```

In mock mode this still does not modify external systems; it only shows the point where a real adapter would create the work item.

## Real MCP Wiring Point

`RealMcpClient` is intentionally a thin adapter. Wire it to the deployed MCP endpoint or to a Python MCP client library by implementing:

- `fetch_active_alerts`
- `fetch_logs`
- `resolve_owner`
- `create_work_item`

The orchestration in `agents/phase2/runner.py` does not need to change when the adapter moves from mock data to real MCP calls.

## Suggested Next Step

Connect `RealMcpClient` to `demo-agents-mcp` first for read-only health and investigation calls, then add Azure Monitor, Microsoft Graph, and Azure DevOps write operations behind the existing approval gate.
