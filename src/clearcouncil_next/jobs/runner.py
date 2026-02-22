"""Background worker loop for autonomous queue processing."""

from __future__ import annotations

import json
import logging
import time

from clearcouncil_next.core.config import get_settings
from clearcouncil_next.core.database import init_db
from clearcouncil_next.jobs.queue import claim_next_queued_job, mark_job_completed, mark_job_failed
from clearcouncil_next.jobs.tasks import JOB_HANDLERS


logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")
logger = logging.getLogger("clearcouncil_next.worker")


def run_worker_forever() -> None:
    settings = get_settings()
    init_db()

    logger.info("Worker started", extra={"poll_seconds": settings.worker_poll_seconds})
    while True:
        job = claim_next_queued_job()
        if job is None:
            time.sleep(settings.worker_poll_seconds)
            continue

        handler = JOB_HANDLERS.get(job.job_type)
        if handler is None:
            mark_job_failed(job.id, f"No job handler registered for type '{job.job_type}'")
            continue

        try:
            payload = json.loads(job.payload_json)
            handler(job.council_key, payload)
            mark_job_completed(job.id)
            logger.info("Job completed", extra={"job_id": job.id, "job_type": job.job_type})
        except Exception as exc:  # noqa: BLE001
            mark_job_failed(job.id, str(exc))
            logger.exception("Job failed", extra={"job_id": job.id})


if __name__ == "__main__":
    run_worker_forever()
