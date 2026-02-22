"""FastAPI application for ClearCouncil Next."""

from contextlib import asynccontextmanager
from datetime import datetime

from fastapi import FastAPI, HTTPException

from clearcouncil_next.core.config import get_settings
from clearcouncil_next.core.database import init_db
from clearcouncil_next.core.schemas import HealthResponse, JobCreateRequest, JobResponse
from clearcouncil_next.jobs.queue import enqueue_job, get_job
from clearcouncil_next.mcp.tools import TOOLS

settings = get_settings()


@asynccontextmanager
async def lifespan(_: FastAPI):
    init_db()
    yield


app = FastAPI(title=settings.app_name, version="0.1.0", lifespan=lifespan)


@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(service=settings.app_name, status="ok", timestamp_utc=datetime.utcnow())


@app.get("/v1/mcp/tools")
def list_mcp_tools() -> dict:
    return {"tools": TOOLS}


@app.post("/v1/jobs", response_model=JobResponse)
def create_job(request: JobCreateRequest) -> JobResponse:
    job = enqueue_job(request.council_key, request.job_type, request.payload)
    return JobResponse(
        id=job.id,
        council_key=job.council_key,
        job_type=job.job_type,
        status=job.status.value,
        started_at=job.started_at,
        completed_at=job.completed_at,
        error_message=job.error_message,
    )


@app.get("/v1/jobs/{job_id}", response_model=JobResponse)
def job_status(job_id: int) -> JobResponse:
    job = get_job(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")

    return JobResponse(
        id=job.id,
        council_key=job.council_key,
        job_type=job.job_type,
        status=job.status.value,
        started_at=job.started_at,
        completed_at=job.completed_at,
        error_message=job.error_message,
    )
