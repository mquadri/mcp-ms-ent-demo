"""Shared data models for the phase 2 DevOps agent foundation."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


@dataclass
class AlertSignal:
    alert_id: str
    service_name: str
    severity: str
    message: str
    affected_resources: list[str]
    timestamp: str
    source: str = "mock"
    raw: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_mapping(cls, payload: dict[str, Any], source: str = "mock") -> "AlertSignal":
        alert_id = payload.get("AlertId") or payload.get("alert_id") or payload.get("id") or "alert-unknown"
        service_name = payload.get("ServiceName") or payload.get("service_name") or payload.get("service")
        return cls(
            alert_id=str(alert_id),
            service_name=str(service_name or "UnknownService"),
            severity=str(payload.get("Severity") or payload.get("severity") or "Unknown"),
            message=str(payload.get("Message") or payload.get("message") or ""),
            affected_resources=list(payload.get("AffectedResources") or payload.get("affected_resources") or []),
            timestamp=str(payload.get("Timestamp") or payload.get("timestamp") or utc_now_iso()),
            source=source,
            raw=payload,
        )

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class Investigation:
    investigation_id: str
    status: str
    severity: str
    services: list[str]
    resources: list[str]
    root_cause: str | None = None
    mitigation_plan: list[str] = field(default_factory=list)
    approval_status: str = "not_required"
    created_at: str = field(default_factory=utc_now_iso)
    updated_at: str = field(default_factory=utc_now_iso)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class TopologyNode:
    node_id: str
    kind: str
    name: str
    properties: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class TopologyEdge:
    source: str
    target: str
    relationship: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class Recommendation:
    recommendation_id: str
    title: str
    area: str
    priority: int
    rationale: str
    action: str
    owner: str
    source_investigations: list[str]
    created_at: str = field(default_factory=utc_now_iso)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
