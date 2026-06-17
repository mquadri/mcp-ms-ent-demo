"""Phase 2 orchestration runner."""

from __future__ import annotations

import uuid
from typing import Any

from .approvals import evaluate_remediation_approval
from .mcp_client import DevOpsToolClient
from .models import AlertSignal, Investigation
from .prevention import generate_prevention_recommendations
from .store import AgentStore
from .topology import build_topology


class Phase2DevOpsAgent:
    def __init__(self, tools: DevOpsToolClient, store: AgentStore) -> None:
        self.tools = tools
        self.store = store

    def run_alert_cycle(self, auto_approve: bool = False, dry_run: bool = True) -> dict[str, Any]:
        alerts = self.tools.fetch_active_alerts()
        nodes, edges = build_topology(alerts)
        self.store.save_topology(nodes, edges)

        services = sorted({alert.service_name for alert in alerts})
        resources = sorted({resource for alert in alerts for resource in alert.affected_resources})
        severity = _highest_severity(alerts)
        investigation = Investigation(
            investigation_id=f"inv-{uuid.uuid4().hex[:10]}",
            status="investigating",
            severity=severity,
            services=services,
            resources=resources,
        )
        self.store.save_investigation(investigation)
        self.store.add_event(
            investigation.investigation_id,
            "alerts_received",
            {"alerts": [alert.to_dict() for alert in alerts]},
        )
        self.store.add_event(
            investigation.investigation_id,
            "topology_updated",
            {"nodes": [node.to_dict() for node in nodes], "edges": [edge.to_dict() for edge in edges]},
        )

        logs_by_service = {service: self.tools.fetch_logs(service) for service in services}
        root_cause = _infer_root_cause(logs_by_service)
        mitigation_plan = _build_mitigation_plan(root_cause)
        owner = self.tools.resolve_owner(services[0] if services else "UnknownService")
        approval = evaluate_remediation_approval(severity, mitigation_plan, auto_approve=auto_approve)

        work_item = self.tools.create_work_item(
            title=f"{severity}: {'/'.join(services) or 'Unknown service'} incident",
            body=_format_work_item_body(root_cause, mitigation_plan, logs_by_service),
            owner=owner["mail"],
            dry_run=dry_run or approval.status != "approved",
        )

        investigation.status = "approval_pending" if approval.status == "pending" else "ready_for_execution"
        investigation.root_cause = root_cause
        investigation.mitigation_plan = mitigation_plan
        investigation.approval_status = approval.status
        self.store.save_investigation(investigation)
        self.store.add_event(
            investigation.investigation_id,
            "mitigation_planned",
            {
                "root_cause": root_cause,
                "mitigation_plan": mitigation_plan,
                "approval": approval.__dict__,
                "work_item": work_item,
            },
        )

        recent = self.store.load_recent_investigations(limit=20)
        recommendations = generate_prevention_recommendations(recent)
        self.store.save_recommendations(recommendations)

        return {
            "investigation": investigation.to_dict(),
            "alerts": [alert.to_dict() for alert in alerts],
            "topology": {
                "nodes": [node.to_dict() for node in nodes],
                "edges": [edge.to_dict() for edge in edges],
            },
            "logs_by_service": logs_by_service,
            "approval": approval.__dict__,
            "work_item": work_item,
            "prevention_recommendations": [rec.to_dict() for rec in recommendations],
            "store": self.store.summary(),
        }

    def run_prevention_cycle(self) -> dict[str, Any]:
        recent = self.store.load_recent_investigations(limit=50)
        recommendations = generate_prevention_recommendations(recent)
        self.store.save_recommendations(recommendations)
        return {
            "investigations_analyzed": len(recent),
            "recommendations": [rec.to_dict() for rec in recommendations],
            "store": self.store.summary(),
        }


def _highest_severity(alerts: list[AlertSignal]) -> str:
    order = ["critical", "sev1", "error", "warning", "info", "unknown"]
    normalized = {alert.severity.lower(): alert.severity for alert in alerts}
    for candidate in order:
        for severity in normalized:
            if candidate in severity:
                return "Sev1" if candidate in {"critical", "sev1"} else normalized[severity]
    return alerts[0].severity if alerts else "Unknown"


def _infer_root_cause(logs_by_service: dict[str, list[dict[str, Any]]]) -> str:
    flattened = [entry for logs in logs_by_service.values() for entry in logs]
    messages = " ".join(str(entry.get("message", "")) for entry in flattened).lower()
    if "connection pool" in messages:
        return "Database connection pool exhaustion in CheckoutService"
    if "503" in messages:
        return "Upstream dependency returned elevated 503 responses"
    return "Operational anomaly requires deeper telemetry correlation"


def _build_mitigation_plan(root_cause: str) -> list[str]:
    if "connection pool" in root_cause.lower():
        return [
            "Increase database connection pool max size from 50 to 200.",
            "Deploy a circuit breaker on the database retry path.",
            "Scale CheckoutService instances before reopening traffic.",
            "Add Azure Monitor alerts for connection pool saturation.",
        ]
    return [
        "Capture correlated traces and dependency metrics.",
        "Create an Azure DevOps work item for the owning service team.",
        "Add an alert that catches the failure mode earlier.",
    ]


def _format_work_item_body(
    root_cause: str,
    mitigation_plan: list[str],
    logs_by_service: dict[str, list[dict[str, Any]]],
) -> str:
    lines = [
        f"Root cause: {root_cause}",
        "",
        "Mitigation plan:",
    ]
    lines.extend(f"- {step}" for step in mitigation_plan)
    lines.append("")
    lines.append("Evidence:")
    for service, logs in logs_by_service.items():
        for entry in logs[:3]:
            lines.append(f"- {service}: {entry.get('message', 'no message')}")
    return "\n".join(lines)
