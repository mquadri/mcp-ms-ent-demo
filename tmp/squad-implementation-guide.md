# Implementing Squad for the Competency Updater Project

> **Date:** 2026-05-19  
> **Purpose:** Structure guide for using [bradygaster/squad](https://github.com/bradygaster/squad) to develop the competency-updater project with AI agent teams via GitHub Copilot

---

## What is Squad?

Squad gives you a **human-directed AI development team** through GitHub Copilot. Each agent has a charter (identity, expertise), persists across sessions, learns your codebase, and writes decisions back so work is inspectable. You stay in control — agents help with coordination, repetition, and parallel execution.

---

## Recommended Squad Structure for Competency Project

### Team Composition

Given the competency-updater spans **3 repos** with **3 tech stacks**, here's the recommended squad:

| Agent Role | Responsibility | Primary Repo(s) |
|---|---|---|
| **Lead / Architect** | Architecture decisions, cross-repo coordination, API design, ADR creation | All 3 |
| **Backend Engineer** | FastAPI endpoints, Pydantic models, Databricks SDK integration, Workday SOAP | `competency-updater-backend` |
| **Frontend Engineer** | React components, MUI, state management, UX flows | `competency-updater-ui` |
| **Data Engineer** | PySpark notebooks, Databricks pipelines, vector search, LLM agent logic | `competency-updater-workflow` |
| **Tester** | Integration tests, contract tests, unit tests across all repos | All 3 |
| **Scribe** | Decision logging, documentation, knowledge persistence | Automatic (silent) |

---

## Setup Steps

### 1. Install Squad CLI

```bash
npm install -g @bradygaster/squad-cli
```

### 2. Initialize in Each Repo (or pick one primary)

**Option A — Per-repo squads (Recommended for your separate-repo architecture):**

```bash
# In each repo
cd competency-updater-backend
squad init

cd ../competency-updater-ui
squad init

cd ../competency-updater-workflow
squad init
```

**Option B — Single squad with remote links (if you want one coordinating team):**

```bash
cd competency-updater-backend
squad init
squad link ../competency-updater-ui
squad link ../competency-updater-workflow
```

### 3. Authenticate

```bash
gh auth login
```

### 4. Launch with Copilot

```bash
copilot --agent squad --yolo
```

Or in VS Code: Open Copilot Chat → select **Squad** agent.

---

## Recommended `.squad/` Structure for Competency Project

```
competency-updater-backend/.squad/
├── team.md                          # Roster
├── routing.md                       # Who handles what
├── decisions.md                     # Architecture decisions (linked to ADRs)
├── ceremonies.md                    # Sprint config
├── agents/
│   ├── lead/
│   │   ├── charter.md              # Architect — owns API design, cross-repo contracts
│   │   └── history.md              # Learned: Databricks Lakebase patterns, Workday SOAP quirks
│   ├── backend/
│   │   ├── charter.md              # FastAPI expert — Pydantic, psycopg2, Databricks SDK
│   │   └── history.md              # Learned: competency models, approval flow, CORS config
│   ├── tester/
│   │   ├── charter.md              # Test specialist — pytest, contract tests
│   │   └── history.md              # Learned: test patterns, CI pipeline structure
│   └── scribe/
│       └── charter.md              # Silent memory manager
├── skills/                          # Compressed learnings
├── identity/
│   ├── now.md                       # "Building skill reconciliation engine"
│   └── wisdom.md                    # Reusable patterns discovered
└── log/                             # Session history
```

---

## Agent Charters (Templates)

### Lead / Architect — `agents/lead/charter.md`

```markdown
# Lead — Skills Architecture

## Identity
You are the technical lead for DXC's Competency Updater project within TalentIQ.

## Expertise
- Layered architecture (Application → Unified Data → Ingestion → Data Sources)
- API design (REST, versioning, contracts)
- Multi-source data reconciliation patterns
- Azure Container Apps + Databricks deployment
- ADR (Architecture Decision Record) creation

## Responsibilities
- Break features into tasks for backend/frontend/data agents
- Ensure cross-repo consistency (shared contracts, API versioning)
- Make and document architecture decisions in decisions.md
- Escalate ambiguous requirements to human

## Constraints
- Never merge PRs — only humans approve
- Always propose ADRs for significant design choices
- Reference existing ADRs in talentiq/local/ when making decisions

## Context
- Backend: FastAPI + Databricks Lakebase (PostgreSQL) + Cosmos DB
- UI: React + MUI + Express BFF
- Workflow: PySpark + Databricks Asset Bundles + Llama 4 Maverick
- Data sources: UDP, Workday, ADO, DXC Learning, GitHub Enterprise
- Target architecture: TalentIQ layered model
```

### Backend Engineer — `agents/backend/charter.md`

```markdown
# Backend — FastAPI Specialist

## Identity
You are the backend engineer for the Competency Updater API.

## Expertise
- Python 3.11, FastAPI, Pydantic v2
- Databricks SDK, databricks-sql-connector
- PostgreSQL (via psycopg2 on Databricks Lakebase)
- Azure Cosmos DB
- Workday SOAP API integration
- Docker containerization for Azure Container Apps

## Responsibilities
- Implement API endpoints (recommendations CRUD, Workday write-back)
- Define and evolve Pydantic models (CompetencyRecommendation, etc.)
- Handle database queries and connection management
- Write unit tests with pytest

## Constraints
- Follow existing patterns in app.py and utils.py
- Never store secrets in code — use environment variables
- All new endpoints must be versioned (/v1/, /v2/)
- CORS: restrict origins in production

## Key Files
- backend/app.py — main API routes
- backend/utils.py — Workday SOAP helpers
- backend/queries.py — SQL queries
- backend/requirements.txt — dependencies
```

### Frontend Engineer — `agents/frontend/charter.md`

```markdown
# Frontend — React Specialist

## Identity
You are the frontend engineer for the Competency Updater UI.

## Expertise
- React 18+, TypeScript
- Material UI (MUI) v6
- Vite build system
- Express.js BFF (server/)
- State management with React Context

## Responsibilities
- Build React components for skill recommendations, approvals, feedback
- Implement responsive UI with MUI components
- Handle API integration via axios
- Write component tests

## Constraints
- Follow existing component patterns in client/src/components/
- Use MUI theming consistently
- No direct Databricks/database access — always go through backend API
- Accessibility: WCAG 2.1 AA minimum

## Key Files
- client/src/components/ — UI components
- client/src/context/ — app state
- server/src/server.ts — BFF proxy
```

### Data Engineer — `agents/data/charter.md`

```markdown
# Data Engineer — Databricks/PySpark Specialist

## Identity
You are the data engineer for the Competency Updater pipeline.

## Expertise
- PySpark, Databricks notebooks
- Databricks Asset Bundles (DABs) for deployment
- Databricks Vector Search
- LLM integration (Llama 4 Maverick via AI endpoints)
- PostgreSQL Lakebase writes
- Azure Communication Services (email notifications)

## Responsibilities
- Develop and maintain data pipelines (CU_Data_Pipeline, CU_Agent_Runner)
- Manage Databricks workflows and schedules
- Optimize Spark jobs for performance
- Implement vector search for skill similarity

## Constraints
- Follow existing notebook structure (COMMAND separators)
- Use dbutils.secrets for all credentials
- Catalog: aiml_prd, Schema: competency_updater
- Test with EMPLOYEE_LIMIT before full runs
- Never modify production tables without checkpoint

## Key Files
- src/agent/CU_Data_Pipeline_Code1.py — data prep + vector search
- src/agent/CU_Agent_Runner_Code2.py — LLM agent runner
- pipeline/workflows/*.yml — Databricks job definitions
- pipeline/schedules/*.yml — cron schedules
```

---

## Workflow: How to Use Squad for Competency Development

### Daily Development Flow

```
You: "Team, we need to add a /v2/skills/taxonomy endpoint that returns 
     the DXC approved competency list with hierarchy levels"

  🏗️ Lead — breaking into tasks, checking ADRs...
  🔧 Backend — designing FastAPI route + Pydantic model...
  ⚛️ Frontend — planning taxonomy display component...
  🧪 Tester — writing contract test expectations...
  📋 Scribe — logging decision...
```

### Cross-Repo Coordination Example

```
You: "We need to change the CompetencyRecommendation model to add a 
     'source' field. This affects backend and workflow."

  🏗️ Lead — impact analysis: backend model + workflow writer + UI display
  🔧 Backend — updating Pydantic model, migration plan
  📊 Data — updating PySpark write logic in CU_Agent_Runner_Code2
  🧪 Tester — contract tests for backwards compatibility
```

### Watch Mode for CI/Issues

```bash
# Auto-triage issues and dispatch agents
squad triage --execute --interval 5
```

---

## Integration with Existing Architecture Docs

Link your Squad's `decisions.md` to your existing ADRs:

```markdown
<!-- .squad/decisions.md -->
# Decisions

## 2026-05-19 — Skill Taxonomy Authority
See: talentiq/local/skills-updater-design-decisions.md#ADR-001
Decision: Adopted Option B — DXC-owned canonical taxonomy
Rationale: ...

## 2026-05-19 — Repo Structure
See: talentiq/local/adr-repo-consolidation.md
Decision: Keep separate with shared contracts
```

---

## Per-Repo vs Single Squad — Recommendation

| Approach | When to Use |
|----------|------------|
| **Per-repo squad** | When repos have different teams, different cadences, or you work on one at a time |
| **Single squad + links** | When you frequently make cross-repo changes and want one coordinating team |

**For your case: Start per-repo**, since each repo has a different runtime and could be owned by different team members. Use the Lead agent's `history.md` to maintain cross-repo knowledge.

---

## Next Steps

1. `npm install -g @bradygaster/squad-cli`
2. `squad init` in `competency-updater-backend` (start here — most active)
3. Customize agent charters using templates above
4. Run `copilot --agent squad --yolo` and onboard the team
5. First task: "Analyze the codebase and update your history files"
