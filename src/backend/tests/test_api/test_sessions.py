"""Session CRUD endpoint tests."""

import pytest


@pytest.mark.asyncio
async def test_create_session(test_client):
    resp = await test_client.post("/api/sessions")
    assert resp.status_code == 201
    data = resp.json()
    assert "session_id" in data
    assert data["status"] == "active"


@pytest.mark.asyncio
async def test_get_session(test_client):
    # Create first
    create_resp = await test_client.post("/api/sessions")
    session_id = create_resp.json()["session_id"]

    # Get
    resp = await test_client.get(f"/api/sessions/{session_id}")
    assert resp.status_code == 200
    assert resp.json()["session_id"] == session_id


@pytest.mark.asyncio
async def test_get_nonexistent_session(test_client):
    resp = await test_client.get("/api/sessions/00000000-0000-0000-0000-000000000000")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_delete_session(test_client):
    create_resp = await test_client.post("/api/sessions")
    session_id = create_resp.json()["session_id"]

    resp = await test_client.delete(f"/api/sessions/{session_id}")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ended"
