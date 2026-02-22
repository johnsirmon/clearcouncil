"""Pydantic API contracts for the next-generation service."""

from datetime import datetime
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    service: str
    status: str
    timestamp_utc: datetime


class JobCreateRequest(BaseModel):
    council_key: str = Field(min_length=2, max_length=120)
    job_type: str = Field(default="ingest", min_length=2, max_length=120)
    payload: Dict[str, Any] = Field(default_factory=dict)


class JobResponse(BaseModel):
    id: int
    council_key: str
    job_type: str
    status: str
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    error_message: Optional[str]
