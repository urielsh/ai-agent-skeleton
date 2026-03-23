"""Compute endpoint tests."""

import pytest


@pytest.mark.asyncio
async def test_compute_missing_fields_returns_400(test_client):
    # Create session (empty draft)
    create_resp = await test_client.post("/api/sessions")
    session_id = create_resp.json()["session_id"]

    resp = await test_client.post(f"/api/sessions/{session_id}/compute")
    assert resp.status_code == 400
    assert "Missing required fields" in resp.json()["detail"]


@pytest.mark.asyncio
async def test_compute_nonexistent_session(test_client):
    resp = await test_client.post(
        "/api/sessions/00000000-0000-0000-0000-000000000000/compute"
    )
    assert resp.status_code == 404
