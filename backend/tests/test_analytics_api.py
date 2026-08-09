import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_get_analytics():
    response = client.get("/api/analytics/orders")
    assert response.status_code == 200
    data = response.json()
    assert "business_model" in data
    assert "product" in data
    assert "order_status" in data
    assert "sales_executive" in data
    assert "customer_type" in data
    
    # Verify the structure is a list of {label, value}
    if len(data["business_model"]) > 0:
        first_item = data["business_model"][0]
        assert "label" in first_item
        assert "value" in first_item
