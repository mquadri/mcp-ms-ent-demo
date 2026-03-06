# File: demos/setup_scenario_3.py
"""
Scenario 3: Multi-Agent Incident Remediation — Data Setup
Seeds the same data as Scenario 1 plus multi-agent orchestration metadata
for demonstrating the Handoff pattern with Semantic Kernel.
"""

import json
import os
import sys
from datetime import datetime, timedelta

USE_MOCK_DATA = os.getenv("USE_MOCK_DATA", "true").lower() == "true"

# ============================================================================
# Scenario 3 mock data — extends Scenario 1 with multi-agent context
# ============================================================================

ALERTS = [
    {
        "AlertId": "alert-001",
        "ServiceName": "CheckoutService",
        "Severity": "Critical",
        "Message": "Database connection timeout - unable to process orders",
        "AffectedResources": ["sql-checkout-db", "app-checkout-01", "app-checkout-02"],
        "ErrorCode": "CONN_TIMEOUT_5000",
        "Timestamp": (datetime.utcnow() - timedelta(minutes=15)).isoformat(),
        "IncidentCount": 342,
    },
    {
        "AlertId": "alert-002",
        "ServiceName": "PaymentGateway",
        "Severity": "Critical",
        "Message": "Payment processor API returning 503 errors",
        "AffectedResources": ["payment-gateway-01", "payment-gateway-02"],
        "ErrorCode": "EXT_API_ERROR_503",
        "Timestamp": (datetime.utcnow() - timedelta(minutes=12)).isoformat(),
        "IncidentCount": 127,
    },
    {
        "AlertId": "alert-003",
        "ServiceName": "NotificationService",
        "Severity": "Error",
        "Message": "Email queue backing up - 50K+ undelivered messages",
        "AffectedResources": ["queue-notifications", "email-service-01"],
        "ErrorCode": "QUEUE_OVERFLOW",
        "Timestamp": (datetime.utcnow() - timedelta(minutes=8)).isoformat(),
        "IncidentCount": 89,
    },
]

ERROR_LOGS = [
    {
        "level": "ERROR",
        "service": "CheckoutService",
        "message": "Database query timeout after 5000ms — connection pool exhausted",
        "stack_trace": (
            "at CheckoutService.ProcessOrder (line 234)\n"
            "  at DbConnectionPool.Acquire (line 89)\n"
            "  at SqlClient.ExecuteQuery (line 156)"
        ),
        "request_id": "req-9921-8839",
        "timestamp": (datetime.utcnow() - timedelta(minutes=14)).isoformat(),
    },
    {
        "level": "ERROR",
        "service": "PaymentGateway",
        "message": "External API unreachable: Stripe gateway returns 503",
        "error_code": "STRIPE_503",
        "request_id": "req-9921-8840",
        "timestamp": (datetime.utcnow() - timedelta(minutes=11)).isoformat(),
    },
    {
        "level": "ERROR",
        "service": "CheckoutService",
        "message": "Connection pool exhausted, unable to allocate new connection",
        "error_code": "CONN_POOL_EXHAUSTED",
        "request_id": "req-9921-8841",
        "timestamp": (datetime.utcnow() - timedelta(minutes=10)).isoformat(),
    },
]

ONCALL_ENGINEER = {
    "displayName": "Ahmed Hassan",
    "mail": "ahmed.hassan@contoso.com",
    "jobTitle": "Senior Platform Engineer",
    "team": "Platform Engineering",
}

AGENT_HANDOFF_LOG = [
    {
        "step": 1,
        "agent": "TriageAgent",
        "action": "Classified Sev1, identified 2 critical services, 4 resources",
        "handoff_to": "DiagnosticsAgent",
        "duration_ms": 1200,
    },
    {
        "step": 2,
        "agent": "DiagnosticsAgent",
        "action": "Root cause: DB connection pool exhaustion; 3 contributing factors",
        "handoff_to": "RemediationAgent",
        "duration_ms": 2400,
    },
    {
        "step": 3,
        "agent": "RemediationAgent",
        "action": "Created Bug #54321, assigned to Ahmed Hassan, proposed 3-step fix",
        "handoff_to": None,
        "duration_ms": 1800,
    },
]


def main():
    print("=" * 70)
    print("🤖 SCENARIO 3: MULTI-AGENT INCIDENT REMEDIATION — SETUP")
    print("=" * 70)
    print(f"Mode: {'MOCK DATA' if USE_MOCK_DATA else 'LIVE'}\n")

    # Seed alerts
    print("📊 Seeding Azure Monitor with critical alerts...")
    for alert in ALERTS:
        print(f"   ✓ Alert {alert['AlertId']}: {alert['ServiceName']} - {alert['Message']}")

    # Seed logs
    print("\n📋 Seeding application error logs...")
    for log in ERROR_LOGS:
        print(f"   ✓ {log['service']}: {log['message']}")

    # Seed on-call
    print(f"\n👤 On-call engineer: {ONCALL_ENGINEER['displayName']} ({ONCALL_ENGINEER['mail']})")

    # Seed agent handoff metadata
    print("\n🤖 Agent Handoff Chain:")
    for entry in AGENT_HANDOFF_LOG:
        arrow = f"→ {entry['handoff_to']}" if entry['handoff_to'] else "(terminal)"
        print(f"   Step {entry['step']}: {entry['agent']} {arrow}")
        print(f"           {entry['action']}")

    # Write mock data to a JSON file for the orchestration script to consume
    output_dir = os.path.join(os.path.dirname(__file__), "..", "agents", ".data")
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, "scenario_3_mock_data.json")

    mock_data = {
        "alerts": ALERTS,
        "error_logs": ERROR_LOGS,
        "oncall_engineer": ONCALL_ENGINEER,
        "agent_handoff_log": AGENT_HANDOFF_LOG,
        "generated_at": datetime.utcnow().isoformat(),
    }

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(mock_data, f, indent=2)
    print(f"\n💾 Mock data written to {output_file}")

    print("\n" + "=" * 70)
    print("✅ SCENARIO 3 SETUP COMPLETE")
    print("=" * 70)
    print("\nNext: Run the multi-agent orchestration:")
    print("  python agents/incident_remediation.py")
    print("\nOr with real Semantic Kernel + Azure OpenAI:")
    print("  python agents/incident_remediation.py --real")


if __name__ == "__main__":
    main()
