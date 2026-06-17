"""MCP adapter boundary for phase 2.

The mock implementation keeps the demo runnable offline. The real adapter is a
thin seam for wiring an MCP client library or deployed MCP endpoint without
changing the orchestration logic.
"""

from __future__ import annotations

from typing import Any, Protocol

from .models import AlertSignal


class DevOpsToolClient(Protocol):
    def fetch_active_alerts(self) -> list[AlertSignal]:
        ...

    def fetch_logs(self, service_name: str) -> list[dict[str, Any]]:
        ...

    def resolve_owner(self, service_name: str) -> dict[str, str]:
        ...

    def create_work_item(self, title: str, body: str, owner: str, dry_run: bool = True) -> dict[str, Any]:
        ...


class MockDevOpsToolClient:
    def __init__(self) -> None:
        self._alerts = [
            {
                "AlertId": "alert-001",
                "ServiceName": "CheckoutService",
                "Severity": "Critical",
                "Message": "Database connection timeout - unable to process orders",
                "AffectedResources": ["sql-checkout-db", "app-checkout-01", "app-checkout-02"],
                "ErrorCode": "CONN_TIMEOUT_5000",
            },
            {
                "AlertId": "alert-002",
                "ServiceName": "PaymentGateway",
                "Severity": "Critical",
                "Message": "Payment processor API returning 503 errors",
                "AffectedResources": ["payment-gateway-01", "payment-gateway-02"],
                "ErrorCode": "EXT_API_ERROR_503",
            },
        ]

    def fetch_active_alerts(self) -> list[AlertSignal]:
        return [AlertSignal.from_mapping(alert, source="mock-azure-monitor") for alert in self._alerts]

    def fetch_logs(self, service_name: str) -> list[dict[str, Any]]:
        common = [
            {
                "level": "ERROR",
                "service": "CheckoutService",
                "message": "Connection pool exhausted after traffic spike",
                "signal": "CONN_POOL_EXHAUSTED",
            },
            {
                "level": "ERROR",
                "service": "PaymentGateway",
                "message": "Upstream checkout retry storm caused downstream 503s",
                "signal": "RETRY_STORM",
            },
        ]
        return [row for row in common if row["service"] == service_name] or common

    def resolve_owner(self, service_name: str) -> dict[str, str]:
        owners = {
            "CheckoutService": {
                "displayName": "System Administrator",
                "mail": "admin@MngEnv399036.onmicrosoft.com",
            },
            "PaymentGateway": {
                "displayName": "Priya Sharma",
                "mail": "priya.sharma@contoso.com",
            },
        }
        return owners.get(service_name, {"displayName": "Platform Engineering", "mail": "platform@contoso.com"})

    def create_work_item(self, title: str, body: str, owner: str, dry_run: bool = True) -> dict[str, Any]:
        return {
            "dry_run": dry_run,
            "id": None if dry_run else 10001,
            "title": title,
            "assigned_to": owner,
            "body": body,
            "url": None if dry_run else "https://dev.azure.com/mquadri-msmenv/mcp-demo/_workitems/edit/10001",
        }


class RealMcpClient:
    def __init__(self, endpoint: str | None = None) -> None:
        self.endpoint = endpoint

    def _not_wired(self) -> RuntimeError:
        return RuntimeError(
            "Real MCP client is not wired yet. Configure this adapter with an MCP client "
            "library or deployed endpoint, or run with --mode mock."
        )

    def fetch_active_alerts(self) -> list[AlertSignal]:
        raise self._not_wired()

    def fetch_logs(self, service_name: str) -> list[dict[str, Any]]:
        raise self._not_wired()

    def resolve_owner(self, service_name: str) -> dict[str, str]:
        raise self._not_wired()

    def create_work_item(self, title: str, body: str, owner: str, dry_run: bool = True) -> dict[str, Any]:
        raise self._not_wired()

