# File: agents/incident_remediation.py
"""
Scenario 3: Multi-Agent Incident Remediation
=============================================
Demonstrates the Semantic Kernel Handoff Orchestration pattern where
three specialized agents collaborate to handle an incident end-to-end:

  TriageAgent → DiagnosticsAgent → RemediationAgent

Each agent uses MCP tools (Azure MCP Server, Enterprise MCP) and hands
off context to the next agent in the chain.

Requirements:
  pip install semantic-kernel[agents]
  Environment: AZURE_OPENAI_ENDPOINT, AZURE_OPENAI_DEPLOYMENT, AZURE_OPENAI_API_KEY
               or use DefaultAzureCredential for token-based auth.

References:
  - https://learn.microsoft.com/en-us/semantic-kernel/frameworks/agent/agent-orchestration/handoff
  - https://learn.microsoft.com/en-us/azure/architecture/ai-ml/guide/ai-agent-design-patterns
"""

import asyncio
import argparse
import json
import os
import sys
from datetime import datetime, timedelta, timezone
from typing import Any

# ---------------------------------------------------------------------------
# Mock mode — if True, agents use simulated tool results instead of live MCP
# ---------------------------------------------------------------------------
USE_MOCK_DATA = os.getenv("USE_MOCK_DATA", "true").lower() == "true"

# ---------------------------------------------------------------------------
# Mock MCP tool responses (used when USE_MOCK_DATA=true or SK not installed)
# ---------------------------------------------------------------------------

MOCK_ALERTS = [
    {
        "AlertId": "alert-001",
        "ServiceName": "CheckoutService",
        "Severity": "Critical",
        "Message": "Database connection timeout - unable to process orders",
        "AffectedResources": ["sql-checkout-db", "app-checkout-01", "app-checkout-02"],
        "ErrorCode": "CONN_TIMEOUT_5000",
        "Timestamp": (datetime.now(timezone.utc) - timedelta(minutes=15)).isoformat(),
        "IncidentCount": 342,
    },
    {
        "AlertId": "alert-002",
        "ServiceName": "PaymentGateway",
        "Severity": "Critical",
        "Message": "Payment processor API returning 503 errors",
        "AffectedResources": ["payment-gateway-01", "payment-gateway-02"],
        "ErrorCode": "EXT_API_ERROR_503",
        "Timestamp": (datetime.now(timezone.utc) - timedelta(minutes=12)).isoformat(),
        "IncidentCount": 127,
    },
]

MOCK_LOGS = [
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
        "timestamp": (datetime.now(timezone.utc) - timedelta(minutes=14)).isoformat(),
    },
    {
        "level": "ERROR",
        "service": "PaymentGateway",
        "message": "External API unreachable: Stripe gateway returns 503",
        "error_code": "STRIPE_503",
        "request_id": "req-9921-8840",
        "timestamp": (datetime.now(timezone.utc) - timedelta(minutes=11)).isoformat(),
    },
]

MOCK_ONCALL = {
    "displayName": "System Administrator",
    "mail": "admin@MngEnv399036.onmicrosoft.com",
    "jobTitle": "Senior Platform Engineer",
    "team": "Platform Engineering",
}

ADO_ORG = "mquadri-msmenv"
ADO_PROJECT = "mcp-demo"

MOCK_WORKITEM = {
    "id": 1,
    "title": "CRITICAL: CheckoutService DB Connection Timeout - Sev1 Incident",
    "url": f"https://dev.azure.com/{ADO_ORG}/{ADO_PROJECT}/_workitems/edit/1",
    "state": "To Do",
    "type": "Issue",
    "assignedTo": "admin@MngEnv399036.onmicrosoft.com",
    "childTasks": [
        {"id": 5, "title": "Increase DB connection pool max size from 50 to 200"},
        {"id": 6, "title": "Add circuit breaker on DB retry path"},
        {"id": 4, "title": "Enable auto-scale on app-checkout-01/02"},
        {"id": 2, "title": "PaymentGateway: Investigate Stripe 503 errors"},
        {"id": 3, "title": "Post-incident review: CheckoutService Sev1 outage"},
    ],
}


# ============================================================================
# Agent implementations (mock mode — demonstrates the handoff flow)
# ============================================================================


def triage_agent(incident_description: str) -> dict[str, Any]:
    """
    TriageAgent: queries Azure Monitor for active alerts, classifies severity.
    In real mode this calls the Azure MCP Server's monitor_* tools.
    """
    print("=" * 70)
    print("🔍 TRIAGE AGENT — Classifying Incident")
    print("=" * 70)
    print(f"Input: {incident_description}\n")

    print("📊 Querying Azure MCP Server → monitor namespace...")
    for alert in MOCK_ALERTS:
        sev = alert["Severity"]
        svc = alert["ServiceName"]
        msg = alert["Message"]
        print(f"   ✓ [{sev}] {svc}: {msg}")

    classification = {
        "severity": "Sev1",
        "blast_radius": {
            "services": ["CheckoutService", "PaymentGateway"],
            "resources": [r for a in MOCK_ALERTS for r in a["AffectedResources"]],
            "customer_impact": "High — checkout flow is completely blocked",
        },
        "alerts": MOCK_ALERTS,
        "recommendation": "Escalate to DiagnosticsAgent for root-cause analysis",
    }

    print(f"\n🏷️  Classification: {classification['severity']}")
    print(f"💥 Blast Radius: {len(classification['blast_radius']['resources'])} resources across "
          f"{len(classification['blast_radius']['services'])} services")
    print(f"👥 Customer Impact: {classification['blast_radius']['customer_impact']}")
    print("\n➡️  HANDOFF → DiagnosticsAgent\n")
    return classification


def diagnostics_agent(triage_result: dict[str, Any]) -> dict[str, Any]:
    """
    DiagnosticsAgent: deep root-cause analysis via Application Insights + Log Analytics.
    In real mode this calls Azure MCP Server's applicationinsights_* and monitor_* tools.
    """
    print("=" * 70)
    print("🔬 DIAGNOSTICS AGENT — Root Cause Analysis")
    print("=" * 70)
    print(f"Received triage: {triage_result['severity']} incident, "
          f"{len(triage_result['blast_radius']['services'])} services affected\n")

    print("📋 Querying Azure MCP Server → applicationinsights namespace...")
    for log in MOCK_LOGS:
        print(f"   ✓ [{log['level']}] {log['service']}: {log['message']}")

    print("\n🔗 Correlating events...")
    print("   Timeline:")
    print("   T-15m: CheckoutService → DB connection pool exhausted")
    print("   T-14m: Cascading timeout errors → 342 failed orders")
    print("   T-12m: PaymentGateway → Stripe 503 (likely caused by retry storm)")
    print("   T-08m: NotificationService queue overflow (downstream effect)")

    root_cause = {
        "root_cause": "Database connection pool exhaustion in CheckoutService",
        "contributing_factors": [
            "Connection pool max size (50) insufficient for Black Friday traffic spike",
            "Missing circuit breaker on the DB retry path caused retry storm",
            "PaymentGateway 503 errors are a secondary effect of backend overload",
        ],
        "recommended_fix": (
            "1. Increase connection pool max size to 200\n"
            "2. Add circuit breaker on DB retry path\n"
            "3. Enable auto-scale on app-checkout-01/02"
        ),
        "logs": MOCK_LOGS,
        "triage": triage_result,
    }

    print(f"\n🎯 Root Cause: {root_cause['root_cause']}")
    print("📝 Contributing Factors:")
    for f in root_cause["contributing_factors"]:
        print(f"   • {f}")
    print(f"\n💡 Recommended Fix:\n{root_cause['recommended_fix']}")
    print("\n➡️  HANDOFF → RemediationAgent\n")
    return root_cause


def remediation_agent(diagnostics_result: dict[str, Any]) -> dict[str, Any]:
    """
    RemediationAgent: creates work item in Azure DevOps, looks up on-call via
    Enterprise MCP (Graph), assigns the ticket, and produces final summary.
    """
    print("=" * 70)
    print("🛠️  REMEDIATION AGENT — Driving Resolution")
    print("=" * 70)
    print(f"Root cause: {diagnostics_result['root_cause']}\n")

    # Step 1: Reference real ADO work item (created during setup)
    print("📋 Referencing Issue in Azure DevOps (mcp-demo)...")
    wi = MOCK_WORKITEM
    print(f"   ✓ Issue #{wi['id']}: {wi['title']}")
    print(f"   ✓ URL: {wi['url']}")
    print(f"   ✓ State: {wi['state']}  |  Type: {wi.get('type', 'Issue')}")
    if wi.get("childTasks"):
        print(f"   ✓ Linked tasks: {len(wi['childTasks'])}")
        for task in wi["childTasks"]:
            print(f"       • Task #{task['id']}: {task['title']}")

    # Step 2: Find on-call engineer (Enterprise MCP → Microsoft Graph)
    print("\n👤 Querying Enterprise MCP → microsoft_graph_get...")
    oc = MOCK_ONCALL
    print(f"   ✓ On-call: {oc['displayName']} ({oc['mail']})")
    print(f"   ✓ Role: {oc['jobTitle']}, Team: {oc['team']}")

    # Step 3: Assign work item
    print(f"\n✅ Assigning Issue #{wi['id']} to {oc['displayName']}...")
    print(f"   ✓ Work item assigned to {oc['mail']}")

    summary = {
        "status": "Incident response complete",
        "severity": diagnostics_result["triage"]["severity"],
        "root_cause": diagnostics_result["root_cause"],
        "work_item": wi,
        "assigned_to": oc,
        "recommended_fix": diagnostics_result["recommended_fix"],
        "next_steps": [
            f"Engineer {oc['displayName']} to apply connection pool fix",
            "Deploy hotfix via app-checkout-01/02 slots",
            "Post-incident review scheduled for tomorrow",
        ],
    }

    print("\n" + "=" * 70)
    print("📊 INCIDENT RESPONSE SUMMARY")
    print("=" * 70)
    print(f"Severity:    {summary['severity']}")
    print(f"Root Cause:  {summary['root_cause']}")
    print(f"Work Item:   Issue #{wi['id']} — {wi['title']}")
    print(f"Assigned To: {oc['displayName']} ({oc['mail']})")
    print(f"Status:      {wi['state']}")
    print(f"ADO URL:     {wi['url']}")
    print("\nNext Steps:")
    for i, step in enumerate(summary["next_steps"], 1):
        print(f"   {i}. {step}")

    return summary


# ============================================================================
# Handoff Orchestrator
# ============================================================================


def run_handoff_orchestration(incident: str) -> dict[str, Any]:
    """
    Executes the Handoff Orchestration pattern:
      TriageAgent → DiagnosticsAgent → RemediationAgent

    Each agent processes its step and passes context to the next.
    """
    print()
    print("╔" + "═" * 68 + "╗")
    print("║  SCENARIO 3: MULTI-AGENT INCIDENT REMEDIATION                     ║")
    print("║  Pattern: Semantic Kernel Handoff Orchestration                    ║")
    print("╚" + "═" * 68 + "╝")
    print(f"\nMode: {'MOCK DATA' if USE_MOCK_DATA else 'LIVE — Azure MCP Server + Enterprise MCP'}")
    print(f"Incident: {incident}\n")

    # Step 1 — Triage
    triage_result = triage_agent(incident)

    # Step 2 — Diagnostics
    diagnostics_result = diagnostics_agent(triage_result)

    # Step 3 — Remediation
    final_result = remediation_agent(diagnostics_result)

    print("\n" + "=" * 70)
    print("✅ SCENARIO 3 — MULTI-AGENT INCIDENT REMEDIATION COMPLETE")
    print("=" * 70)
    print("Agents involved: TriageAgent → DiagnosticsAgent → RemediationAgent")
    print(f"Total handoffs:  2")
    print(f"Outcome:         Issue #{final_result['work_item']['id']} assigned to "
          f"{final_result['assigned_to']['displayName']}")
    print("=" * 70)

    return final_result


# ============================================================================
# Semantic Kernel Handoff Orchestration (real mode)
# ============================================================================


async def run_sk_handoff_orchestration(incident: str) -> dict[str, Any]:
    """
    Real-mode orchestration using Semantic Kernel Agent Framework.
    Requires: pip install semantic-kernel[agents]
    Environment: AZURE_OPENAI_ENDPOINT, AZURE_OPENAI_DEPLOYMENT
    """
    try:
        from semantic_kernel import Kernel
        from semantic_kernel.agents import ChatCompletionAgent
        from semantic_kernel.agents.orchestration.handoffs import (
            HandoffOrchestration,
            OrchestrationHandoffs,
        )
        from semantic_kernel.agents.runtime import InProcessRuntime
        from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion
    except ImportError:
        print("⚠ semantic-kernel[agents] not installed. Run: pip install semantic-kernel[agents]")
        print("  Falling back to mock orchestration.\n")
        return run_handoff_orchestration(incident)

    endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
    deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT")

    if not endpoint or not deployment:
        print("⚠ AZURE_OPENAI_ENDPOINT / AZURE_OPENAI_DEPLOYMENT not set.")
        print("  Falling back to mock orchestration.\n")
        return run_handoff_orchestration(incident)

    # Build Semantic Kernel with Azure OpenAI
    kernel = Kernel()
    kernel.add_service(
        AzureChatCompletion(
            deployment_name=deployment,
            endpoint=endpoint,
        )
    )

    # Define agents with specialized system prompts
    triage = ChatCompletionAgent(
        kernel=kernel,
        name="TriageAgent",
        instructions=(
            "You are a Triage Agent. Classify the incident severity (Sev1-Sev4), "
            "identify the blast radius, and hand off to DiagnosticsAgent."
        ),
    )

    diagnostics = ChatCompletionAgent(
        kernel=kernel,
        name="DiagnosticsAgent",
        instructions=(
            "You are a Diagnostics Agent. Perform root-cause analysis using log "
            "correlation and dependency analysis. Hand off to RemediationAgent "
            "with your findings."
        ),
    )

    remediation = ChatCompletionAgent(
        kernel=kernel,
        name="RemediationAgent",
        instructions=(
            "You are a Remediation Agent. Create a work item for the incident, "
            "identify the on-call engineer, assign the ticket, and produce a "
            "final incident response summary. You are the terminal agent."
        ),
    )

    # Configure handoff rules
    handoffs = OrchestrationHandoffs(
        handoffs={
            triage: [diagnostics],
            diagnostics: [remediation, triage],
            remediation: [],  # terminal
        }
    )

    # Create the handoff orchestration
    orchestration = HandoffOrchestration(
        members=[triage, diagnostics, remediation],
        handoffs=handoffs,
    )

    # Run with in-process runtime
    runtime = InProcessRuntime()
    runtime.start()

    result = await orchestration.invoke(
        task=f"Handle this incident: {incident}",
        runtime=runtime,
    )

    await runtime.stop_when_idle()

    value = await result.get()
    print("\n📊 Semantic Kernel Handoff Orchestration Result:")
    print(str(value))

    return {"sk_result": str(value)}


# ============================================================================
# Entry point
# ============================================================================


def main():
    parser = argparse.ArgumentParser(
        description="Scenario 3: Multi-Agent Incident Remediation"
    )
    parser.add_argument(
        "--incident",
        default=(
            "CheckoutService is returning 500 errors and database connections "
            "are timing out. Payment processing is also failing."
        ),
        help="Incident description to process",
    )
    parser.add_argument(
        "--real",
        action="store_true",
        help="Use Semantic Kernel with real Azure OpenAI (requires SK + env vars)",
    )
    args = parser.parse_args()

    if args.real and not USE_MOCK_DATA:
        asyncio.run(run_sk_handoff_orchestration(args.incident))
    else:
        run_handoff_orchestration(args.incident)


if __name__ == "__main__":
    main()
