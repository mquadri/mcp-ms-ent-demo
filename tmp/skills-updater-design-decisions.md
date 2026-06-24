# Skills Updater — Design Decisions

> **Module:** Skills Updater (Training Pathway)  
> **Owner:** TBD  
> **Last Updated:** 2026-05-18  
> **Status:** Draft — In Review

---

## Context

The Skills Updater is responsible for maintaining the "golden record" of worker skills across DXC by reconciling data from multiple authoritative sources (Workday, Luxoft/SL2, FDS, Databricks/UDP, Resumes) and writing to the People Graph. It must support both the TalentIQ platform and downstream consumers (AI Interviewer, Training Pathway, Talent Matching).

---

## Decision Log

### ADR-001: Skill Taxonomy Authority

| Field | Value |
|-------|-------|
| **Status** | 🟡 Proposed |
| **Date** | 2026-05-18 |
| **Context** | Multiple sources use different skill vocabularies (Workday skill dictionary, Luxoft taxonomy, FDS categories). Need a single canonical taxonomy for matching and search. |
| **Decision** | TBD — Options: (A) Adopt Luxoft taxonomy as base and map others, (B) Build DXC-owned canonical taxonomy, (C) Use industry standard (ESCO/O*NET) and map all sources |
| **Consequences** | Impacts ingestion mappers, search/matching accuracy, and ongoing maintenance cost |
| **Open Questions** | Who owns taxonomy governance? How frequently do new skills get added? |

---

### ADR-002: Proficiency Scale Normalization

| Field | Value |
|-------|-------|
| **Status** | 🟡 Proposed |
| **Date** | 2026-05-18 |
| **Context** | Workday uses 1-5, Luxoft may use descriptive levels, FDS uses certifications as proxy. Need unified proficiency representation. |
| **Decision** | TBD — Options: (A) Normalize all to 1-5 numeric, (B) Use descriptive levels (Beginner/Intermediate/Advanced/Expert), (C) Hybrid with confidence score |
| **Consequences** | Affects matching precision, UI display, and AI model training |
| **Open Questions** | Is self-assessed proficiency reliable? Should AI Interviewer override self-assessment? |

---

### ADR-003: Conflict Resolution Strategy

| Field | Value |
|-------|-------|
| **Status** | 🟡 Proposed |
| **Date** | 2026-05-18 |
| **Context** | When multiple sources assert different skill levels for the same worker+skill, need deterministic merge logic. |
| **Decision** | TBD — Options: (A) Source priority ranking (e.g., AI Interviewer > Certification > Self-declared), (B) Most recent wins, (C) Highest confidence wins, (D) Weighted average |
| **Consequences** | Directly impacts data quality and worker trust in the system |
| **Open Questions** | Should workers be able to dispute/override? What's the escalation path? |

---

### ADR-004: Skill Provenance & Lineage

| Field | Value |
|-------|-------|
| **Status** | 🟡 Proposed |
| **Date** | 2026-05-18 |
| **Context** | Need to track where each skill assertion originated for audit, compliance, and confidence scoring. |
| **Decision** | TBD — Options: (A) Store source + timestamp per skill-worker pair, (B) Full event sourcing of all skill changes, (C) Simple last-source-wins with audit log |
| **Consequences** | Event sourcing gives full history but higher storage/complexity cost |
| **Open Questions** | What retention period? Is GDPR/data residency a concern for skill data? |

---

### ADR-005: Ingestion Mode (Batch vs Real-Time)

| Field | Value |
|-------|-------|
| **Status** | 🟡 Proposed |
| **Date** | 2026-05-18 |
| **Context** | Skills data changes infrequently per worker but there are ~130K+ workers. Need to balance freshness vs. cost. |
| **Decision** | TBD — Options: (A) Nightly batch via Databricks only, (B) Event-driven (CDC from sources), (C) Hybrid — batch for bulk + real-time for self-service updates |
| **Consequences** | Real-time adds infrastructure complexity; batch-only means up to 24h staleness |
| **Open Questions** | Do sources support CDC/webhooks? What's acceptable latency for skill updates? |

---

### ADR-006: Resume Skill Extraction Pipeline

| Field | Value |
|-------|-------|
| **Status** | 🟡 Proposed |
| **Date** | 2026-05-18 |
| **Context** | Resumes are an unstructured source of skills data. Need NLP/AI pipeline to extract skills, certifications, and experience. |
| **Decision** | TBD — Options: (A) Azure OpenAI for extraction, (B) Custom NER model, (C) Third-party resume parser + AI enrichment |
| **Consequences** | AI extraction has confidence variance; need human-in-the-loop for low-confidence results |
| **Open Questions** | Resume format/storage location? Consent for AI processing? |

---

### ADR-007: Skill Decay / Staleness Model

| Field | Value |
|-------|-------|
| **Status** | 🟡 Proposed |
| **Date** | 2026-05-18 |
| **Context** | Skills degrade if not practiced. A "Java" skill from 5 years ago with no recent project usage should be down-weighted. |
| **Decision** | TBD — Options: (A) Time-based decay function, (B) Activity-based (linked to project assignments), (C) No decay — rely on reassessment gates |
| **Consequences** | Affects matching accuracy and requires project history as input |
| **Open Questions** | What's the half-life for a skill? Should workers be notified of decaying skills? |

---

### ADR-008: Feedback Loop — AI Interviewer → Skills Updater

| Field | Value |
|-------|-------|
| **Status** | 🟡 Proposed |
| **Date** | 2026-05-18 |
| **Context** | The AI Interviewer validates skills via conversational assessment. Results should feed back to update/verify skill proficiency. |
| **Decision** | TBD — Options: (A) Direct write-back on interview completion, (B) Queue for human review before update, (C) Update confidence score only (don't change proficiency) |
| **Consequences** | Direct write-back is fast but risky if interview had errors; review adds latency |
| **Open Questions** | What's the interview → skill mapping? Can one interview validate multiple skills? |

---

### ADR-009: People Graph Integration

| Field | Value |
|-------|-------|
| **Status** | 🟡 Proposed |
| **Date** | 2026-05-18 |
| **Context** | The People Graph is the central entity for worker data. Skills Updater needs to write merged/validated skills back. |
| **Decision** | TBD — Options: (A) Direct DB write to People Graph store, (B) API-mediated updates via Unified Data Layer, (C) Event-driven (publish skill events, People Graph subscribes) |
| **Consequences** | Direct writes risk data corruption; event-driven adds eventual consistency |
| **Open Questions** | Does People Graph exist today or is it aspirational? What's the write contract? |

---

### ADR-010: Missing Data Sources

| Field | Value |
|-------|-------|
| **Status** | 🟡 Proposed |
| **Date** | 2026-05-18 |
| **Context** | Current sources (Workday, Luxoft, FDS, DBX, Resumes) may not be sufficient for a complete skill profile. |
| **Decision** | Evaluate adding: (A) Project/assignment history from Compass/GSAP, (B) Training completions from DXC Learning, (C) External certifications (Credly, cloud providers), (D) Peer/manager endorsements |
| **Consequences** | Each new source adds ingestion complexity but improves accuracy |
| **Open Questions** | Data access agreements? API availability? Priority order for new sources? |

---

## Architectural Gaps Summary

| # | Gap | Layer | Severity | Notes |
|---|-----|-------|----------|-------|
| G1 | No dedicated Skills API surface | Application | High | Need REST/GraphQL endpoints for CRUD, bulk update, validation |
| G2 | No Skills self-service UI | Application | Medium | Workers should view/dispute their skills |
| G3 | No event bus for skill changes | Application | High | Downstream consumers need notifications |
| G4 | No taxonomy/ontology service | Unified Data | Critical | Foundation for all skill operations |
| G5 | No proficiency normalization | Unified Data | High | Can't compare across sources without it |
| G6 | No temporal versioning | Unified Data | Medium | Need skill history for decay & audit |
| G7 | No conflict resolution logic | Ingestion | Critical | Multiple sources = conflicting data |
| G8 | No resume NLP pipeline | Ingestion | Medium | Unstructured → structured extraction |
| G9 | No project history as source | Data Sources | Medium | Actual work validates claimed skills |
| G10 | No training completions feed | Data Sources | Medium | Certifications = verified skills |

---

## Next Steps

- [ ] Decide on taxonomy authority (ADR-001) — blocks all mapping work
- [ ] Define proficiency normalization (ADR-002) — blocks unified data model
- [ ] Confirm People Graph contract (ADR-009) — blocks write-back design
- [ ] Identify available APIs/CDC from sources (ADR-005) — blocks ingestion design
- [ ] Stakeholder review of this document

---

## References

- TalentIQ Layered Architecture diagram
- TalentIQ Platform (Initial) module map
- Skills Module data flow diagram (slide 10)
