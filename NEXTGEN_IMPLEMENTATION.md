# ClearCouncil Next: Implementation Start

This document tracks the first implementation slice of the agent-first rewrite.

## What is implemented

- New package namespace: `src/clearcouncil_next/`
- API service (FastAPI): `src/clearcouncil_next/api/app.py`
- Core data model for tenant/council/document/job entities: `src/clearcouncil_next/core/models.py`
- Database bootstrap + sessions: `src/clearcouncil_next/core/database.py`
- Queue primitives backed by DB: `src/clearcouncil_next/jobs/queue.py`
- Worker loop for autonomous processing: `src/clearcouncil_next/jobs/runner.py`
- Placeholder job handlers for ingest/reindex/evaluate: `src/clearcouncil_next/jobs/tasks.py`
- Typed MCP-style tool catalog: `src/clearcouncil_next/mcp/tools.py`
- Local scripts:
  - API: `scripts/run_next_api.py`
  - Worker: `scripts/run_next_worker.py`
- Cloud unattended workflow: `.github/workflows/autonomous-pipeline.yml`
- Local stack compose file: `docker-compose.next.yml`

## Why this matters

- Creates a stable foundation for agent-first interactions and unattended operation.
- Separates legacy runtime from next-gen runtime to allow migration without service disruption.
- Introduces explicit job orchestration contracts that GitHub Actions can trigger without human interaction.

## Local run (initial)

1. Install dependencies:

```bash
pip install -r requirements-next.txt
```

2. Start API:

```bash
set PYTHONPATH=src
python scripts/run_next_api.py
```

3. Start worker in a second shell:

```bash
set PYTHONPATH=src
python scripts/run_next_worker.py
```

4. Queue a job:

```bash
curl -X POST http://localhost:8080/v1/jobs \
  -H "Content-Type: application/json" \
  -d "{\"council_key\":\"york_county_sc\",\"job_type\":\"ingest\",\"payload\":{\"source\":\"manual\"}}"
```

## GitHub unattended mode

The workflow `.github/workflows/autonomous-pipeline.yml` supports:

- Scheduled execution (`cron`) with no user interaction.
- Manual `workflow_dispatch` when needed.
- Queueing jobs to the API endpoint using a self-hosted runner labeled `clearcouncil`.

Required repository secrets:

- `CC_NEXT_API_URL`
- `CC_NEXT_API_TOKEN` (optional if API endpoint is internal and trusted)

## Privacy and PII guardrails

- Secret scanning is enforced in CI with `.github/workflows/security-privacy-scan.yml`.
- `gitleaks` uses `.gitleaks.toml` with a narrow allowlist for template placeholders.
- Next-gen worker log payloads are redacted via `src/clearcouncil_next/core/privacy.py`.
- Job APIs support bearer-token protection via `CC_NEXT_API_TOKEN`.

## Next implementation targets

1. Implement real ingestion handlers with source connectors and provenance persistence.
2. Add tenant-aware authz and API token verification middleware.
3. Add `documents.search` and `votes.query` backed by PostgreSQL + pgvector.
4. Add evaluation pipelines and confidence thresholds for publish mode.
5. Add contract and integration tests for API and worker behavior.
