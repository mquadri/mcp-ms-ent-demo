"""Application topology builder for investigations."""

from __future__ import annotations

from .models import AlertSignal, TopologyEdge, TopologyNode


def build_topology(alerts: list[AlertSignal]) -> tuple[list[TopologyNode], list[TopologyEdge]]:
    nodes: dict[str, TopologyNode] = {}
    edges: list[TopologyEdge] = []

    for alert in alerts:
        service_id = f"service:{alert.service_name}"
        nodes[service_id] = TopologyNode(
            node_id=service_id,
            kind="service",
            name=alert.service_name,
            properties={"severity": alert.severity, "source": alert.source},
        )
        for resource in alert.affected_resources:
            resource_id = f"resource:{resource}"
            nodes[resource_id] = TopologyNode(
                node_id=resource_id,
                kind=_infer_resource_kind(resource),
                name=resource,
                properties={"alert_id": alert.alert_id},
            )
            edges.append(TopologyEdge(source=service_id, target=resource_id, relationship="depends_on"))

    if "service:CheckoutService" in nodes and "service:PaymentGateway" in nodes:
        edges.append(
            TopologyEdge(
                source="service:CheckoutService",
                target="service:PaymentGateway",
                relationship="calls",
            )
        )

    return list(nodes.values()), edges


def _infer_resource_kind(resource_name: str) -> str:
    lowered = resource_name.lower()
    if "sql" in lowered or "db" in lowered:
        return "database"
    if "queue" in lowered:
        return "queue"
    if "app" in lowered or "service" in lowered:
        return "compute"
    return "resource"

