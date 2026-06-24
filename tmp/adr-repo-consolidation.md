# ADR: Competency Repos — Consolidate or Keep Separate?

> **Date:** 2026-05-19  
> **Status:** Under Discussion  
> **Context:** Three repos exist today: `competency-updater-backend`, `competency-updater-ui`, `competency-updater-workflow`

---

## Current State

| Repo | Tech Stack | Deployment Target | Team Concern |
|------|-----------|-------------------|--------------|
| `competency-updater-backend` | Python/FastAPI | Azure Container Apps | API serving |
| `competency-updater-ui` | React/TypeScript + Express | Azure Container Apps | Frontend + BFF |
| `competency-updater-workflow` | PySpark/Databricks notebooks | Databricks Jobs (via Asset Bundles) | Data pipeline + AI agent |

---

## Option A: Keep Separate (Current State) ✅ RECOMMENDED

| Aspect | Assessment |
|--------|-----------|
| **Deployment independence** | ✅ Each deploys independently — UI can ship without touching pipeline |
| **Release cadence** | ✅ Workflow runs on schedule (batch), backend/UI are on-demand — different rhythms |
| **Runtime mismatch** | ✅ Workflow runs on Databricks Spark clusters; backend/UI run on Container Apps — fundamentally different runtimes |
| **Team ownership** | ✅ Data engineers own workflow; app devs own backend+UI — clear boundaries |
| **CI/CD simplicity** | ✅ Each repo has its own pipeline (Azure Pipelines for backend, Databricks Asset Bundles for workflow) |
| **Blast radius** | ✅ A broken workflow deploy doesn't block UI fixes |
| **Scaling** | ✅ Backend/UI scale horizontally on containers; workflow scales via Spark cluster sizing |

### But fix these issues:

| Issue | Fix |
|-------|-----|
| No shared contract/schema | Create a shared `competency-models` package or schema registry |
| Duplicated Databricks SDK versions | Pin versions in a shared config |
| No API versioning | Backend should version its API (`/v1/`, `/v2/`) |
| Workflow writes directly to Lakebase | Should go through backend API or publish events |

---

## Option B: Monorepo (All Three Together)

| Aspect | Assessment |
|--------|-----------|
| **Atomic changes** | ✅ Schema changes across all 3 in one PR |
| **Discoverability** | ✅ New devs see the full system in one clone |
| **Shared code** | ✅ Common models, utils, types in one place |
| **CI complexity** | ⚠️ Need path-based triggers (only build what changed) |
| **Databricks deployment** | ❌ Asset Bundles expect a specific repo structure with `.databricks/` at root — awkward in monorepo |
| **Container image builds** | ⚠️ Need separate Dockerfiles and build contexts per service |
| **Runtime mismatch** | ❌ PySpark notebooks ≠ FastAPI ≠ React — no shared toolchain benefit |
| **Permission model** | ⚠️ Different team members may need different repo-level access |

---

## Option C: Merge Backend + UI Only (Keep Workflow Separate)

| Aspect | Assessment |
|--------|-----------|
| **Rationale** | Backend and UI are tightly coupled (UI calls backend directly), same runtime (Container Apps), same team |
| **Deployment** | Single container or two containers from one repo (common pattern) |
| **Workflow stays separate** | Databricks notebooks have unique deployment model — natural boundary |
| **Shared types** | TypeScript types (UI) ↔ Pydantic models (backend) still different languages |

---

## Recommendation Matrix

| Criteria | Keep Separate | Monorepo | Merge Backend+UI |
|----------|:---:|:---:|:---:|
| Deployment independence | ✅ | ⚠️ | ✅ |
| Runtime compatibility | ✅ | ❌ | ✅ |
| Databricks Asset Bundles fit | ✅ | ❌ | ✅ |
| Atomic cross-service changes | ❌ | ✅ | ⚠️ |
| CI/CD simplicity | ✅ | ❌ | ✅ |
| Team boundary clarity | ✅ | ⚠️ | ✅ |
| Shared schema enforcement | ❌ | ✅ | ⚠️ |
| New developer onboarding | ⚠️ | ✅ | ⚠️ |

---

## Verdict

### 🏆 Keep Separate — with a shared contract layer

**Why:**
1. **Databricks workflow is a fundamentally different deployment model** — PySpark notebooks deployed via Asset Bundles don't benefit from being in the same repo as a Container App
2. **Different release cadences** — workflow runs nightly batch; UI/backend iterate on user feedback weekly
3. **No shared language** — Python (backend) + TypeScript (UI) + PySpark (workflow) — monorepo tooling adds cost with no benefit
4. **Industry pattern** — microservices with separate repos is the norm for different runtime targets

### What to add to make separation work well:

| Need | Solution |
|------|----------|
| Shared data contract | Create `competency-updater-contracts` repo with Pydantic models + JSON Schema → generate TypeScript types |
| API versioning | Backend exposes versioned endpoints; workflow writes via API not direct DB |
| Event-driven communication | Workflow publishes `skill.recommended` events → backend subscribes (decouple the direct Lakebase coupling) |
| Integration tests | Separate repo with contract tests that validate all 3 work together |
| Shared config | Environment variables, Databricks secrets, and connection strings managed centrally (Azure Key Vault) |

---

## If Scaling to Full TalentIQ Skills Module

When the Skills module grows to include taxonomy service, conflict resolution, additional connectors, the repo structure should be:

```
competency-updater-backend     → Skills API (FastAPI, Container Apps)
competency-updater-ui          → Skills UI (React, Container Apps)  
competency-updater-workflow    → Data pipelines (PySpark, Databricks)
competency-updater-contracts   → Shared schemas, models, events (NEW)
skills-taxonomy-service        → Taxonomy CRUD + governance (NEW, if scope grows)
```

This maintains separation of concerns while the contracts repo enforces consistency.
