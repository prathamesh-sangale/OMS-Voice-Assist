import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_list_tasks():
    response = client.get("/api/tasks")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data
    assert "page" in data
    
def test_list_tasks_pagination():
    response = client.get("/api/tasks?page_size=2")
    assert response.status_code == 200
    data = response.json()
    assert data["page_size"] == 2
    assert len(data["items"]) <= 2

def test_list_tasks_filters():
    response = client.get("/api/tasks?status=done")
    assert response.status_code == 200
    data = response.json()
    for task in data["items"]:
        assert task["status"].lower() == "done"
