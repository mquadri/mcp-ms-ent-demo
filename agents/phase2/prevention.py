"""Recurring prevention analysis over persisted investigations."""

from __future__ import annotations

from collections import Counter
import hashlib

from .models import Recommendation


def generate_prevention_recommendations(investigations: list[dict]) -> list[Recommendation]:
    service_counts: Counter[str] = Counter()
    cause_counts: Counter[str] = Counter()
    source_ids: list[str] = []

    for item in investigations:
        source_ids.append(item.get("investigation_id", "unknown"))
        for service in item.get("services", []):
            service_counts[service] += 1
        root_cause = item.get("root_cause")
        if root_cause:
            cause_counts[root_cause] += 1

    recommendations: list[Recommendation] = []

    for service, count in service_counts.most_common(3):
        if count >= 1:
            recommendations.append(
                Recommendation(
                    recommendation_id=f"prevent-{service.lower()}-observability",
                    title=f"Strengthen observability for {service}",
                    area="observability",
                    priority=1 if count > 1 else 2,
                    rationale=f"{service} appeared in {count} recent investigation(s).",
                    action="Add service-level alerts for dependency saturation, error budget burn, and rollback rate.",
                    owner="Platform Engineering",
                    source_investigations=source_ids,
                )
            )

    for cause, count in cause_counts.most_common(2):
        recommendations.append(
            Recommendation(
                recommendation_id=f"prevent-cause-{_stable_suffix(cause)}",
                title="Prevent recurring root cause",
                area="reliability",
                priority=1,
                rationale=f"Root cause observed {count} time(s): {cause}",
                action="Create a reliability work item with automated validation and a rollback test.",
                owner="Service Owner",
                source_investigations=source_ids,
            )
        )

    return recommendations


def _stable_suffix(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()[:10]
