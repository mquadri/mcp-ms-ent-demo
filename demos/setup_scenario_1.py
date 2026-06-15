# File: demos/setup_scenario_1.py
"""
Scenario 1: Automated Incident Response
- Seeds Azure Monitor with critical alerts
- Creates sample log data
- Configures DevOps project for incident creation
"""

import json
import os
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Any
import sys

# ============================================================================
# Configuration
# ============================================================================

SUBSCRIPTION_ID = os.getenv("AZURE_SUBSCRIPTION_ID")
RESOURCE_GROUP = os.getenv("AZURE_RESOURCE_GROUP", "contoso-monitoring")
LOG_ANALYTICS_WORKSPACE_ID = os.getenv("LOG_ANALYTICS_WORKSPACE_ID")

DEVOPS_ORG_URL = os.getenv("AZURE_DEVOPS_ORG_URL", "https://dev.azure.com/contoso-org")
DEVOPS_PROJECT = os.getenv("AZURE_DEVOPS_PROJECT", "ContosoApp")
DEVOPS_PAT = os.getenv("AZURE_DEVOPS_PAT")

GRAPH_TENANT_ID = os.getenv("AZURE_TENANT_ID")
GRAPH_CLIENT_ID = os.getenv("AZURE_CLIENT_ID")
GRAPH_CLIENT_SECRET = os.getenv("AZURE_CLIENT_SECRET")

# Mock mode flag
USE_MOCK_DATA = os.getenv("USE_MOCK_DATA", "true").lower() == "true"

# ============================================================================
# 1. Seed Azure Monitor with Critical Alerts
# ============================================================================

def seed_azure_monitor_alerts() -> List[Dict[str, Any]]:
    """
    Injects synthetic critical alerts into Azure Monitor.
    In mock mode, returns simulated alert data.
    In production mode, uses LogsQueryClient.
    """
    
    alerts = [
        {
            "AlertId": "alert-001",
            "ServiceName": "CheckoutService",
            "Severity": "Critical",
            "Message": "Database connection timeout - unable to process orders",
            "AffectedResources": ["sql-checkout-db", "app-checkout-01", "app-checkout-02"],
            "ErrorCode": "CONN_TIMEOUT_5000",
            "Timestamp": (datetime.now(timezone.utc) - timedelta(minutes=15)).isoformat(),
            "IncidentCount": 342
        },
        {
            "AlertId": "alert-002",
            "ServiceName": "PaymentGateway",
            "Severity": "Critical",
            "Message": "Payment processor API returning 503 errors",
            "AffectedResources": ["payment-gateway-01", "payment-gateway-02"],
            "ErrorCode": "EXT_API_ERROR_503",
            "Timestamp": (datetime.now(timezone.utc) - timedelta(minutes=12)).isoformat(),
            "IncidentCount": 127
        },
        {
            "AlertId": "alert-003",
            "ServiceName": "NotificationService",
            "Severity": "Error",
            "Message": "Email queue backing up - 50K+ undelivered messages",
            "AffectedResources": ["queue-notifications", "email-service-01"],
            "ErrorCode": "QUEUE_OVERFLOW",
            "Timestamp": (datetime.now(timezone.utc) - timedelta(minutes=8)).isoformat(),
            "IncidentCount": 89
        }
    ]
    
    if not USE_MOCK_DATA:
        try:
            from azure.identity import DefaultAzureCredential
            from azure.monitor.query import LogsQueryClient
            
            credential = DefaultAzureCredential()
            logs_client = LogsQueryClient(credential)
            print("✓ Using real Azure Monitor connection")
        except Exception as e:
            print(f"⚠ Could not connect to real Azure Monitor: {e}")
            print("  Falling back to mock data")
    
    print("📊 Seeding Azure Monitor with critical alerts...")
    for alert in alerts:
        print(f"   ✓ Alert {alert['AlertId']}: {alert['ServiceName']} - {alert['Message']}")
    
    return alerts


def seed_application_logs() -> List[Dict[str, Any]]:
    """
    Injects application error logs into Azure Monitor.
    These will be queried by the incident response scenario.
    """
    logs = [
        {
            "level": "ERROR",
            "service": "CheckoutService",
            "message": "Database query timeout after 5000ms",
            "stack_trace": "at CheckoutService.ProcessOrder (line 234)\n  at PaymentProcessor.Execute (line 156)",
            "request_id": "req-9921-8839",
            "user_id": "user-5502",
            "timestamp": (datetime.now(timezone.utc) - timedelta(minutes=14)).isoformat()
        },
        {
            "level": "ERROR",
            "service": "PaymentGateway",
            "message": "External API unreachable: Stripe gateway returns 503",
            "error_code": "STRIPE_503",
            "request_id": "req-9921-8840",
            "user_id": "user-5503",
            "timestamp": (datetime.now(timezone.utc) - timedelta(minutes=11)).isoformat()
        },
        {
            "level": "ERROR",
            "service": "CheckoutService",
            "message": "Connection pool exhausted, unable to allocate new connection",
            "error_code": "CONN_POOL_EXHAUSTED",
            "request_id": "req-9921-8841",
            "user_id": "user-5504",
            "timestamp": (datetime.now(timezone.utc) - timedelta(minutes=10)).isoformat()
        }
    ]
    
    print("📋 Seeding application error logs...")
    for log in logs:
        print(f"   ✓ {log['service']}: {log['message']}")
    
    return logs


# ============================================================================
# 2. Create Azure DevOps Incident Ticket
# ============================================================================

def create_devops_incident_ticket(
    title: str,
    description: str,
    severity: str = "1 - Critical",
    area_path: str = "ContosoApp\\Platform\\Backend",
    iteration_path: str = "ContosoApp\\Sprint 24"
) -> Dict[str, Any]:
    """
    Creates a new incident/bug work item in Azure DevOps.
    In mock mode, returns simulated ticket data.
    In production mode, uses azure-devops SDK.
    
    Args:
        title: Work item title
        description: Detailed description
        severity: Priority level (1-4, where 1 is critical)
        area_path: Area classification
        iteration_path: Sprint assignment
    
    Returns:
        Created work item details
    """
    
    # Generate mock work item ID
    import random
    mock_id = random.randint(10000, 99999)
    
    if not USE_MOCK_DATA:
        try:
            from azure.identity import DefaultAzureCredential
            from azure.devops.connection import Connection
            from azure.devops.v7_0.work_item_tracking.models import JsonPatchOperation
            
            credentials = {'PAT': DEVOPS_PAT}
            connection = Connection(base_url=DEVOPS_ORG_URL, creds=credentials)
            wit_client = connection.clients.get_work_item_tracking_client()
            
            patch_operations = [
                JsonPatchOperation(op="add", path="/fields/System.Title", value=title),
                JsonPatchOperation(op="add", path="/fields/System.Description", value=description),
                JsonPatchOperation(op="add", path="/fields/System.AreaPath", value=area_path),
                JsonPatchOperation(op="add", path="/fields/System.IterationPath", value=iteration_path),
                JsonPatchOperation(op="add", path="/fields/Microsoft.VSTS.Common.Severity", value=severity),
                JsonPatchOperation(op="add", path="/fields/System.Tags", value="incident;auto-generated;critical"),
                JsonPatchOperation(op="add", path="/fields/Microsoft.VSTS.Common.Priority", value="1")
            ]
            
            work_item = wit_client.create_work_item(
                patch_operations,
                project=DEVOPS_PROJECT,
                type="Bug"
            )
            
            print(f"✅ Created DevOps work item: {work_item.id} - {work_item.fields.get('System.Title')}")
            
            return {
                "id": work_item.id,
                "title": work_item.fields.get('System.Title'),
                "url": work_item.url,
                "state": work_item.fields.get('System.State')
            }
        except Exception as e:
            print(f"⚠ Could not create real DevOps ticket: {e}")
            print("  Using mock data instead")
    
    mock_ticket = {
        "id": mock_id,
        "title": title,
        "url": f"{DEVOPS_ORG_URL}/{DEVOPS_PROJECT}/_workitems/edit/{mock_id}",
        "state": "New"
    }
    
    print(f"✅ [MOCK] Created DevOps work item: {mock_ticket['id']} - {title}")
    
    return mock_ticket


# ============================================================================
# 3. Query On-Call Engineer from Microsoft Graph
# ============================================================================

def get_oncall_engineer_info(team_name: str = "Platform") -> Dict[str, str]:
    """
    Fetches on-call engineer information from Microsoft Graph.
    In mock mode, returns simulated team member data.
    """
    
    oncall_engineers = {
        "Platform": {
            "name": "Ahmed Hassan",
            "email": "ahmed.hassan@contoso.com",
            "phone": "+1-206-555-0123",
            "team": "Platform Engineering"
        },
        "Payment": {
            "name": "Sarah Chen",
            "email": "sarah.chen@contoso.com",
            "phone": "+1-206-555-0124",
            "team": "Payment Systems"
        },
        "Notifications": {
            "name": "Marcus Johnson",
            "email": "marcus.johnson@contoso.com",
            "phone": "+1-206-555-0125",
            "team": "Communications"
        }
    }
    
    if not USE_MOCK_DATA:
        try:
            from azure.identity import DefaultAzureCredential
            from msgraph.core import GraphClient
            
            credential = DefaultAzureCredential()
            graph_client = GraphClient(credential=credential)
            print("✓ Using real Microsoft Graph connection")
        except Exception as e:
            print(f"⚠ Could not connect to real Microsoft Graph: {e}")
    
    engineer = oncall_engineers.get(team_name, oncall_engineers["Platform"])
    print(f"📞 On-call engineer: {engineer['name']} ({engineer['email']})")
    
    return engineer


# ============================================================================
# 4. Assign Work Item to On-Call Engineer
# ============================================================================

def assign_work_item_to_oncall(
    work_item_id: int,
    assignee_email: str
) -> Dict[str, Any]:
    """
    Assigns DevOps work item to on-call engineer.
    In mock mode, returns simulated assignment data.
    """
    
    if not USE_MOCK_DATA:
        try:
            from azure.devops.connection import Connection
            from azure.devops.v7_0.work_item_tracking.models import JsonPatchOperation
            
            credentials = {'PAT': DEVOPS_PAT}
            connection = Connection(base_url=DEVOPS_ORG_URL, creds=credentials)
            wit_client = connection.clients.get_work_item_tracking_client()
            
            patch_operations = [
                JsonPatchOperation(op="add", path="/fields/System.AssignedTo", value=assignee_email)
            ]
            
            updated_item = wit_client.update_work_item(
                patch_operations,
                id=work_item_id,
                project=DEVOPS_PROJECT
            )
            
            print(f"✅ Assigned work item {work_item_id} to {assignee_email}")
            
            return {
                "work_item_id": updated_item.id,
                "assigned_to": updated_item.fields.get('System.AssignedTo')
            }
        except Exception as e:
            print(f"⚠ Could not assign real DevOps ticket: {e}")
    
    print(f"✅ [MOCK] Assigned work item {work_item_id} to {assignee_email}")
    
    return {
        "work_item_id": work_item_id,
        "assigned_to": assignee_email
    }


# ============================================================================
# 5. Main Setup Execution
# ============================================================================

def run_scenario_1_setup():
    """
    Complete setup for Scenario 1: Automated Incident Response
    """
    print("\n" + "="*70)
    print("🚨 SCENARIO 1: AUTOMATED INCIDENT RESPONSE - SETUP")
    print("="*70)
    print(f"Mode: {'MOCK DATA' if USE_MOCK_DATA else 'REAL AZURE'}\n")
    
    # Step 1: Seed Azure Monitor alerts
    alerts = seed_azure_monitor_alerts()
    print()
    
    # Step 2: Seed application logs
    logs = seed_application_logs()
    print()
    
    # Step 3: Create DevOps incident ticket
    incident_description = """## Critical Incident Summary

**Primary Alert:** CheckoutService database connection timeout

**Details:**
- Service: CheckoutService
- Error: Database query timeout after 5000ms
- Affected Resources: sql-checkout-db, app-checkout-01, app-checkout-02
- Impact: 342 failed transactions in last 15 minutes
- Secondary Impact: PaymentGateway also affected (127 failures)

**Status:** ACTIVE - Requires immediate investigation

**Trending:** Failures increasing exponentially over last 20 minutes

**Error Pattern:**
1. 14:45 UTC - Initial timeout spike detected
2. 14:48 UTC - Connection pool exhaustion errors
3. 14:52 UTC - Cascading failures to payment gateway
4. 14:55 UTC - Alert threshold triggered
"""
    
    ticket = create_devops_incident_ticket(
        title="CRITICAL: Checkout Service - Database Connection Timeout",
        description=incident_description,
        severity="1 - Critical",
        area_path="ContosoApp\\Platform\\Backend\\Database"
    )
    print()
    
    # Step 4: Get on-call engineer
    oncall = get_oncall_engineer_info(team_name="Platform")
    print()
    
    # Step 5: Assign ticket to on-call
    assignment = assign_work_item_to_oncall(
        work_item_id=ticket["id"],
        assignee_email=oncall["email"]
    )
    print()
    
    # Step 6: Print summary
    print("\n" + "="*70)
    print("✅ SCENARIO 1 SETUP COMPLETE")
    print("="*70)
    print(f"""
Incident Summary:
  - Alerts Seeded: {len(alerts)}
  - Error Logs Seeded: {len(logs)}
  - DevOps Ticket Created: #{ticket['id']}
  - Ticket State: {ticket['state']}
  - Assigned To: {oncall['name']} ({oncall['email']})
  
Sample Alert:
  - ID: {alerts[0]['AlertId']}
  - Service: {alerts[0]['ServiceName']}
  - Severity: {alerts[0]['Severity']}
  - Impact: {alerts[0]['IncidentCount']} incidents
  
Next Steps (For Copilot Testing):
  1. Ask Copilot: "Fetch critical alerts from last hour"
  2. Request: "Create incident ticket in DevOps for CheckoutService"
  3. Query: "Who is the on-call engineer for Platform team?"
  4. Verify: "Assign ticket #{ticket['id']} to on-call"
  
DevOps URL: {ticket['url']}
""")
    
    return {
        "alerts": alerts,
        "logs": logs,
        "ticket": ticket,
        "oncall_engineer": oncall,
        "assignment": assignment
    }


if __name__ == "__main__":
    try:
        setup_data = run_scenario_1_setup()
        print("\n" + "="*70)
        print("💾 Setup data saved. Ready for Copilot testing!")
        print("="*70)
    except Exception as e:
        print(f"\n❌ Error during setup: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)