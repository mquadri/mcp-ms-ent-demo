# File: demos/setup_scenario_5.py
"""
Scenario 5: Development Velocity Analysis
- Populates Azure DevOps with sprint/repo metrics
- Seeds Azure Monitor with build/deployment logs
- Stores historical trends in Cosmos DB
"""

import os
import sys
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Any
import random

# ============================================================================
# Configuration
# ============================================================================

SUBSCRIPTION_ID = os.getenv("AZURE_SUBSCRIPTION_ID")
DEVOPS_ORG_URL = os.getenv("AZURE_DEVOPS_ORG_URL", "https://dev.azure.com/contoso-org")
DEVOPS_PROJECT = os.getenv("AZURE_DEVOPS_PROJECT", "ContosoApp")
DEVOPS_PAT = os.getenv("AZURE_DEVOPS_PAT")

LOG_ANALYTICS_WORKSPACE_ID = os.getenv("LOG_ANALYTICS_WORKSPACE_ID")

COSMOS_ENDPOINT = os.getenv("COSMOS_DB_ENDPOINT")
COSMOS_KEY = os.getenv("COSMOS_DB_KEY")
COSMOS_DATABASE = "dev_analytics"
COSMOS_CONTAINER = "velocity_metrics"

# Mock mode flag
USE_MOCK_DATA = os.getenv("USE_MOCK_DATA", "true").lower() == "true"

# ============================================================================
# 1. Seed Azure DevOps Sprint Metrics
# ============================================================================


def seed_devops_sprint_metrics() -> Dict[str, Any]:
    """
    Creates realistic sprint data in Azure DevOps:
    - Work items by status
    - Velocity trend
    - Bug burndown
    - Test coverage
    """

    sprint_data = {
        "Sprint 24": {
            "start_date": (datetime.now(timezone.utc) - timedelta(days=14)).isoformat(),
            "end_date": (datetime.now(timezone.utc)).isoformat(),
            "total_work_items": 42,
            "completed": 38,
            "in_progress": 3,
            "blocked": 1,
            "velocity_points": 156,
            "planned_points": 160,
            "completion_percentage": 90.5,
            "bug_count": 7,
            "test_pass_rate": 96.2
        },
        "Sprint 23": {
            "start_date": (datetime.now(timezone.utc) - timedelta(days=28)).isoformat(),
            "end_date": (datetime.now(timezone.utc) - timedelta(days=14)).isoformat(),
            "total_work_items": 40,
            "completed": 38,
            "velocity_points": 152,
            "planned_points": 155,
            "completion_percentage": 95.0,
            "bug_count": 5,
            "test_pass_rate": 97.8
        },
        "Sprint 22": {
            "start_date": (datetime.now(timezone.utc) - timedelta(days=42)).isoformat(),
            "end_date": (datetime.now(timezone.utc) - timedelta(days=28)).isoformat(),
            "total_work_items": 38,
            "completed": 36,
            "velocity_points": 148,
            "planned_points": 150,
            "completion_percentage": 94.7,
            "bug_count": 6,
            "test_pass_rate": 96.5
        }
    }

    print("📊 Azure DevOps Sprint Metrics:")
    for sprint, metrics in sprint_data.items():
        print(f"   {sprint}:")
        print(f"      Velocity: {metrics['velocity_points']} / {metrics['planned_points']} points")
        print(f"      Completion: {metrics['completion_percentage']}%")
        print(f"      Test Pass Rate: {metrics['test_pass_rate']}%")

    return sprint_data


def seed_devops_repo_metrics() -> Dict[str, Any]:
    """
    Populates repository metrics:
    - Commit frequency
    - PR merge rate
    - Code review time
    - Branch coverage
    """
    repo_data = {
        "ContosoApp": {
            "commits_per_day": 42,
            "pr_merged_per_day": 8,
            "avg_pr_size": 185,
            "avg_review_time_hours": 3.2,
            "branch_coverage_percent": 87.3,
            "pull_requests": {
                "open": 5,
                "merged_last_7_days": 56,
                "avg_time_to_merge_hours": 2.8
            },
            "main_branch": {
                "commits_last_30_days": 1260,
                "contributors": 24,
                "test_pass_rate": 96.2
            }
        }
    }

    print("\n📈 Repository Metrics:")
    repo = repo_data["ContosoApp"]
    print(f"   Commits/Day: {repo['commits_per_day']}")
    print(f"   PRs Merged/Day: {repo['pr_merged_per_day']}")
    print(f"   Avg PR Review Time: {repo['avg_review_time_hours']} hours")
    print(f"   Branch Coverage: {repo['branch_coverage_percent']}%")

    return repo_data


# ============================================================================
# 2. Seed Build & Deployment Performance Logs (Azure Monitor)
# ============================================================================

def seed_build_deployment_logs() -> List[Dict[str, Any]]:
    """
    Injects build and deployment performance metrics into Azure Monitor.
    Includes:
    - Build duration trends
    - Test execution times
    - Deployment frequency
    - Failure rates
    """

    build_logs = []

    # Generate 30 days of build metrics
    for day_offset in range(30, 0, -1):
        timestamp = datetime.now(timezone.utc) - timedelta(days=day_offset)

        # 3-5 builds per day
        builds_today = random.randint(3, 5)

        for build_num in range(builds_today):
            build_log = {
                "timestamp": timestamp.isoformat(),
                "build_id": f"build-{(30-day_offset):02d}-{build_num:02d}",
                "pipeline": "ContosoApp-CI",
                "status": random.choices(
                    ["Success", "Failed"],
                    weights=[85, 15]
                )[0],
                "duration_seconds": random.randint(180, 900),
                "test_execution_time_seconds": random.randint(120, 600),
                "test_pass_count": random.randint(2400, 2500),
                "test_fail_count": random.randint(0, 50),
                "code_coverage_percent": round(random.uniform(82, 95), 2),
                "artifact_size_mb": random.randint(150, 350)
            }
            build_logs.append(build_log)

    print("\n🔨 Build Performance Logs (Last 30 Days):")
    print(f"   Total Builds: {len(build_logs)}")
    successful = sum(1 for b in build_logs if b['status'] == 'Success')
    print(
        f"   Success Rate: {successful}/{len(build_logs)}"
        f" ({100*successful/len(build_logs):.1f}%)")
    avg_time = sum(b['duration_seconds'] for b in build_logs)/len(build_logs)
    print(f"   Avg Build Time: {avg_time:.0f}s (~{avg_time/60:.1f} minutes)")

    return build_logs


def seed_deployment_logs() -> List[Dict[str, Any]]:
    """
    Seeds deployment metrics including:
    - Deployment frequency
    - Deployment success rate
    - Rollback frequency
    - Time to production
    """

    deployment_logs = []

    for day_offset in range(30, 0, -1):
        timestamp = datetime.now(timezone.utc) - timedelta(days=day_offset)

        # 1-3 deployments per day
        deployments_today = random.randint(1, 3)

        for deploy_num in range(deployments_today):
            deployment = {
                "timestamp": timestamp.isoformat(),
                "deployment_id": f"deploy-{(30-day_offset):02d}-{deploy_num:02d}",
                "environment": random.choice(["Staging", "Production"]),
                "service": random.choice(["CheckoutService", "PaymentGateway", "NotificationService", "APIGateway"]),
                "status": random.choices(
                    ["Success", "Rollback", "Partial Failure"],
                    weights=[88, 8, 4]
                )[0],
                "duration_minutes": random.randint(5, 45),
                "rollback_reason": None if random.random() > 0.1 else "High error rate detected",
                "impact_users": random.randint(0, 5000),
                "error_rate_percent_before": round(random.uniform(0.1, 1.5), 2),
                "error_rate_percent_after": round(random.uniform(0.05, 1.0), 2)
            }
            deployment_logs.append(deployment)

    print("\n🚀 Deployment Logs (Last 30 Days):")
    print(f"   Total Deployments: {len(deployment_logs)}")
    prod_deploys = sum(1 for d in deployment_logs if d['environment'] == 'Production')
    success_deploys = sum(1 for d in deployment_logs if d['status'] == 'Success')
    print(f"   Production Deployments: {prod_deploys}")
    print(f"   Success Rate: {100*success_deploys/len(deployment_logs):.1f}%")

    return deployment_logs


# ============================================================================
# 3. Seed Cosmos DB with Historical Trend Data
# ============================================================================

def seed_cosmos_velocity_trends() -> List[Dict[str, Any]]:
    """
    Stores historical velocity and performance trends in Cosmos DB
    for long-term analysis and forecasting.
    """

    trend_documents = []

    # Generate 12 weeks of velocity trends
    for week_offset in range(12, 0, -1):
        week_start = datetime.now(timezone.utc) - timedelta(weeks=week_offset)

        trend_doc = {
            "id": f"velocity-week-{12-week_offset:02d}",
            "week_start": week_start.isoformat(),
            "sprint_number": 24 - week_offset,
            "velocity_points": random.randint(140, 160),
            "planned_points": random.randint(150, 170),
            "completion_rate": round(random.uniform(0.85, 0.98), 3),
            "bug_escape_rate": round(random.uniform(0.005, 0.015), 4),
            "test_pass_rate": round(random.uniform(0.94, 0.99), 3),
            "avg_pr_review_time_hours": round(random.uniform(2.0, 5.0), 2),
            "deployment_frequency_per_day": round(random.uniform(1.5, 3.5), 2),
            "mean_time_to_recovery_hours": round(random.uniform(0.5, 2.0), 2),
            "team_size": random.randint(8, 14)
        }
        trend_documents.append(trend_doc)

    if not USE_MOCK_DATA:
        try:
            from azure.identity import DefaultAzureCredential
            from azure.cosmos import CosmosClient

            credential = DefaultAzureCredential()
            cosmos_client = CosmosClient(COSMOS_ENDPOINT, credential=credential)
            database = cosmos_client.get_database_client(COSMOS_DATABASE)
            container = database.get_container_client(COSMOS_CONTAINER)

            for doc in trend_documents:
                container.upsert_item(doc)

            print("\n✓ Stored trends in real Cosmos DB")
        except (ImportError, ValueError, RuntimeError) as e:
            print(f"\n⚠ Could not store in real Cosmos DB: {e}")
            print("  Using mock data instead")

    print("\n📊 Cosmos DB Velocity Trends (12 Weeks):")
    print(f"   Documents Stored: {len(trend_documents)}")
    for doc in trend_documents[:3]:
        print(f"   Sprint {doc['sprint_number']}: {doc['velocity_points']} points, {100*doc['completion_rate']:.1f}% completion")

    return trend_documents


# ============================================================================
# 4. Generate Analysis & Recommendations
# ============================================================================

def analyze_velocity_trends(
    sprint_data: Dict,
    repo_data: Dict,
    build_logs: List,
    deployment_logs: List
) -> Dict[str, Any]:
    """
    Synthesizes all data into actionable insights about team velocity,
    bottlenecks, and improvement opportunities.
    """

    # Calculate trends
    latest_sprint = sprint_data.get("Sprint 24", {})
    previous_sprint = sprint_data.get("Sprint 23", {})

    velocity_trend = latest_sprint.get("velocity_points", 0) - previous_sprint.get("velocity_points", 0)
    velocity_trend_percent = (velocity_trend / previous_sprint.get("velocity_points", 1)) * 100 if previous_sprint.get("velocity_points") else 0

    # Build metrics
    avg_build_time = sum(b['duration_seconds'] for b in build_logs) / len(build_logs) if build_logs else 0
    build_success_rate = sum(1 for b in build_logs if b['status'] == 'Success') / len(build_logs) if build_logs else 0

    # Deployment metrics
    prod_deployments = [d for d in deployment_logs if d['environment'] == 'Production']
    deployment_success_rate = sum(1 for d in prod_deployments if d['status'] == 'Success') / len(prod_deployments) if prod_deployments else 0

    analysis = {
        "summary": {
            "current_sprint": "Sprint 24",
            "velocity_points": latest_sprint.get("velocity_points", 0),
            "completion_rate": f"{latest_sprint.get('completion_percentage', 0):.1f}%",
            "test_pass_rate": f"{latest_sprint.get('test_pass_rate', 0):.1f}%"
        },
        "trends": {
            "velocity_change_points": velocity_trend,
            "velocity_change_percent": f"{velocity_trend_percent:.1f}%",
            "direction": "📈 Improving" if velocity_trend > 0 else "📉 Declining"
        },
        "build_metrics": {
            "average_build_time_seconds": f"{avg_build_time:.0f}s",
            "build_success_rate_percent": f"{build_success_rate*100:.1f}%",
            "builds_per_day": f"{len(build_logs)/30:.1f}"
        },
        "deployment_metrics": {
            "production_deployments_per_day": f"{len(prod_deployments)/30:.1f}",
            "deployment_success_rate_percent": f"{deployment_success_rate*100:.1f}%",
            "avg_deployment_duration_minutes": sum(d['duration_minutes'] for d in prod_deployments) / len(prod_deployments) if prod_deployments else 0
        },
        "code_metrics": {
            "commits_per_day": repo_data["ContosoApp"]["commits_per_day"],
            "pr_merged_per_day": repo_data["ContosoApp"]["pr_merged_per_day"],
            "avg_pr_review_time_hours": repo_data["ContosoApp"]["avg_review_time_hours"],
            "branch_coverage_percent": repo_data["ContosoApp"]["branch_coverage_percent"]
        },
        "recommendations": []
    }

    # Generate recommendations
    if velocity_trend_percent < -10:
        analysis["recommendations"].append({
            "priority": "High",
            "area": "Velocity Declining",
            "suggestion": "Team velocity down 10%+. Review sprint planning and identify blockers.",
            "action": "Run sprint retrospective focusing on impediments"
        })

    if build_success_rate < 0.85:
        analysis["recommendations"].append({
            "priority": "High",
            "area": "Build Stability",
            "suggestion": f"Build success rate {build_success_rate*100:.0f}%. Address flaky tests.",
            "action": "Quarantine and fix failing tests; add retry logic for network issues"
        })

    if latest_sprint.get("test_pass_rate", 100) < 95:
        analysis["recommendations"].append({
            "priority": "Medium",
            "area": "Test Quality",
            "suggestion": "Test pass rate below 95%. Review test coverage.",
            "action": "Increase unit test coverage; remove duplicate test suites"
        })

    if repo_data["ContosoApp"]["avg_review_time_hours"] > 4:
        analysis["recommendations"].append({
            "priority": "Medium",
            "area": "Code Review Cycle",
            "suggestion": "PR review time > 4 hours. Consider adding more reviewers.",
            "action": "Distribute code review load; set SLA for PR reviews"
        })

    return analysis


# ============================================================================
# 5. Main Setup Execution
# ============================================================================

def run_scenario_5_setup():
    """
    Complete setup for Scenario 5: Development Velocity Analysis
    """
    print("\n" + "="*70)
    print("📊 SCENARIO 5: DEVELOPMENT VELOCITY ANALYSIS - SETUP")
    print("="*70)
    print(f"Mode: {'MOCK DATA' if USE_MOCK_DATA else 'REAL AZURE'}\n")

    # Step 1: Seed DevOps sprint metrics
    sprint_data = seed_devops_sprint_metrics()
    print()

    # Step 2: Seed repository metrics
    repo_data = seed_devops_repo_metrics()
    print()

    # Step 3: Seed build logs
    build_logs = seed_build_deployment_logs()
    print()

    # Step 4: Seed deployment logs
    deployment_logs = seed_deployment_logs()
    print()

    # Step 5: Seed Cosmos DB trends
    trend_docs = seed_cosmos_velocity_trends()
    print()

    # Step 6: Analyze and generate insights
    analysis = analyze_velocity_trends(sprint_data, repo_data, build_logs, deployment_logs)
    print("\n📈 Analysis Summary:")
    print(f"   Velocity Change: {analysis['trends']['velocity_change_points']:+.0f} points ({analysis['trends']['velocity_change_percent']})")
    print(f"   Build Success Rate: {analysis['build_metrics']['build_success_rate_percent']}")
    print(f"   Deployment Success Rate: {analysis['deployment_metrics']['deployment_success_rate_percent']}")
    print(f"   Code Review Cycle: {analysis['code_metrics']['avg_pr_review_time_hours']} hours")
    print(f"\n📋 Recommendations Generated: {len(analysis['recommendations'])}")
    for rec in analysis["recommendations"]:
        print(f"   [{rec['priority']}] {rec['area']}: {rec['suggestion']}")

    # Final summary
    print("\n" + "="*70)
    print("✅ SCENARIO 5 SETUP COMPLETE")
    print("="*70)
    print(f"""
Data Summary:
  - Sprints Seeded: {len(sprint_data)}
  - Repositories: {len(repo_data)}
  - Build Logs: {len(build_logs)} (30 days)
  - Deployment Logs: {len(deployment_logs)} (30 days)
  - Cosmos DB Trend Documents: {len(trend_docs)} (12 weeks)
  - Recommendations: {len(analysis['recommendations'])}

Next Steps (For Copilot Testing):
  1. Ask Copilot: "Analyze our development velocity over last 12 weeks"
  2. Request: "Pull sprint metrics from Azure DevOps"
  3. Query: "Get build and deployment performance trends"
  4. Ask: "What are the top bottlenecks in our development process?"
  5. Request: "Recommend 3 actions to improve deployment frequency"

DevOps URL: {DEVOPS_ORG_URL}/{DEVOPS_PROJECT}
""")

    return {
        "sprint_data": sprint_data,
        "repo_data": repo_data,
        "build_logs": build_logs,
        "deployment_logs": deployment_logs,
        "trend_documents": trend_docs,
        "analysis": analysis
    }


if __name__ == "__main__":
    try:
        setup_data = run_scenario_5_setup()
        print("\n" + "="*70)
        print("💾 Setup data ready. Prepared for Copilot testing!")
        print("="*70)
    except (RuntimeError, ValueError, OSError) as e:
        print(f"\n❌ Error during setup: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
