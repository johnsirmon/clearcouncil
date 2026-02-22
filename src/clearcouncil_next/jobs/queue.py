"""Simple database-backed queue primitives for unattended job execution."""

from datetime import datetime
import json
from typing import Optional

from sqlalchemy import select

from clearcouncil_next.core.database import session_scope
from clearcouncil_next.core.models import JobRun, JobStatus


def enqueue_job(council_key: str, job_type: str, payload: dict) -> JobRun:
    with session_scope() as session:
        job = JobRun(
            council_key=council_key,
            job_type=job_type,
            status=JobStatus.queued,
            payload_json=json.dumps(payload, sort_keys=True),
        )
        session.add(job)
        session.flush()
        session.refresh(job)
        return job


def get_job(job_id: int) -> Optional[JobRun]:
    with session_scope() as session:
        return session.get(JobRun, job_id)


def claim_next_queued_job() -> Optional[JobRun]:
    with session_scope() as session:
        stmt = select(JobRun).where(JobRun.status == JobStatus.queued).order_by(JobRun.id.asc()).limit(1)
        job = session.execute(stmt).scalar_one_or_none()
        if job is None:
            return None

        job.status = JobStatus.running
        job.started_at = datetime.utcnow()
        session.add(job)
        session.flush()
        session.refresh(job)
        return job


def mark_job_completed(job_id: int) -> None:
    with session_scope() as session:
        job = session.get(JobRun, job_id)
        if not job:
            return
        job.status = JobStatus.completed
        job.completed_at = datetime.utcnow()
        session.add(job)


def mark_job_failed(job_id: int, error_message: str) -> None:
    with session_scope() as session:
        job = session.get(JobRun, job_id)
        if not job:
            return
        job.status = JobStatus.failed
        job.completed_at = datetime.utcnow()
        job.error_message = error_message
        session.add(job)
