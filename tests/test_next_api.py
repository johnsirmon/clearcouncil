"""Smoke tests for the next-generation API surface."""

from fastapi.testclient import TestClient

import clearcouncil_next.api.app as next_app

from clearcouncil_next.api.app import app


def test_health_endpoint_returns_ok() -> None:
    client = TestClient(app)
    response = client.get("/health")

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"


def test_mcp_tools_endpoint_returns_catalog() -> None:
    client = TestClient(app)
    response = client.get("/v1/mcp/tools")

    assert response.status_code == 200
    body = response.json()
    assert "tools" in body
    assert isinstance(body["tools"], list)


def test_create_job_returns_identifier() -> None:
    client = TestClient(app)
    response = client.post(
        "/v1/jobs",
        json={
            "council_key": "york_county_sc",
            "job_type": "ingest",
            "payload": {"trigger": "pytest"},
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["id"] > 0
    assert body["status"] == "queued"


def test_source_audit_returns_facts_bias_and_translation() -> None:
    client = TestClient(app)
    response = client.post(
        "/v1/audit/source",
        json={
            "source_name": "Local Daily",
            "source_url": "https://example.org/article-1",
            "article_text": (
                "On February 14, 2026, the county board voted 5-2 to approve a $1.2 million contract "
                "for road resurfacing. The project will begin in April 2026 according to the meeting minutes. "
                "Insiders say the process was obviously rigged and a disgraceful decision. "
                "The procurement office reported that three bids were submitted before the deadline."
            ),
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["source_name"] == "Local Daily"
    assert isinstance(body["factual_claims"], list)
    assert len(body["factual_claims"]) >= 1
    assert isinstance(body["bias_signals"], list)
    assert body["bias_score"] >= 0
    assert "Objective summary" in body["objective_translation"]


def test_source_audit_requires_article_text() -> None:
    client = TestClient(app)
    response = client.post(
        "/v1/audit/source",
        json={
            "source_name": "Local Daily",
            "article_text": "short",
        },
    )

    assert response.status_code == 422


def test_source_url_audit_returns_analysis(monkeypatch) -> None:
    client = TestClient(app)

    def _fake_fetch(_: str) -> str:
        return (
            "On March 2, 2026, the city council voted 4-1 to approve a $800,000 sidewalk contract. "
            "The public works report listed two qualified bidders and a 90-day completion timeline. "
            "Sources say this was clearly a cover-up and a disgraceful process, according to insiders."
        )

    monkeypatch.setattr(next_app, "fetch_article_text", _fake_fetch)

    response = client.post(
        "/v1/audit/source-url",
        json={
            "source_name": "Metro Ledger",
            "source_url": "https://example.org/news-item",
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["source_url"] == "https://example.org/news-item"
    assert body["bias_score"] >= 0
    assert isinstance(body["factual_claims"], list)


def test_source_url_audit_handles_short_content(monkeypatch) -> None:
    client = TestClient(app)

    def _fake_fetch(_: str) -> str:
        raise ValueError("Fetched content is too short for reliable auditing")

    monkeypatch.setattr(next_app, "fetch_article_text", _fake_fetch)

    response = client.post(
        "/v1/audit/source-url",
        json={
            "source_name": "Metro Ledger",
            "source_url": "https://example.org/news-item",
        },
    )

    assert response.status_code == 400
