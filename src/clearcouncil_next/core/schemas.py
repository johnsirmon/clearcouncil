"""Pydantic API contracts for the next-generation service."""

from datetime import datetime
from typing import Any, Dict, List, Optional

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


class SourceAuditRequest(BaseModel):
    source_name: Optional[str] = Field(default=None, max_length=200)
    source_url: Optional[str] = Field(default=None, max_length=600)
    article_text: str = Field(min_length=80)


class SourceUrlAuditRequest(BaseModel):
    source_name: Optional[str] = Field(default=None, max_length=200)
    source_url: str = Field(min_length=8, max_length=600)


class BiasSignalResponse(BaseModel):
    category: str
    phrase: str
    sentence: str
    severity: str


class SourceAuditResponse(BaseModel):
    source_name: Optional[str]
    source_url: Optional[str]
    factual_claims: List[str]
    bias_signals: List[BiasSignalResponse]
    bias_score: int
    factual_density: float
    bias_summary: str
    objective_translation: str
    investigation_prompts: List[str]
