"""Health endpoint tests."""

import pytest


@pytest.mark.asyncio
async def test_health_returns_ok(test_client):
    resp = await test_client.get("/api/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] in ("healthy", "degraded")
    assert "database" in data
    assert "redis" in data
