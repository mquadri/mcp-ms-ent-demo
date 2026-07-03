# Maple TalentIQ — Skills & Competency Module
## AI Placement Architecture: Where AI Is Used, Where It Is Not, and How

**Status:** Decision record (v2 target architecture) · **Audience:** Technical architects, governance-minded product owners
**Scope:** ~130,000 employees · Workday is the system of record · Human-gated writes only

This README is a **decision**, not a survey. For every functional area of the module it states whether AI is used, which kind, at which model tier, behind which guardrails, and measured by which evaluation — or why AI is deliberately excluded. Every call is tied to a stated principle and a hard constraint.

---

## 1. AI-Placement Doctrine

Six principles govern every placement decision below. Each is derived directly from the module's hard constraints (explainability, human-gated governance, consume-don't-rebuild, right engine, cost/failure discipline, measured-not-vibes).

**P1 — AI proposes at the fuzzy edges; arithmetic scores and ranks; humans write.**
LLMs are used only where the task is linguistic/semantic and beyond rules (extraction, mapping the long tail, drafting proposals, critique). Anything that must be *defended to an employee or auditor* — a score, a rank, a written record — is deterministic, weighted, and source-traceable. AI output is an *input with provenance*, never the final authority.

**P2 — Embeddings widen recall; they never order what a human sees or what gets written.**
Vector similarity (bge-large-en 1024-d in pgvector/DiskANN) is a candidate-generation device. Final ordering is always a versioned deterministic formula whose per-factor breakdown can be printed. This is the direct consequence of the explicit rejection of opaque LLM confidence numbers.

**P3 — Consume before build.**
The ~55K-concept canonical catalog, its embeddings, its 16 grounded categories, deterministic `skillId`s, and the learned relationship weights (held 1.0 / adjacent ×0.9 / related ×0.5, tier-weighted 3/2/1, m-smoothed, aspiration term) come from the Career Navigator sibling. Any AI spend that re-derives taxonomy, dedup, or adjacency is waste and is prohibited.

**P4 — LLM judges sit behind cheap deterministic pre-filters, and every verdict is cached and evaluated.**
Wherever an LLM adjudicates (mapping tail, critique, conflict, level plausibility), deterministic checks run first and eliminate the bulk of cases for free. The LLM sees only the residue, emits a schema-conformant verdict, and that verdict is cached by input hash and scored against a gold set before it can gate anything.

**P5 — Cheapest model that passes the gold gate; batch whenever no human is waiting.**
Default workhorse is Llama-4-Maverick on Databricks `ai_query` (Spark-parallel, ~50% async discount). Claude Haiku for high-volume classification, Sonnet where cross-family judgment or interactive quality is needed, Opus only for low-volume/high-stakes work (answer-key drafting). Tier upgrades must be justified by a measured gold-set delta, not preference.

**P6 — No AI output touches a governed record without: schema conformance, catalog membership, evidence provenance, deterministic scoring overlay, and a human gate.**
The pipeline is propose → critique → deterministic Score A overlay → **human approval** → immutable audit → Workday sync. No exceptions in the MVP; a graduated autonomy ladder is defined but explicitly deferred until precision is measured (§7).

---

## 2. Placement Table

Legend: **AI-gen** = LLM generation · **AI-judge** = LLM classification/adjudication · **emb** = embeddings/vector · **agentic** = orchestrated multi-step · **det** = deterministic/rules · **consume** = from sibling catalog. Areas 16–17 added beyond the brief.

| # | Area | Decision | Technique + model tier | Rationale (principle) | Guardrail + eval | Risk → mitigation | Batch/Interactive |
|---|------|----------|------------------------|------------------------|-------------------|--------------------|--------------------|
| 1 | Ingestion & normalization of raw skill strings | **det** | Unicode/case/whitespace normalization, punctuation folding, alias & abbreviation tables, exact-match lookup vs catalog. No LLM. | P1, P5 — string hygiene is rules territory; an LLM here adds cost and nondeterminism for zero semantic gain. | Idempotent transforms; error-side-records for unparseable rows; conformance tests on a fixed corpus. | Silent alias drift → alias table is versioned, changes reviewed like code. | Batch |
| 2 | Canonical-skill mapping / dedup / consolidation | **consume + hybrid tail** | Consume sibling catalog + dedup process. Mapping incoming strings: (a) det exact/alias (~70–90% expected), (b) emb ANN top-k (bge-large-en, pgvector/DiskANN), (c) **AI-judge precision gate** (Haiku or Maverick batch) picks among top-k or **abstains**; abstentions route to sibling's operator-gated dedup queue. Verdicts cached by normalized-string hash. | P3, P4, P5 — never re-invent the catalog; LLM only adjudicates the ambiguous tail behind free filters. | Judge constrained to top-k candidate `skillId`s or `ABSTAIN`; schema-validated; gold set of ~2K labeled string→skillId pairs; precision gate ≥ target before verdicts auto-map. | Wrong mapping poisons downstream scores → abstain-by-default posture; sampled human audit of auto-mapped tail. | Batch |
| 3 | Skill extraction from CVs / unstructured docs | **AI-gen (constrained)** | LLM extraction with strict JSON schema: `{surface_string, evidence_span, doc_id, offsets}`. Tier: Maverick batch as default; promote to Sonnet only if gold-set recall/precision gap is measured. Extracted strings then flow through area 2 — the extractor **never assigns skillIds or levels**. | P1, P5, P6 — genuinely linguistic task rules can't do; output is raw evidence, not record. | PII-redacted input (area 17); span offsets mandatory (auditability: "this claim came from these words"); gold set of ~200 annotated CVs; precision/recall regression gate. | Hallucinated skills → catalog-membership enforced downstream; span must exist verbatim in source or row is rejected. | Batch |
| 4 | Skill adjacency & co-occurrence learning | **consume** | Sibling's learned relationships (held 1.0 / adjacent ×0.9 / related ×0.5, tier 3/2/1, proficiency-credited, m-smoothed, aspiration term). The designed-but-unbuilt semantic (embedding) upgrade is built **once, in the sibling pipeline**, and consumed — not duplicated here. | P3 — the single clearest consume-don't-rebuild call in the module. LLM-invented adjacency would be unexplainable and redundant. | Relationship weights sync with version stamps; downstream scores record which relationship version they used. | Sibling sunset orphans the pipeline → transfer *ownership of the pipeline* into TalentIQ ops (migration, not rebuild). | Batch (sync) |
| 5 | Semantic skill match (query/role ↔ person) | **hybrid: emb recall + det rank** | Query expansion via consumed relationships + bge ANN neighbors → candidate set. **Ranking is deterministic**: Score A × relationship weight × coverage, per-factor breakdown returned by the serve API. Optional Haiku for NL-query → structured-filter parsing (interactive, schema-out, keyword fallback). | P1, P2 — embeddings recall, arithmetic ranks. Opaque similarity as a rank was explicitly rejected. | Rank formula versioned; API returns factor breakdown with every result; parser eval: 200 NL queries → expected structured filters. | Embedding-space mismatch with sibling embeddings → see Open Decision OD-1 (§7). | Interactive |
| 6 | Recommendation ranking (people↔roles/assignments) | **det** | Weighted, source-traceable formula over Score A, consumed relationship weights, requirement coverage, recency. No LLM anywhere in the ordering path. | P1, P2 — "why ranked #1?" must have an arithmetic answer. | Every recommendation persists its factor vector; regression suite of frozen scenarios must reproduce ranks bit-for-bit across releases. | Formula gaming/staleness → weights versioned, changes A/B'd offline vs outcome telemetry (assignment acceptance). | Interactive (serve API) |
| 7 | Competency **proposal** (core updater) | **AI-gen** | v1 pattern retained and hardened: Databricks `ai_query`, **Maverick batch** proposes 2–8 competencies per employee, strictly from the approved competency list, schema `{competency, level, evidence_citations[], reasoning}`. Note: raw LLM "confidence" is **dropped from the record**; the deterministic Score A overlay replaces it before any human sees the proposal. Sonnet uplift evaluated on gold cohort before any tier change. | P1, P5, P6 — the canonical "AI proposes" slot; batch because no human waits; cheapest tier proven in v1. | Catalog-membership check; evidence citations must resolve to ingested rows; delta-trigger (re-propose only when evidence changed, keyed by evidence hash); human approval mandatory. Eval: gold cohort answer-key + live approval-rate telemetry. | Approval fatigue at 130K scale → deterministic pre-rank of proposals by Score A, cap per cycle, suppress low-evidence proposals. | Batch |
| 8 | Critique / verification of proposals | **AI-judge + det, lightly agentic** | Deterministic checks first (schema, catalog membership, citation resolution, duplicate/conflict with existing record) — free and binding. Then **cross-family LLM critic** (proposer = Maverick ⇒ critic = **Claude Sonnet**) judges substantive plausibility: evidence-supports-level, reasoning-consistency. Microsoft Agent Framework orchestrates propose → critique → **one** bounded revision → verify. No open-ended loops. | P4, P6 — judge behind a pre-filter; cross-family to avoid self-agreement bias. | Critic verdict schema `{pass|revise|reject, reason, evidence_gap}`; cached; critic itself evaluated against a human-labeled verdict gold set (meta-eval). Rejected proposals never reach the approval queue but are retained as side-records. | Critic too lenient/harsh → calibration against human approve/reject history; drift alarms on pass-rate. | Batch |
| 9 | Multi-source conflict resolution (Workday vs PSA vs CV) | **hybrid: det precedence + AI-judge residue + human** | Deterministic source-trust hierarchy resolves most conflicts: Workday-verified > certification > PSA project evidence > course > CV/self-claim, with recency decay. **AI-judge (Sonnet, batch)** only for residual *semantic* conflicts (e.g., project narrative contradicts claimed level). Verdict never silently resolves: it **flags** the conflict with both sources shown to the human approver. | P1, P4, P6 — precedence is policy, not inference; AI only interprets language; humans arbitrate anything touching a record. | Precedence table signed off by HR governance and versioned; judge gold set of labeled conflicts; every flag carries both source rows verbatim. | Precedence table encodes bad policy → governance review cycle; conflicts telemetry surfaces systematic source disagreement. | Batch |
| 10 | Proficiency-level inference | **hybrid: det rubric first, AI-gen assist on residue** | Deterministic rubric maps hard signals → levels (cert tier, role on project, duration, prior verified level). Where the rubric under-determines, the proposer LLM (area 7) suggests a level **with rubric-anchored reasoning and citations**. Level is never finalized by AI: it rides the same human approval gate. | P1, P6 — level is the most contested field ("why Expert?"); the defensible part must be arithmetic, the suggestion clearly labeled as such. | Rubric versioned and published to employees; LLM-suggested levels visually distinguished in the approval UI; eval: level-accuracy vs human-adjudicated gold, tracked separately from competency-accuracy. | Level inflation → asymmetric gate: upgrades demand stronger evidence class than confirmations; monitor approve-rate by level delta. | Batch |
| 11 | Deterministic Score A / Score B | **det — AI prohibited** | Score A (skill confidence): versioned weighted formula over source type, evidence count, recency, verification status, relationship credit. Score B (completeness): pure coverage arithmetic. AI-extracted evidence enters only as **inputs carrying a provenance flag and a lower source weight**. | P1, P2 — this *is* the constraint that rejected opaque LLM confidence. The scores are the module's audit spine. | Formula in code review; scorecard reproducibility test (same inputs ⇒ same score, bit-for-bit); per-factor explanation endpoint. | Weight disputes → weights are governance artifacts with change log, not model parameters. | Batch compute, interactive serve |
| 12 | NL explanations / "ask-any-agent" copilot | **AI-gen (narration only), tool-grounded** | Interactive **Sonnet** (Haiku for simple lookups) on Azure Container Apps, calling the shared **MCP competency tools** that return deterministic facts: score breakdowns, audit entries, proposal status, catalog definitions. The copilot **narrates retrieved facts; it never computes, estimates, or recalls a score**. Answers cite record IDs. | P1, P2, P6 — LLM as presentation layer over the deterministic truth, the one place generation quality justifies interactive Claude spend. | Tool-grounding enforced (no answer without a tool result); refusal on out-of-scope; groundedness eval: sampled answers checked claim-by-claim against tool outputs; PII scope limited to the asking employee/manager per RBAC in the MCP layer. | Fluent fabrication → hard groundedness gate + "show source" affordance on every claim. | Interactive |
| 13 | Autonomy / auto-apply policy | **det policy; AI autonomy = NO (MVP)** | No auto-apply. A **graduated autonomy ladder** is *specified now, activated later*: e.g., Rung 1 candidate = cert-backed exact-match confirmations where det checks pass, critic passes, Score A ≥ threshold — auto-applied **only** after measured precision on that exact slice exceeds an agreed bar, with N% sampling audit and instant kill-switch. The ladder policy engine itself is deterministic rules over AI outputs. | P6 — human gate is a hard constraint; the ladder makes future relaxation an *evidence decision*, not a vibe. | Ladder rungs, thresholds, and audit sampling rates are governance-approved config; activation requires the eval report attached to the change request. | Pressure to auto-apply early → ladder makes the required evidence explicit and non-negotiable. | n/a |
| 14 | Workday write-back governance | **det — AI prohibited** | Approved-items-only queue → idempotent SOAP writes with correlation IDs → immutable audit log → nightly reconciliation (Workday read-back vs expected state) → error side-records with bounded retry. | P1, P6 — the write path is the blast radius; nothing probabilistic belongs within it. | Contract tests against Workday sandbox; reconciliation diff must be zero or alarmed; every write traceable to an approval event and an approver identity. | Partial-failure drift → idempotency keys + reconciliation as the source-of-truth check, never re-derivation. | Batch |
| 15 | Evaluation / answer-key generation | **hybrid: AI-drafted, human-ratified** | **Claude Opus** (low volume, highest stakes) drafts candidate gold labels and clusters hard cases; **human adjudication is what makes them gold**. Frontier tier is justified precisely here: the yardstick's quality bounds everything it measures. Never grade a model solely against unreviewed output of its own family. | P5 (inverted: spend where stakes, not volume, are high), P6. | Two-rater adjudication on disagreements; gold sets versioned and frozen per release; refresh cadence tied to catalog version bumps. | Gold staleness → scheduled refresh; leakage → gold rows excluded from any prompt-tuning corpora. | Batch (offline) |
| 16 | Role-requirement extraction from job descriptions *(added)* | **AI-gen (constrained) → area 2 pipeline** | Same pattern as area 3: Maverick batch extracts `{requirement_string, mandatory|preferred, evidence_span}` from role/JD text; strings resolve to `skillId`s via area 2. Role profiles are then deterministic structures consumed by areas 5–6. | P1, P4 — linguistic extraction, deterministic consumption. | Schema + span provenance; gold set of ~100 annotated JDs; HR owner review for high-traffic roles. | JD boilerplate noise → mandatory/preferred separation + stop-list learned from labeled JDs (deterministic list, human-reviewed). | Batch |
| 17 | PII redaction / minimization pre-LLM *(added)* | **det — AI prohibited for the gate itself** | Deterministic redaction (structured-field stripping, pattern-based identifiers) applied before any document leaves the governed store for an LLM call, inside the Azure/VNet boundary, Managed-Identity auth end-to-end. An ML NER *assist* may flag candidates, but the **blocking gate is rules**, so its behavior is provable. | P1, P6 — a probabilistic privacy gate is an unexplainable privacy gate. | Redaction conformance corpus (known-PII fixtures must always redact); audit of every outbound payload class. | Novel PII shapes leak → conservative field allow-list (send only whitelisted evidence fields, not whole documents). | Batch |

---

## 3. Reference Architecture — the AI / Deterministic Split

```
┌──────────────────────────────────────────────────────────┐
│ CONSUMED PLANE (from Career Navigator sibling, sunset) │
│ • 55K canonical skill catalog (skillId, 16 categories) │
│ • catalog embeddings │
│ • learned relationships (1.0 / ×0.9 / ×0.5, tiers 3/2/1)│
└───────────────┬──────────────────────────────────────────┘
│ versioned sync (batch)
▼
┌─────────────────────────────── BATCH PLANE — Databricks (no human waiting) ──────────────────────────────┐
│ │
│ Workday / PSA / courses / DevOps / CVs / JDs │
│ │ │
│ ▼ │
│ [1] det normalization ──► [17] det PII gate ──► [3][16] LLM extraction (Maverick, schema+spans) │
│ │ │ │
│ ▼ ▼ │
│ [2] mapping: det exact/alias ──► emb ANN top-k ──► LLM-judge tail (Haiku, abstain-capable, cached) │
│ │ └── abstain ► operator dedup queue │
│ ▼ │
│ Canonical evidence store (Postgres/Lakebase) ──► projected People Graph (Apache AGE) │
│ │ │
│ ▼ │
│ [7] proposer (Maverick batch, catalog-constrained, evidence-cited, delta-triggered) │
│ ▼ │
│ [8] det checks ──► cross-family critic (Sonnet) ──► one bounded revision ──► verify (Agent Framework) │
│ ▼ │
│ [9] det precedence + conflict flags (Sonnet on semantic residue) │
│ ▼ │
│ [11] deterministic Score A overlay + Score B ◄── the ONLY numbers a human or auditor is asked to trust │
│ ▼ │
│ Approval queue (pre-ranked deterministically, capped) │
└────────────────────────────────────────────┬───────────────────────────────────────────────────────────────┘
▼
┌───────────── GOVERNANCE PLANE (the human gate) ─────────────┐
│ Approval UI: evidence, citations, Score A breakdown, │
│ conflict flags, LLM-suggested levels visibly labeled │
│ approve / reject ──► immutable audit log │
│ [14] det Workday SOAP write-back + reconciliation │
└───────────────────────────────────────────────────────────────┘

┌───────────── ONLINE PLANE — Azure Container Apps (a human is waiting) ─────────────┐
│ Versioned serve API: [5] emb recall → det rank · [6] det recommendations │
│ [12] Copilot (Sonnet/Haiku) ──► shared MCP competency tools ──► deterministic │
│ facts only (scores, audits, catalog defs); narration, never computation │
└──────────────────────────────────────────────────────────────────────────────────────┘
```

Three structural facts of this diagram carry the whole design. First, **every AI output passes through deterministic constraint before a human sees it**: extraction passes through catalog mapping, proposals pass through deterministic checks, the critic, conflict precedence, and finally the Score A overlay — so the approval UI shows AI *suggestions* framed by arithmetic *facts*. Second, **the human gate is a plane, not a step**: approval, audit, and write-back form a closed governance loop that no batch or online component can bypass. Third, **the online plane contains no generative decision-making** — the only interactive LLM is the copilot, and it is architecturally incapable of asserting anything it did not retrieve from an MCP tool.

---

## 4. Where AI Must NOT Be Used — Anti-Patterns

Each prohibition ties to a hard constraint; these are design invariants, not preferences.

**AP-1: No LLM-produced number in Score A/B or any rank shown to a human.** The module exists because an opaque LLM confidence was rejected. LLM "confidence" fields are dropped at ingestion of the proposal; only the deterministic overlay survives. *(Constraint 1; P1, P2.)*

**AP-2: No AI in the Workday write path.** No generative retry logic, no LLM-composed SOAP payloads, no "smart" reconciliation. The write path must be boring, idempotent, and provable. *(Constraints 1–2; P6.)*

**AP-3: No AI-invented taxonomy or adjacency.** Rebuilding canonicalization or relationship learning with an LLM duplicates a production system and produces unexplainable edges. *(Constraint 3; P3.)*

**AP-4: No auto-apply, and no critic-as-approver.** The critic filters what reaches humans; it never substitutes for them. Autonomy arrives only via the measured ladder (§2, area 13). *(Constraint 2; P6.)*

**AP-5: No embeddings as final ranking.** Cosine similarity answers "what might be relevant," never "who is #1 and why." *(Constraint 1; P2.)*

**AP-6: No unconstrained generation into governed fields.** Every LLM emitting toward a record is schema-bound, catalog-constrained, and citation-required; free text lives only in `reasoning` and copilot narration. *(Constraints 1, 5; P6.)*

**AP-7: No probabilistic PII gate.** The redaction boundary is rules; ML may only add flags on top. *(Constraint 5 + VNet/PII posture.)*

**AP-8: No "call and hope" at 130K scale.** Every LLM stage requires batching, caching by input hash, structured-output validation, rate limits, and error side-records — otherwise it does not ship. *(Constraint 5; P5.)*

**AP-9: No self-graded evaluation.** A model family is never the sole grader of its own outputs; gold is human-ratified. *(Constraint 6; area 15.)*

---

## 5. Evaluation Strategy

Every AI-bearing component ships with a frozen, versioned gold set and a CI regression gate; a failed gate blocks release exactly like a failed unit test.

**Gold sets (human-ratified, Opus-drafted).** (a) *Mapping*: ~2K labeled `raw string → skillId | ABSTAIN` pairs stratified across the 16 categories and the ambiguity tail. (b) *Extraction*: ~200 span-annotated CVs and ~100 JDs. (c) *Proposal answer-key*: a gold cohort of employees with adjudicated correct competency sets and levels, refreshed each catalog version. (d) *Critic meta-eval*: human-labeled pass/revise/reject verdicts on historical proposals. (e) *Conflict*: labeled semantic-conflict cases. (f) *Copilot groundedness*: sampled Q→A pairs checked claim-by-claim against MCP tool outputs.

**Gates.** Mapping judge: precision on auto-mapped decisions is the binding metric (abstention is free; wrong mapping is not). Extraction: precision and recall both gated — hallucination (span not verbatim in source) is an automatic row failure. Proposal: competency-set F1 and level accuracy tracked separately; regressions vs the prior release fail the build. Critic: agreement with human verdicts, plus pass-rate drift alarms in production. Ranking (areas 5–6, deterministic): bit-for-bit reproduction of frozen scenario ranks — determinism itself is the test. Copilot: groundedness ≥ threshold; any fabricated claim in the sample is a release blocker.

**Online telemetry as the second loop.** Approval/rejection rates per competency, per source mix, and per level delta are the production signal that gold sets can't provide; systematic divergence between offline gold scores and online approval rates triggers a gold-set refresh, not a threshold fudge. Cached judge verdicts are re-scored whenever the catalog version bumps.

**Conformance, not just accuracy.** Schema validity, catalog membership, citation resolvability, and PII-redaction fixtures run as hard conformance suites on every pipeline release — these are pass/fail, with no thresholds to negotiate.

---

## 6. Sequencing

**Phase 0 — Consume (unblocks everything).** Sync the sibling catalog, `skillId`s, categories, and relationship weights into Postgres/Lakebase and project into AGE. Resolve **OD-1 (embedding space)** now — it gates areas 2 and 5. Transfer ownership of the catalog dedup/canonicalization pipeline into TalentIQ ops before the Neo4j sunset date. *Consumed: catalog, relationships, embeddings, dedup process. Built here: nothing yet.*

**Phase 1 — Deterministic spine.** Normalization (1), PII gate (17), mapping stages a+b (2), Score A/B (11), approval queue plumbing, Workday write-back + reconciliation (14), immutable audit. This phase contains **zero LLM calls** and delivers the audit backbone every later phase depends on. *Built here: all of it.*

**Phase 2 — AI proposal loop, hardened.** Eval harness and first gold sets (15) — built *before* the components they gate. Then mapping judge tail (2c), extraction (3, 16), proposer v2 with Score A overlay (7), deterministic checks + cross-family critic under Agent Framework (8). v1's Maverick job is the migration seed, not a rewrite.

**Phase 3 — Online plane.** Versioned serve API, semantic match (5), deterministic recommendations (6), copilot over MCP tools (12) with RBAC scoping.

**Phase 4 — Governance depth.** Conflict precedence table + semantic-residue judge (9), level rubric publication + LLM-assist labeling in the UI (10), autonomy-ladder specification signed off (13, *specified only*).

**Deferred deliberately.** Auto-apply activation (needs Phase 2/4 precision evidence); the semantic adjacency upgrade (built once in the sibling pipeline, consumed when ready); any proposer tier upgrade to Sonnet (needs a measured gold delta that pays for the cost multiple at 130K scale).

---

## 7. Top Risks, Open Decisions, Final Recommendation

**Risks → mitigations.**
**R1 — Embedding-space mismatch.** The sibling's catalog embeddings may not match the module's chosen query-side model; mixing spaces silently degrades recall. → Standardize on **one** model (bge-large-en 1024-d preferred: self-hostable, cheaper, no external dependency) and re-embed the catalog once, version-stamped. **R2 — Approval fatigue.** 130K employees × 2–8 proposals can drown approvers and degrade the human gate into rubber-stamping. → Deterministic pre-ranking, per-cycle caps, delta-only re-proposal, suppression of low-Score-A items; monitor time-to-decision and blanket-approve patterns as gate-health metrics. **R3 — Catalog orphaning at sibling sunset.** The consume decision assumes a living catalog. → Pipeline ownership transfer is a Phase 0 exit criterion, not an afterthought. **R4 — Critic miscalibration** (too lenient = noise reaches humans; too harsh = silent recall loss). → Meta-eval against human verdicts, pass-rate drift alarms, rejected-proposal side-records reviewed in samples. **R5 — Cost creep.** Millions of rows × per-row LLM calls compounds quietly. → Delta-triggering, verdict caching by input hash, batch-only defaults, and per-stage unit-cost dashboards from day one.

**Open decisions (each named with the evidence that resolves it).**
**OD-1:** Single embedding model (bge vs ada-002 legacy) — resolved by a recall benchmark of both spaces on the mapping gold set. **OD-2:** Maverick vs Sonnet as proposer — resolved by gold-cohort F1/level-accuracy delta priced against the cost multiple at full scale. **OD-3:** Conflict precedence ordering (is a fresh PSA signal ever allowed to outrank a stale Workday-verified entry?) — resolved by an HR-governance ruling, not engineering. **OD-4:** Autonomy Rung 1 threshold (precision bar and audit-sampling rate for cert-backed confirmations) — resolved by Phase 2 measured precision plus a governance sign-off.

**Final recommendation.** Build the deterministic spine first and treat it as the product's spine forever: canonical store, Score A/B, approval loop, audit, and Workday write-back contain no AI and are what make every AI component safe to add. Consume the sibling's catalog and relationships wholesale and take ownership of that pipeline before its sunset. Place LLMs in exactly five jobs — extraction, mapping-tail adjudication, proposal drafting, cross-family critique, and tool-grounded narration — always batch-first, schema-bound, catalog-constrained, cached, and gated by human-ratified gold sets, with the cheapest passing tier (Maverick/Haiku workhorse, Sonnet where judgment or interaction demands it, Opus only for the yardstick). Keep every number an employee or auditor will ever question deterministic, and keep every write human-approved until the measured autonomy ladder — not enthusiasm — says otherwise.
