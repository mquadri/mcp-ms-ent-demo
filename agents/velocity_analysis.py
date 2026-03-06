# File: agents/velocity_analysis.py
"""
Scenario 5: Multi-Agent Development Velocity Analysis
======================================================
Demonstrates the Semantic Kernel Sequential Orchestration pattern where
three specialized agents form a pipeline to analyze development velocity:

  MetricsCollectorAgent → TrendAnalystAgent → AdvisorAgent

Each agent builds on the previous agent's output to produce an executive
velocity report with actionable recommendations.

This uses a DIFFERENT orchestration pattern from Scenario 3 (Handoff) to
demonstrate the breadth of the Microsoft Agent Framework.

Requirements:
  pip install semantic-kernel[agents]
  Environment: AZURE_OPENAI_ENDPOINT, AZURE_OPENAI_DEPLOYMENT

References:
  - https://learn.microsoft.com/en-us/semantic-kernel/frameworks/agent/agent-orchestration/sequential
  - https://learn.microsoft.com/en-us/azure/architecture/ai-ml/guide/ai-agent-design-patterns
"""

import asyncio
import argparse
import json
import os
import sys
from datetime import datetime, timedelta
from typing import Any

# ---------------------------------------------------------------------------
# Mock mode
# ---------------------------------------------------------------------------
USE_MOCK_DATA = os.getenv("USE_MOCK_DATA", "true").lower() == "true"

# ---------------------------------------------------------------------------
# Mock MCP tool responses
# ---------------------------------------------------------------------------

MOCK_SPRINT_METRICS = {
    "Sprint 24": {
        "start_date": (datetime.utcnow() - timedelta(days=14)).isoformat(),
        "end_date": datetime.utcnow().isoformat(),
        "total_work_items": 42,
        "completed": 38,
        "in_progress": 3,
        "blocked": 1,
        "velocity_points": 156,
        "planned_points": 160,
        "completion_percentage": 90.5,
        "bug_count": 7,
        "test_pass_rate": 96.2,
    },
    "Sprint 23": {
        "start_date": (datetime.utcnow() - timedelta(days=28)).isoformat(),
        "end_date": (datetime.utcnow() - timedelta(days=14)).isoformat(),
        "total_work_items": 40,
        "completed": 38,
        "velocity_points": 152,
        "planned_points": 155,
        "completion_percentage": 95.0,
        "bug_count": 5,
        "test_pass_rate": 97.8,
    },
    "Sprint 22": {
        "start_date": (datetime.utcnow() - timedelta(days=42)).isoformat(),
        "end_date": (datetime.utcnow() - timedelta(days=28)).isoformat(),
        "total_work_items": 38,
        "completed": 36,
        "velocity_points": 148,
        "planned_points": 150,
        "completion_percentage": 94.7,
        "bug_count": 6,
        "test_pass_rate": 96.5,
    },
}

MOCK_REPO_METRICS = {
    "commits_per_day": 42,
    "pr_merged_per_day": 8,
    "avg_pr_size_lines": 185,
    "avg_review_time_hours": 3.2,
    "branch_coverage_percent": 87.3,
    "open_prs": 5,
    "merged_last_7_days": 56,
    "contributors": 24,
}

MOCK_BUILD_SUMMARY = {
    "total_builds_30d": 118,
    "success_count": 100,
    "failed_count": 18,
    "success_rate_percent": 84.7,
    "avg_build_duration_seconds": 542,
    "avg_test_pass_rate": 95.1,
    "avg_code_coverage": 88.4,
    "slowest_build_seconds": 892,
    "fastest_build_seconds": 183,
}

MOCK_DEPLOYMENT_SUMMARY = {
    "total_deployments_30d": 58,
    "production_count": 28,
    "staging_count": 30,
    "success_rate_percent": 89.7,
    "rollback_count": 5,
    "rollback_rate_percent": 8.6,
    "avg_deployment_minutes": 22,
    "mean_time_to_recovery_hours": 1.3,
}

MOCK_COSMOS_TRENDS = [
    {
        "week": i + 1,
        "sprint_number": 13 + i,
        "velocity_points": 140 + i * 2 + (3 if i > 6 else 0),
        "planned_points": 150 + (i % 3) * 5,
        "completion_rate": round(0.88 + i * 0.008, 3),
        "bug_escape_rate": round(0.012 - i * 0.0005, 4),
        "deployment_frequency_per_day": round(1.8 + i * 0.12, 2),
        "mean_time_to_recovery_hours": round(1.8 - i * 0.08, 2),
        "team_size": 10 + (1 if i > 8 else 0),
    }
    for i in range(12)
]

MOCK_TEAM_MEMBERS = [
    {"displayName": "Priya Sharma", "jobTitle": "Engineering Manager", "mail": "priya.sharma@contoso.com"},
    {"displayName": "Marcus Chen", "jobTitle": "Staff Engineer", "mail": "marcus.chen@contoso.com"},
    {"displayName": "Elena Rodriguez", "jobTitle": "Senior Developer", "mail": "elena.rodriguez@contoso.com"},
]


# ============================================================================
# Agent implementations (mock mode)
# ============================================================================


def metrics_collector_agent() -> dict[str, Any]:
    """
    MetricsCollectorAgent: gathers raw data from DevOps, Monitor, and Cosmos DB.
    Uses Azure MCP Server (monitor, cosmos namespaces) and Azure DevOps REST API.
    """
    print("=" * 70)
    print("📥 METRICS COLLECTOR AGENT — Gathering Data")
    print("=" * 70)

    # Step 1: Sprint metrics from Azure DevOps
    print("\n📊 Querying Azure DevOps → Sprint metrics...")
    for sprint_name, metrics in MOCK_SPRINT_METRICS.items():
        print(f"   ✓ {sprint_name}: {metrics['velocity_points']}/{metrics['planned_points']} pts, "
              f"{metrics['completion_percentage']}% complete")

    # Step 2: Repo metrics from Azure DevOps
    print("\n📈 Querying Azure DevOps → Repository statistics...")
    rm = MOCK_REPO_METRICS
    print(f"   ✓ Commits/day: {rm['commits_per_day']}, PRs merged/day: {rm['pr_merged_per_day']}")
    print(f"   ✓ Avg review time: {rm['avg_review_time_hours']}h, Coverage: {rm['branch_coverage_percent']}%")

    # Step 3: Build logs from Azure Monitor
    print("\n🔨 Querying Azure MCP Server → monitor namespace (build logs)...")
    bs = MOCK_BUILD_SUMMARY
    print(f"   ✓ {bs['total_builds_30d']} builds, {bs['success_rate_percent']}% success rate")
    print(f"   ✓ Avg duration: {bs['avg_build_duration_seconds']}s, Avg coverage: {bs['avg_code_coverage']}%")

    # Step 4: Deployment logs from Azure Monitor
    print("\n🚀 Querying Azure MCP Server → monitor namespace (deployment logs)...")
    ds = MOCK_DEPLOYMENT_SUMMARY
    print(f"   ✓ {ds['total_deployments_30d']} deployments, {ds['production_count']} to production")
    print(f"   ✓ Success rate: {ds['success_rate_percent']}%, Rollback rate: {ds['rollback_rate_percent']}%")

    # Step 5: Historical trends from Cosmos DB
    print("\n📊 Querying Azure MCP Server → cosmos namespace (12-week trends)...")
    print(f"   ✓ Retrieved {len(MOCK_COSMOS_TRENDS)} weekly trend documents")
    first = MOCK_COSMOS_TRENDS[0]
    last = MOCK_COSMOS_TRENDS[-1]
    print(f"   ✓ Week 1: {first['velocity_points']} pts → Week 12: {last['velocity_points']} pts")

    collected_data = {
        "sprint_metrics": MOCK_SPRINT_METRICS,
        "repo_metrics": MOCK_REPO_METRICS,
        "build_summary": MOCK_BUILD_SUMMARY,
        "deployment_summary": MOCK_DEPLOYMENT_SUMMARY,
        "historical_trends": MOCK_COSMOS_TRENDS,
    }

    print("\n✅ Data collection complete — 5 data sources gathered")
    print("➡️  Passing to TrendAnalystAgent\n")
    return collected_data


def trend_analyst_agent(collected_data: dict[str, Any]) -> dict[str, Any]:
    """
    TrendAnalystAgent: performs statistical analysis, anomaly detection, and forecasting.
    Uses data from MetricsCollectorAgent — no direct MCP tool calls.
    """
    print("=" * 70)
    print("📊 TREND ANALYST AGENT — Analyzing Metrics")
    print("=" * 70)

    sprints = collected_data["sprint_metrics"]
    builds = collected_data["build_summary"]
    deploys = collected_data["deployment_summary"]
    trends = collected_data["historical_trends"]

    # Velocity trend analysis
    sprint_velocities = [s["velocity_points"] for s in sprints.values()]
    velocity_direction = sprint_velocities[0] - sprint_velocities[-1]
    velocity_pct = (velocity_direction / sprint_velocities[-1]) * 100

    print(f"\n📈 Velocity Trend Analysis:")
    print(f"   Sprint 22 → 24: {sprint_velocities[-1]} → {sprint_velocities[0]} pts "
          f"({velocity_pct:+.1f}%)")
    print(f"   Direction: {'📈 Accelerating' if velocity_direction > 0 else '📉 Decelerating'}")

    # Build stability analysis
    print(f"\n🔨 Build Stability:")
    print(f"   Success rate: {builds['success_rate_percent']}%")
    build_health = "🟢 Healthy" if builds["success_rate_percent"] >= 90 else (
        "🟡 Needs Attention" if builds["success_rate_percent"] >= 80 else "🔴 Critical"
    )
    print(f"   Status: {build_health}")
    print(f"   Avg duration: {builds['avg_build_duration_seconds'] / 60:.1f} min")

    # Deployment cadence
    deploy_freq = deploys["production_count"] / 30
    print(f"\n🚀 Deployment Cadence:")
    print(f"   Production deploys/day: {deploy_freq:.1f}")
    print(f"   Rollback rate: {deploys['rollback_rate_percent']}%")
    print(f"   MTTR: {deploys['mean_time_to_recovery_hours']}h")

    # 12-week trend analysis
    week1_vel = trends[0]["velocity_points"]
    week12_vel = trends[-1]["velocity_points"]
    trend_growth = ((week12_vel - week1_vel) / week1_vel) * 100

    print(f"\n📊 12-Week Historical Trend:")
    print(f"   Velocity: {week1_vel} → {week12_vel} pts ({trend_growth:+.1f}% growth)")
    print(f"   Completion rate: {trends[0]['completion_rate']*100:.1f}% → {trends[-1]['completion_rate']*100:.1f}%")
    print(f"   Bug escape rate: {trends[0]['bug_escape_rate']*100:.2f}% → {trends[-1]['bug_escape_rate']*100:.2f}%")

    # Anomaly detection
    anomalies = []
    if builds["success_rate_percent"] < 85:
        anomalies.append({
            "type": "build_instability",
            "severity": "High",
            "detail": f"Build success rate {builds['success_rate_percent']}% is below 85% threshold",
        })
    if deploys["rollback_rate_percent"] > 5:
        anomalies.append({
            "type": "high_rollback_rate",
            "severity": "Medium",
            "detail": f"Rollback rate {deploys['rollback_rate_percent']}% exceeds 5% threshold",
        })
    if collected_data["repo_metrics"]["avg_review_time_hours"] > 4:
        anomalies.append({
            "type": "slow_reviews",
            "severity": "Medium",
            "detail": f"PR review time {collected_data['repo_metrics']['avg_review_time_hours']}h exceeds 4h SLA",
        })

    latest_sprint = list(sprints.values())[0]
    if latest_sprint.get("blocked", 0) > 0:
        anomalies.append({
            "type": "blocked_items",
            "severity": "Medium",
            "detail": f"{latest_sprint['blocked']} blocked work items in current sprint",
        })

    if anomalies:
        print(f"\n⚠️  Anomalies Detected: {len(anomalies)}")
        for a in anomalies:
            print(f"   [{a['severity']}] {a['type']}: {a['detail']}")
    else:
        print("\n✅ No anomalies detected")

    # Forecast next sprint
    avg_growth_per_sprint = velocity_direction / 2  # over 2 sprint gaps
    forecast_velocity = sprint_velocities[0] + avg_growth_per_sprint
    print(f"\n🔮 Sprint 25 Forecast:")
    print(f"   Predicted velocity: {forecast_velocity:.0f} pts")
    print(f"   Confidence: {'High' if len(anomalies) < 2 else 'Medium'}")

    analysis = {
        "velocity_trend": {
            "direction": "accelerating" if velocity_direction > 0 else "decelerating",
            "change_points": velocity_direction,
            "change_percent": round(velocity_pct, 1),
            "sprint_velocities": sprint_velocities,
        },
        "build_health": {
            "status": build_health,
            "success_rate": builds["success_rate_percent"],
            "avg_duration_minutes": round(builds["avg_build_duration_seconds"] / 60, 1),
        },
        "deployment_cadence": {
            "production_per_day": round(deploy_freq, 1),
            "rollback_rate": deploys["rollback_rate_percent"],
            "mttr_hours": deploys["mean_time_to_recovery_hours"],
        },
        "twelve_week_trend": {
            "velocity_growth_percent": round(trend_growth, 1),
            "completion_rate_trend": f"{trends[0]['completion_rate']*100:.1f}% → {trends[-1]['completion_rate']*100:.1f}%",
            "bug_escape_trend": f"{trends[0]['bug_escape_rate']*100:.2f}% → {trends[-1]['bug_escape_rate']*100:.2f}%",
        },
        "anomalies": anomalies,
        "forecast": {
            "sprint_25_velocity": round(forecast_velocity),
            "confidence": "high" if len(anomalies) < 2 else "medium",
        },
        "collected_data": collected_data,
    }

    print("\n✅ Analysis complete — trends, anomalies, and forecast generated")
    print("➡️  Passing to AdvisorAgent\n")
    return analysis


def advisor_agent(analysis: dict[str, Any]) -> dict[str, Any]:
    """
    AdvisorAgent: generates executive summary, prioritized recommendations,
    and improvement roadmap. Queries Enterprise MCP for team leads.
    """
    print("=" * 70)
    print("💡 ADVISOR AGENT — Generating Recommendations")
    print("=" * 70)

    # Look up engineering leadership via Enterprise MCP
    print("\n👥 Querying Enterprise MCP → microsoft_graph_get (Engineering leadership)...")
    for member in MOCK_TEAM_MEMBERS:
        print(f"   ✓ {member['displayName']} — {member['jobTitle']}")

    # Generate recommendations based on analysis
    recommendations = []

    # Recommendation 1: Build stability
    build_status = analysis["build_health"]["status"]
    if "Needs Attention" in build_status or "Critical" in build_status:
        recommendations.append({
            "priority": 1,
            "area": "Build Stability",
            "issue": f"Build success rate at {analysis['build_health']['success_rate']}%",
            "action": "Quarantine flaky tests, add retry logic for transient failures, "
                      "set up build health alerts in Azure Monitor",
            "impact": "Reduce failed builds by 40%, save ~2h/day of developer wait time",
            "owner": "Marcus Chen (Staff Engineer)",
        })

    # Recommendation 2: Deployment reliability
    if analysis["deployment_cadence"]["rollback_rate"] > 5:
        recommendations.append({
            "priority": 2,
            "area": "Deployment Reliability",
            "issue": f"Rollback rate at {analysis['deployment_cadence']['rollback_rate']}%",
            "action": "Implement canary deployments, add automated smoke tests, "
                      "enforce staging validation gates before production",
            "impact": "Reduce rollbacks by 60%, improve deployment confidence",
            "owner": "Priya Sharma (Engineering Manager)",
        })

    # Recommendation 3: Code review efficiency
    review_time = analysis["collected_data"]["repo_metrics"]["avg_review_time_hours"]
    if review_time > 2.5:
        recommendations.append({
            "priority": 3,
            "area": "Code Review Efficiency",
            "issue": f"Average PR review time is {review_time}h",
            "action": "Set 4h SLA for PR reviews, use GitHub Copilot code review, "
                      "break large PRs into smaller increments (<200 lines)",
            "impact": "Reduce review cycle by 30%, increase merge throughput",
            "owner": "Elena Rodriguez (Senior Developer)",
        })

    # Recommendation 4: Sprint planning (if blocked items)
    blocked_anomaly = next((a for a in analysis["anomalies"] if a["type"] == "blocked_items"), None)
    if blocked_anomaly:
        recommendations.append({
            "priority": 4,
            "area": "Sprint Health",
            "issue": blocked_anomaly["detail"],
            "action": "Daily standup focus on blockers, escalation path within 24h, "
                      "pre-sprint dependency mapping",
            "impact": "Reduce blocked items to zero, improve sprint completion rate",
            "owner": "Priya Sharma (Engineering Manager)",
        })

    # Always add a velocity optimization recommendation
    forecast = analysis["forecast"]
    recommendations.append({
        "priority": len(recommendations) + 1,
        "area": "Velocity Optimization",
        "issue": f"Sprint 25 forecast: {forecast['sprint_25_velocity']} pts ({forecast['confidence']} confidence)",
        "action": "Increase planned capacity by 5%, allocate 10% of sprint to tech debt, "
                  "automate repetitive deployment tasks",
        "impact": "Target 170 pts/sprint within 3 sprints",
        "owner": "Priya Sharma (Engineering Manager)",
    })

    print(f"\n📋 Generated {len(recommendations)} Recommendations:")
    for rec in recommendations:
        print(f"\n   [{rec['priority']}] {rec['area']}")
        print(f"       Issue:  {rec['issue']}")
        print(f"       Action: {rec['action']}")
        print(f"       Impact: {rec['impact']}")
        print(f"       Owner:  {rec['owner']}")

    # Executive summary
    vel = analysis["velocity_trend"]
    summary = {
        "executive_summary": {
            "headline": (
                f"Team velocity is {vel['direction']} ({vel['change_percent']:+.1f}% over 3 sprints). "
                f"Build stability needs attention ({analysis['build_health']['success_rate']}%). "
                f"Sprint 25 forecast: {forecast['sprint_25_velocity']} pts."
            ),
            "velocity_status": vel["direction"],
            "build_health": analysis["build_health"]["status"],
            "deployment_cadence": f"{analysis['deployment_cadence']['production_per_day']} deploys/day",
            "mttr": f"{analysis['deployment_cadence']['mttr_hours']}h",
            "anomalies_count": len(analysis["anomalies"]),
            "forecast_sprint_25": f"{forecast['sprint_25_velocity']} pts",
        },
        "recommendations": recommendations,
        "team_leads": MOCK_TEAM_MEMBERS,
        "analysis": analysis,
    }

    print("\n" + "=" * 70)
    print("📊 EXECUTIVE VELOCITY REPORT")
    print("=" * 70)
    es = summary["executive_summary"]
    print(f"\n{es['headline']}")
    print(f"\n   Velocity:    {vel['direction'].title()} ({vel['change_percent']:+.1f}%)")
    print(f"   Build Health: {es['build_health']}")
    print(f"   Deploy Rate:  {es['deployment_cadence']}")
    print(f"   MTTR:         {es['mttr']}")
    print(f"   Anomalies:    {es['anomalies_count']}")
    print(f"   Forecast:     Sprint 25 → {es['forecast_sprint_25']}")
    print(f"   Actions:      {len(recommendations)} recommendations generated")

    return summary


# ============================================================================
# Sequential Orchestrator
# ============================================================================


def run_sequential_orchestration() -> dict[str, Any]:
    """
    Executes the Sequential Orchestration pattern:
      MetricsCollectorAgent → TrendAnalystAgent → AdvisorAgent

    Each agent processes its step and passes output to the next in a fixed pipeline.
    """
    print()
    print("╔" + "═" * 68 + "╗")
    print("║  SCENARIO 5: MULTI-AGENT DEVELOPMENT VELOCITY ANALYSIS           ║")
    print("║  Pattern: Semantic Kernel Sequential Orchestration                ║")
    print("╚" + "═" * 68 + "╝")
    print(f"\nMode: {'MOCK DATA' if USE_MOCK_DATA else 'LIVE — Azure MCP Server + Enterprise MCP'}")
    print()

    # Step 1 — Collect
    collected_data = metrics_collector_agent()

    # Step 2 — Analyze
    analysis = trend_analyst_agent(collected_data)

    # Step 3 — Advise
    final_report = advisor_agent(analysis)

    print("\n" + "=" * 70)
    print("✅ SCENARIO 5 — MULTI-AGENT VELOCITY ANALYSIS COMPLETE")
    print("=" * 70)
    print("Agents involved: MetricsCollectorAgent → TrendAnalystAgent → AdvisorAgent")
    print("Pattern:         Sequential Orchestration (Semantic Kernel)")
    print(f"Recommendations: {len(final_report['recommendations'])}")
    print(f"Forecast:        Sprint 25 → {final_report['executive_summary']['forecast_sprint_25']}")
    print("=" * 70)

    return final_report


# ============================================================================
# Semantic Kernel Sequential Orchestration (real mode)
# ============================================================================


async def run_sk_sequential_orchestration() -> dict[str, Any]:
    """
    Real-mode orchestration using Semantic Kernel Agent Framework.
    Uses SequentialOrchestration instead of HandoffOrchestration.
    Requires: pip install semantic-kernel[agents]
    """
    try:
        from semantic_kernel import Kernel
        from semantic_kernel.agents import ChatCompletionAgent
        from semantic_kernel.agents.orchestration.sequential import (
            SequentialOrchestration,
        )
        from semantic_kernel.agents.runtime import InProcessRuntime
        from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion
    except ImportError:
        print("⚠ semantic-kernel[agents] not installed. Run: pip install semantic-kernel[agents]")
        print("  Falling back to mock orchestration.\n")
        return run_sequential_orchestration()

    endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
    deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT")

    if not endpoint or not deployment:
        print("⚠ AZURE_OPENAI_ENDPOINT / AZURE_OPENAI_DEPLOYMENT not set.")
        print("  Falling back to mock orchestration.\n")
        return run_sequential_orchestration()

    # Build Semantic Kernel with Azure OpenAI
    kernel = Kernel()
    kernel.add_service(
        AzureChatCompletion(
            deployment_name=deployment,
            endpoint=endpoint,
        )
    )

    # Define agents with specialized system prompts
    collector = ChatCompletionAgent(
        kernel=kernel,
        name="MetricsCollectorAgent",
        instructions=(
            "You are a Metrics Collector Agent. Gather development velocity data from "
            "Azure DevOps (sprint metrics, repo stats), Azure Monitor (build and deployment "
            "logs via the Azure MCP Server), and Cosmos DB (historical trends via the Azure "
            "MCP Server). Present the raw data in a structured format for analysis."
        ),
    )

    analyst = ChatCompletionAgent(
        kernel=kernel,
        name="TrendAnalystAgent",
        instructions=(
            "You are a Trend Analyst Agent. Analyze the metrics from MetricsCollectorAgent: "
            "compute velocity trends, build stability scores, deployment cadence, and detect "
            "anomalies. Identify bottlenecks and forecast next sprint velocity. Present your "
            "analysis with statistical backing."
        ),
    )

    advisor = ChatCompletionAgent(
        kernel=kernel,
        name="AdvisorAgent",
        instructions=(
            "You are an Advisor Agent. Based on the analysis from TrendAnalystAgent, generate "
            "an executive summary and prioritized recommendations. Look up engineering leadership "
            "via the Enterprise MCP Server (Microsoft Graph) and assign owners to each recommendation. "
            "Provide a clear improvement roadmap."
        ),
    )

    # Create sequential orchestration (fixed pipeline order)
    orchestration = SequentialOrchestration(
        members=[collector, analyst, advisor],
    )

    # Run with in-process runtime
    runtime = InProcessRuntime()
    runtime.start()

    result = await orchestration.invoke(
        task=(
            "Analyze the development velocity for the ContosoApp project. "
            "Collect sprint metrics, build/deploy logs, and 12-week trends. "
            "Identify anomalies and bottlenecks. Generate an executive report "
            "with prioritized recommendations."
        ),
        runtime=runtime,
    )

    await runtime.stop_when_idle()

    value = await result.get()
    print("\n📊 Semantic Kernel Sequential Orchestration Result:")
    print(str(value))

    return {"sk_result": str(value)}


# ============================================================================
# Entry point
# ============================================================================


def main():
    parser = argparse.ArgumentParser(
        description="Scenario 5: Multi-Agent Development Velocity Analysis"
    )
    parser.add_argument(
        "--real",
        action="store_true",
        help="Use Semantic Kernel with real Azure OpenAI (requires SK + env vars)",
    )
    args = parser.parse_args()

    if args.real and not USE_MOCK_DATA:
        asyncio.run(run_sk_sequential_orchestration())
    else:
        run_sequential_orchestration()


if __name__ == "__main__":
    main()
