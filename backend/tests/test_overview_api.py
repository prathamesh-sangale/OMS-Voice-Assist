import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_get_overview():
    response = client.get("/api/overview")
    assert response.status_code == 200
    data = response.json()
    assert "metrics" in data
    assert "recent_orders" in data
    assert "recent_tasks" in data
    
    metrics = data["metrics"]
    assert "active_orders" in metrics
    assert "pending_orders" in metrics
    assert "completed_orders" in metrics
    assert "needs_revision" in metrics
    assert metrics.get("total_order_value") is None  # Should be null as requested
