import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200

def test_list_orders():
    response = client.get("/api/orders")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data
    assert "page" in data
    assert len(data["items"]) > 0

def test_list_orders_pagination():
    response = client.get("/api/orders?page_size=2")
    assert response.status_code == 200
    data = response.json()
    assert data["page_size"] == 2
    assert len(data["items"]) <= 2

def test_list_orders_filters():
    # Test a search that matches something like "OR601"
    response = client.get("/api/orders?search=OR601")
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) == 1
    assert data["items"][0]["order_number"] == "OR601"

    # Test status filter
    response = client.get("/api/orders?status=pending_approval")
    assert response.status_code == 200
    assert len(response.json()["items"]) > 0

def test_get_order():
    # First get an order ID to test with
    orders_response = client.get("/api/orders")
    first_order_id = orders_response.json()["items"][0]["id"]

    response = client.get(f"/api/orders/{first_order_id}")
    assert response.status_code == 200
    assert response.json()["id"] == first_order_id

def test_get_order_not_found():
    response = client.get("/api/orders/invalid-uuid-format")
    assert response.status_code == 404
    assert response.json()["error"]["code"] == "RECORD_NOT_FOUND"

def test_get_order_tasks():
    # Get a valid order ID
    orders_response = client.get("/api/orders")
    first_order_id = orders_response.json()["items"][0]["id"]

    response = client.get(f"/api/orders/{first_order_id}/tasks")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
