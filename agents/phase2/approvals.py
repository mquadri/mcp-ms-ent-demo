"""Human approval policy for remediation actions."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class ApprovalDecision:
    status: str
    reason: str
    required_for: list[str]


def evaluate_remediation_approval(
    severity: str,
    mitigation_plan: list[str],
    auto_approve: bool = False,
) -> ApprovalDecision:
    risky_terms = ("deploy", "scale", "restart", "failover", "delete", "rotate")
    risky_steps = [
        step for step in mitigation_plan
        if any(term in step.lower() for term in risky_terms)
    ]

    if auto_approve:
        return ApprovalDecision(
            status="approved",
            reason="Auto-approval enabled for this run.",
            required_for=risky_steps,
        )

    if severity.lower() in {"sev1", "critical", "1 - critical"} or risky_steps:
        return ApprovalDecision(
            status="pending",
            reason="Human approval required before executing production-impacting remediation.",
            required_for=risky_steps or mitigation_plan,
        )

    return ApprovalDecision(
        status="not_required",
        reason="No production-impacting remediation detected.",
        required_for=[],
    )
