TalentIQ Architecture

Draft v1.0
Contributed by Anil Dwarakanath
7 June 2026
 
Table of Contents
1. Platform architecture	3
1.1 Components	3
1.2 Security and connectivity	4
2. Production scale (Azure PostgreSQL)	4
3. How a question is answered	5
3.1 Tool selection by reasoning, not rules	5
3.2 Cypher path — multi-criteria search	5
3.3 Cypher aggregation — dashboards	6
3.4 Vector path — semantic similarity	8
3.5 Full-text path	8
3.6 CV generation and RFP matching	8
4. Natural language to Cypher	8
4.1 Live schema discovery	8
4.2 AGE dialect constraints	9
4.3 Result typing	9
4.4 Agent loop vs. template NL2Cypher	9
5. Comparison with a Neo4j-native stack	10
5.1 Neo4j vector search	10
5.2 Engine and index comparison	10
5.3 Managed platform model	10
5.4 Databricks ingestion	11
6. Comparison with OntoBricks / OWL	12
7. One PostgreSQL instance, four query paradigms	13
7.1 Graph (Apache AGE)	14
7.2 Vector (DiskANN)	14
7.3 Full-text	14
7.4 Hybrid in one transaction	14
8. Summary	15
9. To Do / Open items	15

 
1. Platform architecture
TalentIQ is an Azure-native, VNet-integrated platform. Data is ingested from Workday/Luxoft/PSA sources through the Unified Data Platform (UDP) on Azure Databricks, materialized into a single Azure Database for PostgreSQL Flexible Server that holds the property graph, the embedding vectors, and the full-text indexes, and served by Container Apps (MCP server, FastAPI backend, demo UI) under Microsoft Entra identity.
 
Figure 1 — Deployment architecture: UDP ingestion to PostgreSQL graph, Container Apps backend and frontend, Microsoft Entra throughout.
1.1 Components
Tier	Service	Responsibility
Ingestion	Azure Databricks + UDP/Unity Catalog	Streams 19 gold Delta tables; build_graph_records bulk-loads AGE nodes/edges; Azure OpenAI embeddings pipeline (async, batched, ADLS Gen2 checkpoints) upserts vectors
Data	Azure PostgreSQL Flexible Server (PG 16)	One instance hosting Apache AGE (graph), pgvector + DiskANN (vectors), tsvector/pg_trgm (full-text), B-tree/relational; zone-redundant HA, read replica, automated backups + PITR
Tooling	MCP Server (FastMCP, Streamable HTTP)	Exposes get_graph_schema, query_using_sql_cypher, search_graph, vector_search, list_cv_templates, generate_employee_cv via a PGAgeHelper connection pool
Backend	FastAPI Container App	Validates Entra JWT, builds chat history, runs the Agent Framework orchestrator (triage → query/CV/document agents), streams NDJSON/SSE responses
Frontend	React demo/test UI Container App	Entra sign-in (Easy Auth ingress, HTTPS only), forwards an on-behalf-of token to the backend over the internal network, renders streamed answers + the Run Log
Identity	Microsoft Entra ID	User sign-in (OAuth2/OIDC), service-to-service and database access via Managed Identity (passwordless PostgreSQL), RBAC and group membership

1.2 Security and connectivity
•	Passwordless throughout. Databricks and the Container Apps authenticate to PostgreSQL with Entra Managed Identity tokens; no database passwords are stored.
•	Private data plane. PostgreSQL is reachable only via a Private Endpoint (private IP in a delegated subnet, privatelink.postgres.database.azure.com); there is no public access. A Private DNS Zone resolves the FQDN to the private IP.
•	Network controls. VNet with delegated subnets, NSG/firewall deny-by-default, Private Link, Key Vault for secrets/CMK references, TLS in transit, CMK at rest.
•	Identity at every hop. User → frontend (Entra sign-in) → backend (JWT validation + on-behalf-of) → MCP/agent → PostgreSQL (MSI). The same Entra tenant governs all tiers.
2. Production scale (Azure PostgreSQL)
The graph and vector store run on Azure PostgreSQL Flexible Server. Current loaded volumes from the pipeline validation phase:
Graph: 24 node labels, 32 edge labels, ~14.7M vertices, ~50M edges.
Largest node labels	Count	Largest edge labels	Count
Allocation	12,344,406	HAS_ALLOCATION	12,344,531
Assignment	1,154,447	ALLOCATION_FOR_RESOURCE	12,341,895
ResourceRequest	314,355	IN_PERIOD	12,344,406
ResourceProfile	236,026	ALLOCATION_FOR_REQUEST	2,473,660
Employee	159,182	HAS_SKILL	1,727,305
Project	144,283	ASSIGNED_RESOURCE	1,154,160
Skill	106,081	ASSIGNMENT_FOR_PROJECT	1,154,215
Account	12,372	IN_REGION	549,741
Certification	8,126	OWNS_ACCOUNT	454,147
JobExperience	8,420	REQUESTS_SKILL	463,015

Vectors (DiskANN sidecar tables): v2_employee_embeddings = 160,135 rows (profile/skills/experience vectors), v2_job_experience_embeddings = 15,421 rows. Embedding dimension 1536 (text-embedding-ada-002). Project/request/taxonomy embedding tables are provisioned and currently empty.
This is the scale point relevant to the index choices in Sections 5–7: a 12.3M-row Allocation fact, a 1.15M-row Assignment fact, and a 1.7M-edge HAS_SKILL relationship all live in one managed instance alongside the DiskANN vector index, queried through the same connection pool.
3. How a question is answered
A user types a sentence in the demo UI. The frontend forwards it (with an Entra on-behalf-of token) to the FastAPI backend, which runs the Agent Framework orchestrator. The triage agent classifies intent and hands off to a specialist; the specialist selects MCP tools. The Run Log panel on the right of each screenshot records every step — the handoff, the schema fetch, the generated query, the row count, and the timing.
3.1 Tool selection by reasoning, not rules
The agent chooses a retrieval paradigm from the wording of the request; there is no rules engine. The three captured runs and the demo prompt library exercise each path:
Use case	Example prompt	Tool the agent selects
Multi-criteria talent search	"Find Azure data engineers with Databricks and Python experience"	get_graph_schema → query_using_sql_cypher (Cypher)
Semantic similarity	"Find people similar to an Azure data engineering resource request"	vector_search (DiskANN), then Cypher enrichment
Aggregation / dashboard	"Show open resource requests by status"	query_using_sql_cypher (Cypher aggregation)
Two-dimension rollup	"Show demand by practice and region"	query_using_sql_cypher (two-hop Cypher)
Free-text / fuzzy lookup	"Who has PMP certification or project management experience?"	search_graph (tsvector + pg_trgm)
CV generation	"Generate a CV for jessica.berry@dxc.com"	list_cv_templates → generate_employee_cv
RFP / tender matching	upload an RFP, then "match candidates to it"	Document agent extracts roles → vector_search per role → Cypher fallback

3.2 Cypher path — multi-criteria search
Prompt: "Find Azure data engineers with Databricks and Python experience." The Run Log shows the reasoning trace: HANDOFF → Query Agent, then get_graph_schema(graph=talent_udp_dbx) returning SCHEMA: 25 nodes, 37 edges, 0 enum-like properties, then the generated Cypher:
SELECT * FROM ag_catalog.cypher('talent_udp_dbx', $$
  MATCH (e:Employee)-[hs1:HAS_SKILL]->(s1:Skill),
        (e)-[hs2:HAS_SKILL]->(s2:Skill),
        (e)-[:LOCATED_IN]->(l:Location)
  WHERE s1.name =~ '(?i).*azure.*'
    AND s2.name =~ '(?i).*databricks.*|.*python.*'
$$) AS (...);

 
Figure 2 — Multi-criteria talent search: the agent discovers the schema and generates a multi-skill Cypher join (image.png).
Results render as a table (Full name, Email, Business title, Country, Matched skills). The agent appends a reasoning note: "the graph does not expose a structured 'data engineer' flag, so I matched on Azure plus Databricks/Python skills and included titles where available" — a structural decision made from the discovered schema, not a hardcoded mapping.
3.3 Cypher aggregation — dashboards
Prompt: "Show open resource requests by status." The agent reuses the cached schema and emits an aggregation:
SELECT * FROM ag_catalog.cypher('talent_udp_dbx', $$
  MATCH (r:ResourceRequest)
  WITH r.status_nm AS status, count(r) AS open_request_count
  RETURN status, open_request_count
  ORDER BY open_request_count DESC
$$) AS (status agtype, open_request_count agtype);

 
Figure 3 — Cypher aggregation rendered as table + bar chart; Run Log shows 12 rows in 443 ms (image2.png).
 
Figure 4 — Two-hop demand rollup by practice and region; 200 rows in 1416 ms (image3.png).
The companion prompt "Show demand by practice and region" produces a two-hop Cypher join (ResourceRequest -[:IN_PRACTICE]-> Practice, -[:IN_REGION]-> Region) returning 200 rows in 1416 ms. These aggregations run directly over the 314k-row ResourceRequest label.
3.4 Vector path — semantic similarity
Prompt: "Find people similar to an Azure data engineering resource request." Here the criteria are not enumerable as graph predicates, so the agent calls vector_search: it embeds the request text, runs a DiskANN nearest-neighbor scan over v2_employee_embeddings.skills_embedding, and returns a ranked candidate list with cosine similarity. It then issues a Cypher follow-up to attach graph facts (skills, location, certifications) to the candidate keys. This is the hybrid pattern detailed in Section 7.4.
3.5 Full-text path
Prompt: "Who has PMP certification or project management experience?" combines an exact token ("PMP") with a fuzzy phrase. search_graph wraps public.search_graph_nodes() over the tsvector + pg_trgm indexes, strips honorifics, retries with progressively shorter terms, and verifies name tokens — keyword and fuzzy matching without leaving PostgreSQL.
3.6 CV generation and RFP matching
•	CV generation. The triage agent routes "generate a CV for …" to the CV agent, which calls list_cv_templates then generate_employee_cv; the backend returns a download link. No graph query language is exposed to the user.
•	RFP / tender matching. An uploaded RFP is parsed by the Document Extraction agent into a roles table (skills, certifications, locations, languages). The Query agent then matches per role: vector_search on the role's requirements, with a schema-driven Cypher fallback when graph matches are sparse, producing one candidate table per role. The agent refuses to match until actual requirements are present (uploaded document or extracted roles in history).
All six use cases run against the one PostgreSQL instance described in Section 1, through the MCP tool layer, behind Entra authentication.
4. Natural language to Cypher
The pipeline is a schema-grounded agent loop, not a template engine or a fine-tuned NL2Cypher model:
User sentence
   |
   v
Triage Agent --(intent: talent search)--> handoff_to_query_agent
   |
   v
Query Agent
   1. get_graph_schema()           -> labels, edges, properties, enum samples
   2. (optional) vector_search()   -> semantic candidate set
   3. query_using_sql_cypher(...)  -> schema-validated Cypher via PGAgeHelper
   |
   v
PostgreSQL + Apache AGE  ->  agtype rows  ->  parsed  ->  table/chart in UI

4.1 Live schema discovery
The agent contract requires the live graph as the source of truth: "Do not assume graph labels, edge types, node properties, edge properties, enum values, or display columns from static knowledge."
Each run begins with get_graph_schema(graph=talent_udp_dbx), returning 25 nodes, 37 edges, 0 enum-like properties. The model writes Cypher using only labels and properties present in that result (Employee, HAS_SKILL, s.name, ResourceRequest.status_nm, IN_PRACTICE, IN_REGION). When the UDP model adds labels (ResourceRequest, Allocation, Practice), they become queryable on the next schema fetch with no prompt change or retraining.
Schema is fetched once per conversation and cached; it refreshes only on explicit request, a graph change, or a query failure implicating a missing label/property. Cached schema is why the aggregation executions complete in 443 ms / 1416 ms without a discovery round-trip.
4.2 AGE dialect constraints
AGE Cypher differs from Neo4j Cypher. The agent instructions enforce these constraints so generated queries execute on AGE:
•	No toDate(), date(), datetime, duration, toString, toLower, split — ISO dates compared as string literals.
•	No SQL casts (::date, ::int) inside the Cypher block.
•	String matching uses regex =~ '(?i).*text.*', not CONTAINS / STARTS WITH.
•	List literals use IN ['a','b'], not IN ('a','b').
•	LIMIT stays inside the $$ ... $$ block; aggregates are defined in a WITH before use in RETURN/ORDER BY.
On a database error or implausible empty result, the agent reads the error text, corrects literal typing once, and retries.
4.3 Result typing
AGE returns the agtype type. PGAgeHelper sets search_path = ag_catalog, "$user", public before each call and parses agtype to native Python ("text"→str, 12.5::numeric→float, ["Employee"]→label string). The UI renders rows as a table and, where applicable, a chart from the same row payload.
4.4 Agent loop vs. template NL2Cypher
Property	Template / fine-tuned NL2Cypher	Schema-grounded agent
Schema drift	Requires retraining/retemplating	New labels picked up on next get_graph_schema
Multi-step (vector → graph)	Hard to express	Native: vector_search then Cypher
Dialect correctness	Often emits Neo4j syntax	Constraints enforce AGE dialect
Explainability	Opaque	Run Log: handoff, schema, Cypher, row counts, timings
Failure recovery	Returns wrong/empty	Reads error, fixes literal types, retries

5. Comparison with a Neo4j-native stack
The query language is the same family (MATCH ... WHERE ... RETURN). The differences are in the engine topology, the ANN index, and the platform model.
5.1 Neo4j vector search
From the Neo4j Vector Index and Search guide:
•	Vector indexes use HNSW (Hierarchical Navigable Small World) for ANN over embeddings on nodes and relationships.
•	Index config: vector.dimensions and vector.similarity_function (cosine or euclidean).
•	The GenAI plugin generates embeddings in-database via ai.text.embed(...) against OpenAI, Azure OpenAI, Vertex AI, Bedrock.
•	Cypher 25 provides SEARCH ... IN (VECTOR INDEX ...) SCORE score, plus vector.similarity.cosine() for exact pre-filtered search.
•	Hybrid search (full-text + vector; lexical + semantic + structural) fuses ranked lists from multiple indexes at the query/application layer.
5.2 Engine and index comparison
Dimension	Neo4j	TalentIQ (Azure Postgres + AGE + pgvector)
ANN algorithm	HNSW (index resident in memory)	DiskANN (pg_diskann, SSD-resident); HNSW also available
Memory scaling	Index RAM scales with corpus size	SSD-resident; RAM independent of corpus size
Similarity functions	cosine, euclidean	cosine (<=>), L2, inner product
Hybrid search	Fused across Neo4j indexes at query/app layer	Vector → Cypher → FTS → relational in one SQL statement
Aggregation / BI	Cypher; Neo4j connector ecosystem	Cypher or SQL over matviews; standard BI, pg_dump, Azure Monitor
Databricks ingestion	neo4j-admin import / custom loaders	JDBC / COPY from Databricks Gold tables

Two technical consequences:
•	HNSW vs. DiskANN. HNSW holds its graph layers in memory, so index RAM grows with the embedding corpus. DiskANN keeps the index on SSD, so memory is decoupled from corpus size. For large embedding sets this changes instance sizing and the cost curve.
•	Single-statement hybrid. TalentIQ composes vector candidate selection, Cypher enrichment, full-text, and relational aggregation in one SQL transaction against one store. Neo4j composes vector and full-text results across separate indexes and fuses them in the query or application layer.
5.3 Managed platform model
Both options have a managed offering. Neo4j AuraDB provides a 99.95% uptime SLA, automated upgrades/patches, multi-zone HA, automated backups with point-in-time recovery, and read replicas ("Secondaries" on Business Critical and above), on Azure, AWS, and GCP. Azure Database for PostgreSQL Flexible Server provides zone-redundant HA, read replicas, automated backups, and PITR as a first-party Azure service.
The difference is platform placement, relevant because TalentIQ is Azure-native with Microsoft Entra identity and VNet integration throughout:
Capability	Azure Database for PostgreSQL Flexible Server	Neo4j AuraDB
Service type	First-party Azure PaaS	Neo4j SaaS (third-party on Azure)
HA / read replicas / backups + PITR	Native, in-subscription	Native, in Neo4j's service
Identity	Microsoft Entra ID native	Neo4j-managed auth / SSO
Network	In-subscription VNet + private endpoints	Separate tenancy; VPC isolation at the Virtual Dedicated Cloud tier
Governance / billing	Azure Monitor, Policy, single Azure bill/SLA	Separate vendor portal, bill, SLA
Paradigms in the one service	Graph + vector + full-text + relational	Graph; vector store and warehouse are separate services

•	A single Azure-managed instance covers all four paradigms, with HA, read replicas, backups, and PITR applied to the same instance that holds the graph, DiskANN vectors, tsvector indexes, and relational tables.
•	That instance sits inside the Azure governance boundary (Entra, VNet/private endpoints, Monitor, Policy, single bill) alongside the Container Apps backend and frontend. AuraDB runs in a separate tenancy; keeping a graph engine in-VNet without AuraDB means self-managing Neo4j on VMs/AKS, which reintroduces HA, patching, and backup operations.
5.4 Databricks ingestion
The UDP graph is materialized from Databricks Gold tables. Loading Postgres from Databricks uses a JDBC/COPY path. Neo4j ingestion at this scale uses neo4j-admin import or custom batch loaders outside the lakehouse.
 
Figure 5 — UDP table-to-graph mapping: gold Delta tables to v2 property-graph nodes and edges.
6. Comparison with OntoBricks / OWL
OntoBricks designs an OWL ontology, maps Unity Catalog tables via R2RML, materializes triples into a Delta + Lakebase triple store, runs OWL 2 RL / SWRL / SHACL reasoning, and exposes an auto-generated GraphQL API + MCP. It targets formal knowledge-graph and digital-twin workloads. TalentIQ does not use an OWL/SPARQL/triple-store paradigm; the decision is recorded in ADR-001.
Dimension	OntoBricks (OWL + R2RML + triple store + reasoner)	TalentIQ (Postgres + AGE + pgvector + tsvector)
Data model	RDF triples + OWL TBox	Property graph + embeddings + relational
Query surface	GraphQL (auto-generated) / SPARQL	Cypher + SQL + vector in one transaction
Similarity match	Inference yields class membership (boolean)	Vector cosine yields a ranked score
Aggregations	SPARQL CONSTRUCT / GraphQL	Cypher aggregation or SQL over matviews
Reasoning	OWL 2 RL / SWRL / SHACL	Not used
Stores to operate	Delta triple store + Lakebase Postgres + UC volume	One Postgres instance
Ingestion	R2RML mapping + triple materialization + sync pipeline	Direct node/edge/embedding load from Databricks

Technical points specific to TalentIQ's workload:
1.	Ranked similarity vs. boolean entailment. "Azure data engineer with Databricks and Python" and "candidates similar to this resource request" are nearest-neighbor problems that return a ranked, scored list, including partial matches. An OWL reasoner returns class membership, not a similarity score. The image.png run reflects this: the agent matched on Azure plus Databricks/Python skills because the graph exposes no "data engineer" class flag.
2.	Lookups, not subsumption. EQF/MECES levels are a 4-column lookup table. Skill adjacency is cosine similarity or explicit Skill→Skill edges. Neither requires OWL class subsumption or owl:equivalentClass.
3.	Store count. OntoBricks v0.4.0 requires a Delta triple store, a Lakebase Postgres graph engine, and a UC volume, plus a reasoning/sync pipeline. TalentIQ holds the graph in one Postgres instance with a direct load; the schema lives in AGE rather than as OWL TBox axioms requiring sync.
4.	Aggregation shape. The dashboard prompts are GROUP BY workloads (443 ms, 1416 ms) feeding standard charts. The same shapes in SPARQL over a triple store surfaced through GraphQL add layers without a performance benefit for this workload.
OWL/SPARQL becomes the appropriate choice when the requirements include publishing a public vocabulary via standard URIs, provenance-traceable entailment, live federation across multiple triple stores (ESCO/FIBO/schema.org), or automated subsumption reasoning over large axiom sets. None of these appear in the current user stories.
7. One PostgreSQL instance, four query paradigms
PostgreSQL hosts four query paradigms, each backed by a dedicated index, composable in one SQL statement.
Layer	Mechanism	Index	Query type
Graph	Apache AGE (Cypher)	label/property	"Who has skill X and Y in location Z?"; N-hop traversal
Vector	pgvector + DiskANN	USING diskann	"Find profiles similar to this resume / request"
Full-text	tsvector + GIN + pg_trgm	GIN / trigram	free-text CV search, fuzzy name matching
Relational	tables / matviews	B-tree	aggregations, EQF/MECES lookups, audit, embedding storage

7.1 Graph (Apache AGE)
AGE stores a property graph in Postgres and runs Cypher via ag_catalog.cypher(graph, $$ ... $$):
•	Multi-criteria filtering — Employee joined to two Skill nodes and a Location in one pattern.
•	Aggregation — count by status_nm; count by practice × region.
•	Hierarchy/lifecycle traversal — REPORTS_TO, IN_PRACTICE/PARENT_PRACTICE, ResourceRequest → Assignment → Allocation → TimePeriod.
7.2 Vector (DiskANN)
Embeddings live in sidecar tables (v2_employee_embeddings, v2_resource_request_embeddings, …) indexed with DiskANN:
SELECT e.employee_key, e.skills_text_preview,
       1 - (e.skills_embedding <=> query.query_vector) AS similarity
FROM v2_employee_embeddings e CROSS JOIN query
WHERE e.skills_embedding IS NOT NULL
ORDER BY e.skills_embedding <=> query.query_vector   -- DiskANN scan
LIMIT 25;

DiskANN keeps the index on SSD, so memory does not scale with corpus size, and it runs in the same instance as the graph. It returns a ranked candidate list ordered by cosine distance.
7.3 Full-text
tsvector + GIN handles free-text CV/resume search; pg_trgm handles fuzzy name matching. The search_graph MCP tool wraps public.search_graph_nodes(), retries with progressively shorter terms, and verifies name tokens.
7.4 Hybrid in one transaction
The canonical flow is vector-then-graph:
WITH vector_candidates AS (
  SELECT e.employee_key,
         1 - (e.skills_embedding <=> q.query_vector) AS similarity
  FROM v2_employee_embeddings e CROSS JOIN query q
  ORDER BY e.skills_embedding <=> q.query_vector
  LIMIT 25                          -- (1) DiskANN: semantic candidates
)
-- (2) Cypher enriches the candidate keys with graph facts
SELECT * FROM ag_catalog.cypher('talent_udp_...', $$
  MATCH (e:Employee)-[:HAS_SKILL]->(s:Skill)
  WHERE e.employee_key IN ['...','...']
  RETURN e, collect(s.name)
$$) AS (...);

DiskANN narrows the corpus to semantically relevant candidates; Cypher attaches the relationships that explain each match; full-text and SQL aggregations apply on the same data. All four run against one instance, one security boundary, one backup, one connection pool.
8. Summary
•	Architecture: Databricks/UDP ingests gold Delta tables into one Azure PostgreSQL Flexible Server (Apache AGE + pgvector/DiskANN + tsvector + relational); an MCP tool layer, an Entra-authenticated FastAPI backend, and a demo UI run as VNet-integrated Container Apps; identity is Microsoft Entra end to end, with passwordless MSI to the database over a Private Endpoint.
•	Scale: ~14.7M vertices and ~50M edges (12.3M Allocation, 1.15M Assignment, 1.7M HAS_SKILL) plus 160k+ DiskANN-indexed employee vectors, all in one managed instance.
•	Query routing: an agent selects Cypher, vector (DiskANN), or full-text per request, and covers talent search, similarity, aggregation dashboards, full-text lookup, CV generation, and RFP matching — each step visible in the Run Log.
•	NL → Cypher: a schema-grounded agent discovers the live AGE schema, generates AGE-dialect Cypher under explicit constraints, executes via ag_catalog.cypher, and retries once on error.
•	Neo4j: same Cypher family. Differences are HNSW (RAM-resident index) vs. DiskANN (SSD-resident index), hybrid composition in one SQL statement vs. fusion across separate indexes, and platform placement — Neo4j AuraDB is a third-party SaaS; Azure Database for PostgreSQL Flexible Server is a first-party Azure PaaS covering all four paradigms in one instance.
•	OntoBricks/OWL: targets formal ontologies, R2RML triple materialization, and OWL/SWRL/SHACL reasoning. TalentIQ's workload is ranked, multi-paradigm search with no entailment requirement, so it uses scored vector similarity and avoids the triple-store + Lakebase + volume + reasoner topology.
•	PostgreSQL: AGE (Cypher) for traversal, pgvector + DiskANN for similarity, tsvector/pg_trgm for full-text, SQL for aggregations and lookups — composable in one transaction inside one governance boundary.
9. To Do / Open items
Planned work items beyond the current build:
#	Item	Scope
1	Incremental updates — move ingestion and embedding from full reload to change-data-capture / delta upserts so the graph and vectors refresh without a full rebuild.	Pipeline
2	Employee identity resolution — finalize the canonical employee key and cross-source matching (Workday personnel number / core ID, BenchIQ employee ID, PSA pern_id/email) to deduplicate people across UDP sources.	Data model
3	Data source fields finalization — lock the source field set used for ingestion and for embedding text (which columns feed each *_embedding corpus).	Pipeline / embeddings
4	API access to the database — expose a governed query API surface (beyond the MCP tools) for programmatic/structured access.	Backend
5	Row-level security — apply PostgreSQL RLS policies so query results are scoped to the caller's Entra identity / group membership.	Security

