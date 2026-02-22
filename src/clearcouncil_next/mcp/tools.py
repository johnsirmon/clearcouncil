"""Typed MCP-style tool definitions for the ClearCouncil agent plane."""

from typing import Any, Dict, List

TOOLS: List[Dict[str, Any]] = [
    {
        "name": "documents.search",
        "description": "Search source documents and return grounded chunks with citations.",
        "input_schema": {
            "type": "object",
            "properties": {
                "council_key": {"type": "string"},
                "query": {"type": "string"},
                "limit": {"type": "integer", "minimum": 1, "maximum": 100, "default": 10},
            },
            "required": ["council_key", "query"],
        },
    },
    {
        "name": "votes.query",
        "description": "Run a structured voting query with optional date and representative filters.",
        "input_schema": {
            "type": "object",
            "properties": {
                "council_key": {"type": "string"},
                "representative": {"type": "string"},
                "start_date": {"type": "string"},
                "end_date": {"type": "string"},
            },
            "required": ["council_key"],
        },
    },
    {
        "name": "jobs.start",
        "description": "Start an unattended ingest/reindex/evaluate job for a council.",
        "input_schema": {
            "type": "object",
            "properties": {
                "council_key": {"type": "string"},
                "job_type": {"type": "string", "enum": ["ingest", "reindex", "evaluate"]},
                "payload": {"type": "object"},
            },
            "required": ["council_key", "job_type"],
        },
    },
]
