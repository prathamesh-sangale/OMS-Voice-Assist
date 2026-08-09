from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_agent_api_show_pending_orders():
    response = client.post("/api/agent/command", json={"text": "show pending orders"})
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["intent"] == "LIST_ORDERS"
    assert data["data"] is not None

def test_agent_api_show_specific_order():
    response = client.post("/api/agent/command", json={"text": "show order OR601"})
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["intent"] == "GET_ORDER"
    assert data["data"]["order_number"] == "OR601"

def test_agent_api_unsupported_write():
    response = client.post("/api/agent/command", json={"text": "delete order OR601"})
    assert response.status_code == 200 # App logic handles it smoothly
    data = response.json()
    assert data["status"] == "unsupported"
    assert data["intent"] == "UNSUPPORTED"

def test_agent_api_clarification_needed():
    response = client.post("/api/agent/command", json={"text": "show the order"})
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "needs_clarification"
    assert data["requires_clarification"] is True

def test_agent_api_not_found():
    response = client.post("/api/agent/command", json={"text": "show order OR999999"})
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "error"
    assert "could not find" in data["message"].lower()
