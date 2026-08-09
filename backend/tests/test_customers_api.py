import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_get_customers():
    response = client.get("/api/customers")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data
    
    # We should have some customers derived
    assert data["total"] > 0
    first_customer = data["items"][0]
    assert "client_name" in first_customer
    assert "active_orders" in first_customer
    assert "loading_cities" in first_customer
    assert "delivery_cities" in first_customer

def test_get_customers_search():
    # Attempt to search a known customer if possible, or just test the filter works without error
    response = client.get("/api/customers?search=Everest")
    assert response.status_code == 200
