# Skills Scoring — Complete Meeting Brief

> **Date:** 2026-05-21  
> **Context:** Scoring framework discussion for DXC Skills Updater  
> **Deliverable:** What exists today, what the new design proposes, gap between them, and implementation notes

---

## 1. NEW DESIGN: Scoring Framework (from slides)

### Score A — Skill Confidence (Per Recommendation)

"How sure are we this skill belongs in this employee's profile?"

| Tier | Signal | Weight | Data Source |
|------|--------|--------|-------------|
| **Tier 1** | Workday + PSA (assignment with skill, WD profile / adjacent specialization) | **30** (15+15) | `employee_skills` + `pse_resource_skill_request` |
| **Tier 2** | Developer observability (GitHub commits, ADO ticket match, SABA training) | **20** (10+8+8) | GitHub API, Azure DevOps, DXC Learning |
| **Tier 3** | New-hire interview / AI Interviews (tenure < 6 months, plugs empty PSA history) | **15** | AI Interviewer results (TalentIQ v2) |
| **Tier 4** | Certifications (active certification on this skill) | **15** | `employee_skills` WHERE src_skill_nm='CERTIFICATION' |
| **Tier 5** | CV mention (linked to CV refresh date) | **10** | Resume/CV store |
| **Tier 6** | Role taxonomy + JD (UDP role match, JD specialization includes skill) | **10** | UDP taxonomy tables + `job_profile_navigator` |

**Formula:** Weighted sum of signals, capped at 100 · recency decay applies on PSA + Tier 1  
- Decay: `1.0 ≤6mo`, `0.7 6-12mo`, `0.4 12-24mo`  
- **+10 multi-source bonus** when ≥3 independent sources confirm  
- Configurable weights

### Score B — Profile Completeness (Per Employee)

"How fulfilled and current is this employee's skill profile?"

| Tier | Signal | Points | Source |
|------|--------|--------|--------|
| **Tier 1** | Workday profile — competencies listed (cap 10) | **40** | `employee_skills` count |
| **Tier 2** | Certifications (2 pts each, capped) | **20** | Certification records |
| **Tier 3** | CV — attached (5) + refreshed < 12 mo (10) | **15** | CV/resume metadata |
| **Tier 4** | New-hire interview / AI Interviews (tenure < 6 mo only, reweights if N/A) | **10** | Interview completion |
| **Tier 5** | Dev observability + hygiene (GitHub/ADO trainings 12 mo + 6-mo freshness) | **10** | GitHub + ADO + DXC Learning |
| **Tier 6** | Peer assessments / Performance reviews | **5** | Performance system |

**Thresholds:** < 40 = "Needs Work" | 40–70 = "Healthy" | 70+ = "Strong"

**Edge Cases:**
- New hires can reach 110 → capped at 100
- CV-blocked regions (FR/BE/NL/DE) effective ceiling = 85
- Non-developer roles skip Tier 6 (rescaled to 100)
- LOA = N/A, not zero

---

## 2. WHAT EXISTS TODAY (Current Competency-Updater Code)

### Current Scoring: LLM Confidence Only

| What | How | Where in Code |
|------|-----|---------------|
| **Confidence %** | LLM (Llama 4 Maverick) outputs 0-100% per recommended competency | `CU_Agent_Runner_Code2.py` line 154: `"confidence": {"type": "integer"}` |
| **Level** | LLM outputs: beginner/experienced/expert/guru | `CU_Agent_Runner_Code2.py` line 152: `"level": {"type": "string"}` |
| **Reasoning** | LLM outputs free-text reasoning | `CU_Agent_Runner_Code2.py` line 154 |

### Current Data Signals Already Collected (in `CU_Data_Pipeline_Code1.py`)

| Signal | Status | Maps to New Tier |
|--------|--------|------------------|
| Workday competencies (`wf_competencies`) | ✅ Collected | Tier 1 — Profile check |
| Workday certifications (`wf_certifications`) | ✅ Collected | Tier 4 — Certifications |
| PSA project skills (`psa_competencies`, `psa_certification`, `psa_free_text_skill`) | ✅ Collected | Tier 1 — PSA assignment |
| PSA offering roles (`psa_offering_roles`) | ✅ Collected | Tier 6 — Role taxonomy |
| PSA assignment roles (`psa_assignment_roles`) | ✅ Collected | Tier 6 — Role taxonomy |
| Specializations (via UDP taxonomy) | ✅ Collected | Tier 6 — JD specialization |
| F1 missing competencies (PSA → UDP validated) | ✅ Computed | Tier 1 helper |
| F2 missing competencies (specialization → UDP) | ✅ Computed | Tier 6 helper |
| F3 missing competencies (assignment skill+role → UDP) | ✅ Computed | Tier 6 helper |
| GitHub commits | ⚠️ Referenced in prompt but unclear if collected in pipeline | Tier 2 — Developer observability |
| Azure DevOps tasks | ⚠️ Referenced in prompt but unclear if collected in pipeline | Tier 2 — Developer observability |
| DXC Learning / SABA courses | ⚠️ Referenced in prompt but unclear if collected in pipeline | Tier 2 — Training |
| Job description / profile | ✅ `job_profile_navigator` table exists | Tier 6 — JD |

### Current Limitations

| Limitation | Impact on New Scoring |
|-----------|----------------------|
| **No deterministic scoring** — confidence is 100% LLM-generated (opaque) | Can't explain why a score is 75 vs 85 |
| **No recency decay** — PSA data used regardless of age | Stale assignments inflate confidence |
| **No multi-source bonus** — signals aren't counted independently | Single-source assertions weighted same as multi-confirmed |
| **No per-employee profile completeness score** — only per-recommendation confidence | Can't identify "empty profile" employees proactively |
| **No CV/Resume signal** — not collected | Tier 5 missing entirely |
| **No AI Interview results** — not integrated | Tier 3 missing entirely |
| **No peer/performance review data** — not connected | Score B Tier 6 missing |
| **Fuzzy match at 90% threshold** — binary (match or not) | No partial credit for near-matches |

---

## 3. GAP: What Needs to Be Built

### Score A — Skill Confidence Engine

| # | Gap | Effort | Dependency |
|---|-----|--------|-----------|
| A1 | **Deterministic scoring logic** — replace opaque LLM confidence with weighted tier formula | High | Core refactor of agent output |
| A2 | **Recency decay function** — timestamp-based multiplier on PSA/Tier 1 signals | Medium | Need `assignment_date` or `last_active_date` from PSA |
| A3 | **Multi-source counter** — count independent sources confirming each skill, apply +10 bonus | Medium | Requires source tagging per skill assertion |
| A4 | **GitHub signal extraction** — parse commits for language/framework signals | High | Need GitHub Enterprise API connector (Stream A shows this exists) |
| A5 | **ADO signal extraction** — ticket type, story size, velocity | Medium | Azure DevOps API connector |
| A6 | **CV/Resume parsing** — extract skills + track CV refresh date | High | NLP pipeline or structured CV store |
| A7 | **AI Interview integration** — receive validation scores from TalentIQ v2 | Medium | API contract with AI Interviewer module |
| A8 | **Certification validation** — match cert to skill (cert "AWS Solutions Architect" → skill "AWS") | Medium | Mapping table cert → competency |
| A9 | **Configurable weights** — allow tuning tier weights without code changes | Low | Config table or environment variable |

### Score B — Profile Completeness Engine

| # | Gap | Effort | Dependency |
|---|-----|--------|-----------|
| B1 | **Completeness scoring logic** — new calculation, doesn't exist today | High | New pipeline stage |
| B2 | **CV attachment + freshness check** | Medium | CV store metadata (where are CVs stored?) |
| B3 | **Peer/Performance review integration** | Medium | Performance system API (which system?) |
| B4 | **Threshold-based targeting** — drive notifications from completeness score | Low | Builds on notification workflow |
| B5 | **Edge case handling** — region blocks, non-dev rescaling, LOA, new hires | Medium | Business rules engine |
| B6 | **Dashboard metrics** — adoption acceptance rate, rejection rate | Medium | Analytics store |

---

## 4. DATA SOURCES: Current vs Needed

| Data Source | Current Pipeline | New Scoring Needs | Status |
|---|---|---|---|
| **Workday profile** (`employee_skills`) | ✅ Used | Score A Tier 1, Score B Tier 1 | Ready |
| **PSA assignments** (`pse_resource_skill_request`) | ✅ Used | Score A Tier 1 | Ready — needs recency timestamp |
| **PSA offering/assignment roles** | ✅ Used | Score A Tier 6 | Ready |
| **UDP taxonomy** (offering_role, specialization, skill_catalog) | ✅ Used | Score A Tier 6 | Ready |
| **Job profile navigator** | ✅ Exists | Score A Tier 6 | Ready |
| **DXC approved competency list** | ✅ Used + vector index | Validation | Ready |
| **GitHub Enterprise** | ⚠️ Referenced in prompt | Score A Tier 2 (languages, commits, PR acceptance) | **Needs connector** — Stream A shows ~7K developers |
| **Azure DevOps** | ⚠️ Referenced in prompt | Score A Tier 2 (ticket type, velocity) | **Needs connector** |
| **DXC Learning / SABA** | ⚠️ Referenced in prompt | Score A Tier 2 (technical courses) | **Needs connector** |
| **SonarQube** | ❌ Not present | Score A Tier 2 (code quality, languages) | **New — Investigating** per slide |
| **Databricks notebooks** | ❌ Not present | Score A Tier 2 (Python/SQL/R ownership) | **New** — Stream A |
| **CV / Resume store** | ❌ Not present | Score A Tier 5, Score B Tier 3 | **Needs source identified** |
| **AI Interviewer results** | ❌ Not present | Score A Tier 3, Score B Tier 4 | **Needs API from TalentIQ v2** |
| **Peer/Performance reviews** | ❌ Not present | Score B Tier 6 | **Needs source identified** |
| **TalentIQ heatmap** | ❌ Not present | Stream B — demand forecast | **Next phase** |
| **AI agents usage** (Copilot/Claude) | ❌ Not present | Stream B — tool-use frequency | **Next phase** |
| **Confluence/SharePoint** | ❌ Not present | Stream B — topics covered | **Next phase** |
| **ESL (project specialisation)** | ❌ Not present | Stream B — GIS staff | **Next phase** |
| **Salesforce** | ❌ Not present | Stream B — client engagement | **Next phase** |
| **Learning platform** | ❌ Not present | Stream B — upskilling recs | **Next phase** |

---

## 5. ARCHITECTURE: How Scoring Fits

### Current Flow (LLM-only):
```
Data Pipeline (Code1) → Preprocessed Table → LLM Agent (Code2) → confidence % → PostgreSQL → UI
```

### New Flow (Deterministic + LLM):
```
Data Pipeline (Code1)
  → Collect all tier signals per employee per skill
  → Compute deterministic Score A (weighted sum + decay + bonus)
  → Compute Score B (profile completeness)
  → Pass Score A as EVIDENCE to LLM (replaces opaque confidence)
  → LLM uses score + reasoning to generate recommendation
  → Final output: deterministic score + LLM recommendation + reasoning
  → PostgreSQL → UI + Notifications
```

### Key Architectural Shift:
> "Deterministic numbers computed from source signals first, then passed into the LLM as evidence and replaces today's opaque 60-100% LLM-generated value."

This means:
1. **Score A replaces `confidence` field** in current `CompetencyRecommendation` model
2. **LLM still generates level + reasoning** but confidence is now deterministic
3. **Score B is new** — triggers notifications (Tier 1 daily scan + Tier 2 quarterly L5 escalation)

---

## 6. REFERENCE: AI Staffing Assistant Scoring

The `ai-project-staffing-assistant` uses a **fit score** concept:

| Aspect | ai-project-staffing-assistant | Competency Updater Scoring |
|--------|-------------------------------|---------------------------|
| **Purpose** | Match consultant to project | Validate skill belongs in profile |
| **Direction** | Person → Project fit | Signal → Skill confidence |
| **Score type** | Fit % (how well skills match project needs) | Confidence % (how sure skill is real) |
| **Model** | OpenAI generates fit score | Llama 4 generates confidence (changing to deterministic) |
| **Inputs** | Consultant skills + project requirements | Multi-source signals per skill |
| **Output** | Ranked project list with % | Recommended skill with confidence + level |

**Reusable patterns from staffing assistant:**
- Structured scoring with breakdown (fit score shows per-dimension match)
- Threshold-based recommendations (only show >85% fit)
- Could share: skill taxonomy, worker skill data, matching logic

---

## 7. QUESTIONS FOR YOUR SCORING MEETING

### Implementation Questions:

1. **Where do GitHub/ADO/DXC Learning signals currently live?** The LLM prompt references them but I don't see collection code for all employees. Is this data being passed to the agent today?

2. **How does recency decay apply?** Is `assignment_date` from PSA the timestamp? What about Workday profile skills (they have `src_sys_upd_ts`)?

3. **Score A formula — additive or tiered?** If an employee has Tier 1 (30) + Tier 2 (20) + Tier 4 (15) = 65, but they DON'T have Tier 3/5/6, is the score 65 or rescaled to 100?

4. **What constitutes "independent sources"?** For the +10 multi-source bonus, does Workday + PSA count as 2 sources, or are they considered the same upstream system?

5. **Where is the CV/Resume stored?** FDS? SharePoint? Need location + API to check freshness.

6. **Score B Tier 6 — which Performance Review system?** Workday Performance? Another HR tool?

7. **Should Score A replace LLM confidence entirely, or be passed alongside it?** The slide says "replaces" but the LLM could still add value (e.g., when signals are weak).

### Design Questions:

8. **Is Score A computed BEFORE the LLM runs?** (Score feeds INTO prompt as evidence?) Or AFTER? (Score is computed on LLM output?)

9. **Score B drives notifications (slide 05) — is this a separate pipeline or same run?** The notification workflow triggers on 6-month staleness, which is Score B Tier 1 logic.

10. **How do Stream A (Developers ~7K) and Stream B (All employees 100%) merge?** Developer signals only apply to ~5% of workforce. Non-devs get rescaled scoring.

11. **The vector search narrows ~4,500 approved competencies to top 200/employee — does this happen BEFORE or AFTER scoring?** If before, scoring only applies to the narrowed list. If after, we score all 4,500 (expensive).

12. **Notification Tier 2 (L5 quarterly escalation) — does it use Score B directly?** "Profile crosses 6-mo staleness" seems like Score B < 40 = "Needs Work" → trigger.

---

## 8. IMMEDIATE IMPLEMENTATION PRIORITIES

| Priority | Item | Rationale |
|----------|------|-----------|
| **P0** | Define Score A computation as a Spark UDF/column | Foundation — everything depends on this |
| **P0** | Add recency timestamps to PSA signals | Decay formula needs dates |
| **P1** | Build Score B as separate pipeline stage | Drives notification targeting |
| **P1** | Modify LLM prompt to receive Score A as evidence (not generate confidence) | Core architectural shift |
| **P2** | Connect GitHub/ADO/Learning APIs (Stream A) | Fills Tier 2 for developers |
| **P2** | Add CV freshness check | Fills Tier 5 |
| **P3** | AI Interview integration | Depends on TalentIQ v2 availability |
| **P3** | Stream B sources | Next phase signals |
