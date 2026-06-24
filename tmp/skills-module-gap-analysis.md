# Skills Module — Gap Analysis

> **Purpose:** Architecture review — comparing competency-updater vs ai-project-staffing-assistant  
> **Date:** 2026-05-19  
> **Context:** Informing what's missing for a unified Skills module within TalentIQ

---

## 1. Feature Comparison Table

| Capability | competency-updater (backend + UI + workflow) | ai-project-staffing-assistant | Gap / Missing |
|---|---|---|---|
| **Skill Inference (AI)** | ✅ LLM agent (Llama 4 Maverick) analyzes projects, learning, ADO data to recommend new skills | ❌ Not present | — |
| **Skill Matching** | ❌ Not present | ✅ AI-powered matching of consultant skills → projects with fit scores | Competency-updater has no matching capability |
| **Skill Write-Back (Workday)** | ✅ SOAP call to update Workday competencies | ❌ Not present | Staffing assistant reads skills but never writes back |
| **Employee Self-Service UI** | ✅ View recommendations, approve/reject, feedback | ❌ Chat-only interface, no skill management | — |
| **Chat Interface** | ❌ Not present | ✅ Conversational AI for project discovery | Competency-updater has no conversational UX |
| **Data Sources** | UDP (Databricks), Workday, ADO, DXC Learning, GitHub Enterprise | UDP, SQLite (local project/consultant data) | Neither pulls from Luxoft, FDS, or Resumes |
| **Vector Search / Embeddings** | ✅ Databricks Vector Search for skill similarity | ❌ Not present (uses text matching) | Staffing assistant lacks semantic search |
| **Notification System** | ✅ Email notifications via Azure Communication Services | ❌ Not present | — |
| **Scheduling / Orchestration** | ✅ Databricks Asset Bundles, scheduled workflows | ❌ Not present (on-demand only) | — |
| **Proficiency Levels** | ✅ beginner/intermediate/advanced/expert + confidence % | ❌ Not modeled explicitly | Staffing assistant uses fit % but not per-skill proficiency |
| **Skill Taxonomy** | ⚠️ Uses `dxc_approved_competency` table (flat list) | ❌ No taxonomy | Neither has hierarchy, synonyms, or ontology |
| **Conflict Resolution** | ❌ Not present | ❌ Not present | **Critical gap** — no merge logic for multi-source |
| **Skill Decay / Staleness** | ❌ Not present | ❌ Not present | **Gap** — no temporal degradation model |
| **Audit / Lineage** | ⚠️ Cosmos DB stores analysis results with timestamps | ❌ Not present | No formal provenance tracking in either |
| **Multi-tenant / RBAC** | ⚠️ Basic (employee sees own data) | ❌ No auth beyond demo | Neither has proper role-based access |
| **API Surface** | FastAPI — recommendations CRUD, Workday update | FastAPI v2 — projects, consultants, AI chat, resource requests | No unified Skills API exists |
| **Database** | Databricks Lakebase (PostgreSQL) + Cosmos DB | SQLite (local) | Architecturally different — need unified data layer |
| **Deployment** | Azure Container Apps + Databricks | Docker + Codespace (dev only) | Staffing assistant not production-deployed |

---

## 2. Architecture Layer Mapping

| TalentIQ Layer | competency-updater | ai-project-staffing-assistant | Gaps for Unified Skills Module |
|---|---|---|---|
| **APPLICATION LAYER** | | | |
| → Web UI | ✅ React app (recommendations view, approve/reject) | ✅ React app (chat, project cards) | No unified Skills management UI; no taxonomy admin UI |
| → API Gateway | ❌ Direct FastAPI access | ❌ Direct FastAPI access | No gateway, no rate limiting, no aggregation |
| → Auth / Identity | ⚠️ Basic (implied employee context) | ❌ None | No SSO/OIDC integration in either |
| → Backend APIs | ✅ Recommendations CRUD, Workday update | ✅ Projects, consultants, AI chat | No unified Skills API (CRUD, search, bulk update, validation) |
| → AI Orchestration | ✅ LLM agent for skill inference | ✅ OpenAI for matching/chat | No shared AI orchestration layer; each is siloed |
| → Domain Services | ⚠️ Competency recommendation only | ⚠️ Project matching only | No: Taxonomy Mgmt, Skill Reconciliation, Decay Engine, Verification |
| **UNIFIED DATA LAYER** | | | |
| → Canonical Model | ⚠️ CompetencyRecommendation model (partial) | ⚠️ Consultant/Project models (partial) | No unified Worker/Skill schema spanning both systems |
| → Relational Store | ✅ Databricks Lakebase (PostgreSQL) | ❌ SQLite (dev only) | Need single relational store for golden skill records |
| → Vector Store | ✅ Databricks Vector Search | ❌ Not present | Need vector embeddings for skill semantic matching |
| → Search / Analytics | ❌ Not present | ❌ Not present | No operational telemetry, KPIs, or skill analytics |
| **INGESTION LAYER** | | | |
| → Source Connectors | ✅ Databricks (reads UDP tables) | ❌ Static/local data | Need connectors to Workday, Luxoft, FDS, Resumes |
| → Filters & Cleansing | ⚠️ Basic preprocessing in pipeline | ❌ Not present | No per-source cleansing rules |
| → Mappers (Canonical) | ⚠️ Maps to approved competency list | ❌ Not present | No schema unification or deduplication across sources |
| → Embedding Generation | ✅ Vectorization in data pipeline | ❌ Not present | Need unified embedding pipeline |
| → Orchestration | ✅ Databricks workflows + schedules | ❌ Not present | Need job orchestration with state, checkpoints, retries |
| **DATA SOURCES** | | | |
| → DXC HR / Workday | ✅ Read (via UDP) + Write (SOAP) | ❌ Not connected | — |
| → Luxoft / SL2 | ❌ Not connected | ❌ Not connected | **Gap** — skill profiles, domains, languages |
| → FDS | ❌ Not connected | ❌ Not connected | **Gap** — skills, proficiency, certifications |
| → UDP (Databricks) | ✅ Primary data source | ⚠️ Not directly (uses local copy) | — |
| → Resumes | ❌ Not connected | ❌ Not connected | **Gap** — unstructured skill extraction |
| → Project/ADO | ✅ ADO + GitHub Enterprise | ❌ Not connected | Staffing assistant has project data but not linked to skills |
| → DXC Learning | ✅ Connected | ❌ Not connected | — |

---

## 3. Critical Gaps for Unified Skills Module

| # | Gap | Severity | Exists In Neither Project | Required For |
|---|---|---|---|---|
| 1 | **Skill Taxonomy Service** | 🔴 Critical | ✓ | All skill operations — mapping, search, matching |
| 2 | **Multi-Source Conflict Resolution** | 🔴 Critical | ✓ | Golden record creation when sources disagree |
| 3 | **Unified Skills API** | 🔴 Critical | ✓ | Single entry point for all skill reads/writes |
| 4 | **Skill Provenance / Lineage** | 🟠 High | ✓ | Audit, compliance, confidence scoring |
| 5 | **Skill Decay Model** | 🟠 High | ✓ | Accurate matching over time |
| 6 | **Luxoft + FDS Connectors** | 🟠 High | ✓ | Complete skill coverage across DXC entities |
| 7 | **Resume NLP Pipeline** | 🟡 Medium | ✓ | Unstructured → structured skill extraction |
| 8 | **Event Bus / Pub-Sub** | 🟠 High | ✓ | Notify downstream when skills change |
| 9 | **SSO / OIDC Auth** | 🟠 High | ✓ | Production security |
| 10 | **Skill Analytics / KPIs** | 🟡 Medium | ✓ | Operational visibility, supply/demand |

---

## 4. What Each Project Contributes to the Unified Module

| From competency-updater | From ai-project-staffing-assistant |
|---|---|
| LLM-based skill inference engine | AI-powered skill-to-project matching |
| Workday write-back mechanism | Chat-based conversational UX |
| Employee approval workflow | Project/consultant data models |
| Databricks pipeline orchestration | Resource request handling |
| Vector search for skill similarity | Fit scoring algorithm |
| Notification system | — |
| Scheduled batch processing | — |

---

## 5. Recommended Priority Order

1. **Taxonomy Service** — foundation for everything else
2. **Unified Skills API** — single contract for all consumers
3. **Multi-source ingestion** (add Luxoft, FDS) — complete data coverage
4. **Conflict resolution engine** — produce golden records
5. **Merge inference + matching** — combine both projects' AI capabilities
6. **Auth + event bus** — production readiness
7. **Analytics + decay** — operational maturity
