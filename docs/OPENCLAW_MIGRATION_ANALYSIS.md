# OpenClaw Migration Analysis for ClearCouncil

**Date:** February 2026  
**Scope:** Architectural analysis and migration recommendation  
**Reference:** [OpenClaw Documentation](https://docs.openclaw.ai/)

---

## 1. Current Architecture Summary

### Entry Points

| File | Role |
|------|------|
| `clearcouncil.py` | CLI wrapper → `src/clearcouncil/cli/main.py` |
| `clearcouncil_web.py` | Flask web server launcher |
| `simple_web_server.py` | Standalone transparency dashboard (port 5001) |
| `clearcouncil_chat.py` | Flask chat interface using GitHub Models API (port 5002) |
| `src/clearcouncil_next/api/app.py` | FastAPI next-gen service with MCP-style tools |

The system has **two parallel architectures** in flight: the production v1 (sync CLI + Flask) and a next-gen v2 (FastAPI + async job queue) that is partially implemented.

### Orchestration Logic

The primary orchestration lives in `src/clearcouncil/analysis/voting_analyzer.py` and `analysis/batch_processor.py`:

1. **Time range parsing** → resolve natural language ("last year") to date bounds  
2. **Document discovery** → scan local PDFs matching council config patterns  
3. **Format detection** → identify IQM2, Legistar, standard minutes, or unknown  
4. **Extraction pipeline** → regex-first, AI fallback for unstructured documents  
5. **Representative tracking** → fuzzy name matching, canonical name resolution  
6. **Visualization** → Plotly/matplotlib chart generation

The "agent" component is narrow and single-purpose: `parsers/agentic_minutes_parser.py` makes one-shot LLM calls (GitHub Models API or OpenAI) only when regex extraction fails for unknown document formats. There is no multi-step agent loop or tool-routing at runtime in v1.

### State Handling

| Layer | Mechanism |
|-------|-----------|
| Session state | Flask `session` object stores `council_id` per HTTP session |
| Chat context | In-memory dict in `clearcouncil_chat.py` holds `current_council` |
| Voting records | SQLite (thread-safe with exponential-backoff locking) |
| Vector index | FAISS index cached in `_store` global, persisted to disk with date-stamped filenames |
| Representative state | Built in memory during `VotingAnalyzer` run; not persisted between CLI invocations |

### Tool Integrations

ClearCouncil already defines MCP-style tools in `src/clearcouncil_next/mcp/tools.py`:

- `documents.search` — semantic retrieval via FAISS  
- `votes.query` — structured voting record lookup  
- `source.audit_article` / `source.audit_url` — bias/fact auditing  
- `jobs.start` — enqueue ingest/reindex/evaluate jobs

These are exposed as a REST endpoint (`GET /v1/mcp/tools`) in the FastAPI app but not yet wired to a live agent runtime.

### Async Patterns

- **v1 (production):** Synchronous throughout. Parallelism is `ThreadPoolExecutor` for PDF batch downloads. `aiohttp` is imported in `batch_processor.py` but the call sites are sync.  
- **v2 (next-gen):** FastAPI with `asynccontextmanager` lifespan, async job queue polling, but handlers remain largely synchronous stubs.

---

## 2. Where Custom Agent Patterns Exist

### a. Agentic Minutes Parser (`parsers/agentic_minutes_parser.py`)

A multi-strategy extraction pipeline:

1. Regex patterns for IQM2, Legistar, standard minutes  
2. On failure → one-shot LLM call with structured chain-of-thought prompt  
3. JSON response parsed back to `VotingRecord` dataclasses

This is the only location where an LLM is invoked programmatically (outside the chat interface). It is a **single-turn inference call**, not a loop.

### b. Chat Interface (`clearcouncil_chat.py`)

A Flask endpoint that:

1. Resolves the active council from session  
2. Runs a vector search to inject document chunks into context  
3. Constructs a system prompt with council metadata + search hits + time-range awareness  
4. Issues a single chat-completion call to GitHub Models API  
5. Returns the streamed response

This is **context-augmented single-shot inference**, not an agent loop with tool use.

### c. Source Audit (`clearcouncil_next/analysis/source_audit.py`)

Calls an LLM to extract factual claims, bias signals, and an "objective translation" from article text. Single-turn, no iteration.

### d. Job Queue (`clearcouncil_next/jobs/`)

A lightweight job dispatcher: `JOB_HANDLERS` dict maps `job_type` → Python function. Worker polls the queue, dispatches, and updates status. This is a simple task queue, not an agent runtime — there is no decision-making, tool selection, or iterative planning.

**Summary:** ClearCouncil has no multi-turn agent loop, no dynamic tool selection, no memory system beyond SQLite/FAISS, and no autonomous planning. The "agentic" label on the minutes parser refers to its use of LLM inference, not to a true agent architecture.

---

## 3. OpenClaw Architecture and Capabilities

OpenClaw is a **self-hosted messaging gateway and agent runtime** built around the Pi Agent Framework. Its four-layer architecture:

| Layer | Function |
|-------|----------|
| **Gateway** | Routes and multiplexes traffic across WhatsApp, Telegram, Discord, iMessage |
| **Integration** | Normalizes channel-specific message formats into a unified envelope |
| **Execution** | Lane Queues prevent deadlocks; manages tool invocation ordering and concurrency |
| **Intelligence** | Pi agent core: skills (tools), short/long-term memory (Markdown files), heartbeat loop |

Key differentiators:

- **Skills-as-Markdown:** Tools are declared in YAML/Markdown, installable per agent session  
- **Persistent heartbeat loop:** Agent operates proactively, not just on-demand  
- **Human-readable memory:** Long-term state stored as plain `.md` files  
- **Multi-channel isolation:** Separate memory scopes per platform/workspace  
- **Runtime:** Node.js / TypeScript (Pi agent core is `@mariozechner/pi-agent-core`)

---

## 4. Comparison: ClearCouncil vs. OpenClaw

| Dimension | ClearCouncil Current | OpenClaw |
|-----------|---------------------|---------|
| **Primary purpose** | Document ingestion, structured data extraction, civic transparency | Messaging gateway with persistent AI agents across chat platforms |
| **Agent model** | Single-turn LLM calls; no loop | Continuous heartbeat loop; iterative planning |
| **Tool dispatch** | MCP schema defined but not executed at runtime | Skills registered and invoked dynamically by agent |
| **Memory** | SQLite + FAISS; no LLM-accessible memory layer | MEMORY.md per agent; transcript JSONL logs |
| **Channels** | Web browser, CLI, REST API | WhatsApp, Telegram, Discord, iMessage |
| **Language** | Python | Node.js / TypeScript |
| **State persistence** | DB-backed; explicit | File-backed; implicit (agent writes its own memory) |
| **Observability** | `clearcouncil.log`, SQLite audit trail | JSONL transcripts, per-session files |
| **Deployment target** | Government transparency portal | Personal/enterprise chat assistant |

### Where OpenClaw Adds Value (in general)

- Multi-channel routing for conversational agents  
- Standardized skill registry with community sharing (ClawHub)  
- Autonomous long-running workflows across chat sessions  
- Privacy-preserving local memory management

### Where OpenClaw Does Not Apply to ClearCouncil

- ClearCouncil's core value is **PDF ingestion → structured data extraction → web dashboard**. None of this maps to OpenClaw's messaging gateway model.  
- ClearCouncil serves **browser-based users** and **CLI operators**, not messaging app users.  
- The LLM use in ClearCouncil is narrow (one-shot fallback parsing; chat RAG). It does not require a persistent agent loop.  
- OpenClaw is Node.js-first; ClearCouncil is Python-first. Mixing runtimes would add operational complexity with no architectural gain.  
- ClearCouncil already defines MCP tools and has a FastAPI layer. It is not missing an orchestration primitive.

---

## 5. Concrete Benefits of Migrating — Assessed Honestly

| Claimed Benefit | Applies to ClearCouncil? | Assessment |
|-----------------|--------------------------|------------|
| Reduced boilerplate | No | The "boilerplate" in ClearCouncil is PDF parsing and regex patterns, not agent scaffolding. OpenClaw doesn't help here. |
| Standardized agent runtime | Marginal | Only useful if ClearCouncil adds multi-turn agentic workflows. Current use case doesn't require it. |
| Multi-channel delivery | No | No requirement to deliver answers via WhatsApp or Telegram. |
| Observability | No | ClearCouncil already has file/DB logging. The JSONL transcript format adds no value over SQLite audit rows. |
| Scaling | No | OpenClaw scales agents across messaging sessions. ClearCouncil's scaling challenge is parallel PDF processing, which is a batch compute problem, not an agent routing problem. |
| Extensibility | Marginal | Skills-as-Markdown is elegant but ClearCouncil's MCP tool schema in `clearcouncil_next` already provides equivalent extensibility in Python. |
| Security | No benefit | OpenClaw's sandboxing targets agent-initiated actions. ClearCouncil's threat model is API key protection and read-only civic data—already handled. |

---

## 6. Migration Risks

| Risk | Severity |
|------|----------|
| **Language mismatch (Python → Node.js)** | High — all PDF processing, FAISS, pandas, PyMuPDF, and langchain integrations are Python-native. Rewriting in Node.js is a full rewrite of the data pipeline. |
| **Loss of domain-specific parsers** | High — IQM2, Legistar, and standard-minutes parsers encode years of reverse-engineering effort. These have no equivalent in any agent framework. |
| **Ecosystem immaturity** | Medium — OpenClaw is relatively new. Its community (ClawHub) and tooling are not yet proven for civic data workloads. |
| **Deployment complexity** | Medium — introducing a Node.js gateway alongside a Python backend adds a new runtime dependency, process supervisor configuration, and cross-process API contracts. |
| **Breaking changes to web UI** | High — the Flask web dashboard is the primary user-facing interface. Routing it through an OpenClaw gateway would require significant re-architecture for no UX benefit. |
| **No migration path for FAISS/SQLite** | Medium — OpenClaw's memory model (Markdown files) is incompatible with ClearCouncil's vector index and relational voting database. |

---

## 7. Migration Scope Classification

If a migration were attempted, the scope would be a **full architectural rewrite**:

- The entire Python data pipeline (PDF download → text extraction → format detection → regex/LLM parsing → voting record normalization → FAISS indexing → SQLite storage) has no equivalent in OpenClaw's skills model.  
- The Flask web dashboard, interactive Plotly charts, and REST API would all need to be rebuilt or wrapped behind an OpenClaw gateway with no user-visible improvement.  
- The existing MCP tool definitions in `clearcouncil_next` would need to be re-implemented as OpenClaw "skills."  
- An "adapter layer" approach would leave all Python components in place and add OpenClaw only as a messaging front-end — which is architecturally coherent but answers a question ClearCouncil doesn't have (how do I reach users on Telegram?).

---

## 8. Recommendation: Keep Current Stack

**Do not migrate to OpenClaw.** The reasoning is straightforward:

1. **Wrong tool for the job.** OpenClaw solves the problem of deploying persistent AI agents across messaging platforms. ClearCouncil's problem is structured data extraction from government PDFs and presenting that data through a web UI. These are categorically different problems.

2. **No functional gap.** Every capability OpenClaw provides (tool dispatch, memory, observability) either already exists in ClearCouncil (SQLite, FAISS, logging) or can be added to the existing Python stack at far lower cost (e.g., `langgraph` or `pydantic-ai` for multi-turn agent loops if ever needed).

3. **The next-gen architecture (`clearcouncil_next`) is already on the right path.** It has MCP tool definitions, a FastAPI async API, a job queue, and source-auditing capabilities. Completing this layer is a much better investment than introducing a foreign runtime.

4. **Migration cost is disproportionate.** A full rewrite would take weeks or months and would produce a system with equivalent or worse functionality, higher operational complexity, and a Node.js runtime dependency that the existing team is not equipped to maintain.

### What to Do Instead

| Incremental improvement | Cost | Benefit |
|------------------------|------|---------|
| Finish `clearcouncil_next` FastAPI layer and deprecate Flask | Low | Single, clean async API surface |
| Wire the MCP tools to actual handlers in `clearcouncil_next/jobs/` | Low | True tool-call API compatible with any MCP-capable LLM client |
| Replace single-shot chat RAG with a `langgraph` or `pydantic-ai` multi-turn loop | Medium | True agentic behavior for the chat interface without changing the data pipeline |
| Add structured logging (e.g., `structlog`) with JSON output | Low | Production-grade observability without adding a new runtime |
| If messaging channels are genuinely needed (Telegram bot, etc.), add `python-telegram-bot` or equivalent | Low | Delivers the one concrete OpenClaw benefit that might be relevant, in Python |

---

## Summary

| Question | Answer |
|----------|--------|
| Current architecture style | Sync CLI + Flask web + thread pool; next-gen FastAPI stub |
| Where agent patterns exist | Single-turn LLM fallback in minutes parser; RAG chat |
| OpenClaw fit | Poor — messaging gateway, Node.js runtime, wrong abstraction level |
| Migration scope | Full architectural rewrite |
| Recommendation | **Keep current stack. Complete `clearcouncil_next`. Do not adopt OpenClaw.** |
