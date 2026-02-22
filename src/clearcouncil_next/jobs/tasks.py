"""Job handlers for ingestion and maintenance operations."""

from __future__ import annotations

import logging
import time
from typing import Callable, Dict


logger = logging.getLogger(__name__)


def run_ingest_job(council_key: str, payload: dict) -> None:
    """Placeholder for discover/fetch/parse/index pipeline implementation."""
    logger.info("Running ingest job", extra={"council_key": council_key, "payload": payload})
    time.sleep(0.25)


def run_reindex_job(council_key: str, payload: dict) -> None:
    """Placeholder for vector and metadata reindex."""
    logger.info("Running reindex job", extra={"council_key": council_key, "payload": payload})
    time.sleep(0.25)


def run_eval_job(council_key: str, payload: dict) -> None:
    """Placeholder for extraction and grounding evaluation jobs."""
    logger.info("Running eval job", extra={"council_key": council_key, "payload": payload})
    time.sleep(0.25)


JOB_HANDLERS: Dict[str, Callable[[str, dict], None]] = {
    "ingest": run_ingest_job,
    "reindex": run_reindex_job,
    "evaluate": run_eval_job,
}
