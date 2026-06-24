# Skills & Experience Architecture - Clean Review Version

Date: 2026-05-18  
Scope: TalentIQ Skills & Experience module (DXC)

## 1. Purpose

This document consolidates architecture decisions and implementation guidance for the Skills & Experience module into one clean, execution-ready version.

Core principle:
- Workday is the authoritative HR source of record.
- TalentIQ is the intelligence and enrichment layer for matching, validation, skill gaps, and recommendations.

## 2. Architecture Goals

- Build a trusted skills data foundation for matching and workforce planning.
- Keep skill data current through multi-source ingestion and validation.
- Ensure explainability, governance, and compliance for every skill update.
- Deliver an MVP that can scale into full graph and semantic capabilities.

## 3. Decision Register (must be closed before build)

| ID | Decision | Recommended Position | Owner | Due | Status |
|---|---|---|---|---|---|
| D1 | Canonical person entity | Use `Resource` as canonical in Skills domain; map candidate/employee variants through source adapters | Product + Architecture | TBD | Open |
| D2 | Source of record policy | Workday authoritative for official profile/certs; TalentIQ stores enrichment and proposals | Product + DXC HR IT | TBD | Open |
| D3 | Graph strategy | Relational PostgreSQL is durable source; graph is projection/query layer | Architecture | TBD | Open |
| D4 | Apache AGE feasibility | Validate Azure PostgreSQL support in target env; define fallback if unsupported | Platform | TBD | Open |
| D5 | Skill taxonomy ownership | Central stewardship model (create/merge/deprecate skills and aliases) | Product + Business Owners | TBD | Open |
| D6 | Updater governance | Proposal + approval workflow; controlled auto-apply policy only for low-risk updates | Product + Security | TBD | Open |
| D7 | Compliance controls | RBAC, encryption, audit, retention, and residency requirements signed off | Security + Compliance | TBD | Open |
| D8 | MVP scope | Workday-first ingestion, catalog/profile/matching baseline, governance and audit | Product + Engineering | TBD | Open |

## 4. Target Data Model

Canonical entities:
- Resource
- Skill
- SkillAlias
- SkillCategory
- SkillRelationship
- ResourceSkillAssertion
- ValidationEvent
- SkillEvidence
- Certification
- TrainingPathway
- SkillRefreshTask

Minimum attributes for matching-ready skills:
- skill_id
- canonical_name
- aliases
- category
- proficiency_level (1-5 normalized)
- years_experience
- last_used_date
- source_system
- confidence_score
- validation_status
- stale_flag
- evidence_summary

## 5. Source, Enrichment, and Conflict Rules

Source policy:
- Workday: official profile and certification baseline.
- TalentIQ: enrichment, inferred updates, confidence, explainability, and matching features.
- LuxSkills and other learning systems: training progress and completion signals.

Conflict-resolution policy (required):
1. Apply source precedence (authoritative sources first).
2. Apply recency rule.
3. Apply confidence threshold.
4. Route unresolved conflicts to approval queue.
5. Persist decision and rationale in immutable audit log.

## 6. Storage and Query Architecture

Recommended architecture:
- PostgreSQL relational tables as durable system of record.
- pgvector for semantic similarity and related-skill retrieval.
- Optional Apache AGE graph projection for relationship traversal and adjacency scoring.

Important constraint:
- Graph must not be the only source of truth.
- Graph projection must be rebuildable idempotently from relational data.

## 7. Ingestion and Validation Flow

1. Ingest data from Workday, resumes, PSA/FDS, and validation systems.
2. Normalize identities, skill aliases, and proficiency scales.
3. Upsert canonical records and assertions with provenance metadata.
4. Generate inference proposals in Skills Updater.
5. Score each proposal with confidence and evidence quality.
6. Apply approval policy (manual or rule-based auto-apply).
7. Write changes, update projections, and emit downstream events.
8. Record complete audit trail and freshness timestamps.

## 8. Skills Updater Governance

Proposal lifecycle:
- Drafted -> Scored -> PendingApproval -> Approved/Rejected -> Synced -> Audited

Required metadata per proposal:
- proposal_id
- resource_id
- skill_id
- old_value
- proposed_value
- confidence_score
- evidence_refs
- approval_status
- approver
- synced_to_workday
- timestamps

## 9. Matching Integration Contract (Module 05)

Skills service must publish normalized matching features:
- direct_skill_match_score
- semantic_skill_match_score
- proficiency_score
- recency_score
- certification_score
- validation_score
- adjacency_score
- stale_penalty

Explainability payload must include:
- direct vs related matches
- proficiency fit
- recency impact
- missing skills
- training-needed skills
- confidence indicators

## 10. Skill Gap and Training Contract (Module 14)

Gap object:
- required_skill
- current_skill_level
- required_level
- gap_severity
- evidence
- recommended_training
- estimated_time_to_ready
- reassessment_required

Gap lifecycle:
- Identified -> Assessed -> GapAnalyzed -> InTraining -> Reassessing -> Ready -> Assigned

## 11. API Surface (MVP baseline)

- GET /api/skills
- GET /api/skills/categories
- GET /api/resources/{id}/skills
- PUT /api/resources/{id}/skills/{skillId}
- POST /api/skills/match
- GET /api/resources/{id}/skill-gaps
- POST /api/skills/updater/proposals
- PUT /api/skills/updater/proposals/{id}/approve
- PUT /api/skills/updater/proposals/{id}/revert
- POST /api/skills/validations

API design requirements:
- Versioned routes or headers from day one.
- Clear auth scopes per endpoint.
- Idempotency for write operations.
- Standardized error contract.
- Async event contract for ingestion and validation updates.

## 12. Security and Compliance Baseline

Mandatory controls:
- RBAC roles: SkillsViewer, SkillsEditor, SkillsApprover, SkillsAdmin, ResourceManager, ChapterGuildLead.
- Encryption at rest and in transit.
- Data minimization for sensitive HR attributes.
- Field-level access controls where needed.
- Immutable audit logging for all manual and automated changes.
- Retention and residency aligned to DXC policy.

## 13. Observability and SLOs

Minimum metrics:
- ingestion_success_rate
- ingestion_lag_minutes
- normalization_conflict_rate
- proposal_auto_apply_rate
- approval_cycle_time
- match_api_p95_ms
- skill_profile_freshness_days
- audit_write_failures

Initial SLO targets (to confirm):
- Match API p95 < 400 ms for MVP workloads.
- Daily ingestion freshness < 24h.
- Proposal processing success > 99%.

## 14. Implementation Plan (step by step)

Phase 0 - Architecture Validation
1. Confirm AGE support in target Azure PostgreSQL.
2. Lock canonical domain names and boundaries.
3. Approve source precedence and conflict policy.
4. Approve taxonomy governance model.
5. Approve security/compliance baseline.

Exit criteria:
- Signed decision register (D1-D8).
- Fallback architecture approved if AGE is not feasible.

Phase 1 - Data Foundation
1. Create relational schema + Alembic migrations.
2. Implement normalization and provenance tracking.
3. Deliver Workday-first ingestion pipeline.
4. Add audit trails and freshness tracking.

Phase 2 - Intelligence Layer
1. Add Skills Updater proposals and approval workflow.
2. Add matching features and explainability payload.
3. Add gap analysis and training pathway outputs.
4. Add graph projection and semantic retrieval.

Phase 3 - Productization
1. API hardening, auth scopes, and gateway routes.
2. UI surfaces: Skills library, profile, updater queue, gap dashboard.
3. Monitoring dashboards and operational playbooks.
4. End-to-end UAT and production readiness checks.

## 15. RACI (starter)

| Deliverable | Product | Architect | Backend | Data Eng | Security | DXC Stakeholder |
|---|---|---|---|---|---|---|
| Canonical model | A | R | C | C | C | C |
| Source precedence policy | A | R | C | R | C | C |
| Workday integration contract | C | R | C | R | C | A |
| Skills updater workflow | A | R | R | C | C | C |
| RBAC and audit matrix | C | R | C | C | A | C |
| MVP scope and timeline | A | R | C | C | C | A |

Legend: R = Responsible, A = Accountable, C = Consulted

## 16. Meeting Agenda (60 minutes)

1. Confirm scope and module boundaries (10 min)
2. Close D1-D4 architecture decisions (15 min)
3. Close D5-D7 governance/security decisions (15 min)
4. Confirm MVP features and timeline (10 min)
5. Assign owners and due dates for open actions (10 min)

## 17. Open Questions (carry into meeting)

- Is the module employee-only, candidate-only, or both?
- Is AGE approved in the exact target SKU/region/version?
- Who owns taxonomy stewardship and SLA for changes?
- Which Workday fields are approved for ingestion in MVP?
- What visibility constraints apply for manager/admin skill views?
- Should resume parsing be included in MVP or phase 2?
- Which performance target has priority: search, profile load, or match query?

## 18. Final Architect Recommendation

Approve the module direction, but require a short Phase 0 architecture gate before implementation starts. This avoids rework by forcing early closure on graph feasibility, domain model, source-of-truth policy, compliance controls, and MVP scope.
