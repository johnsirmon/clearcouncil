"""Smoke tests for the next-generation API surface."""

from fastapi.testclient import TestClient

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
