import pytest
import json
import os
import tempfile
from pydantic import ValidationError

from app.oms.schemas.oms import OrderSchema, ProductConfigSchema, ContainerSchema
from app.oms.repositories.json_repository import JSONOMSRepository
from app.oms.exceptions import OMSDataSourceError, OMSRecordNotFoundError, OMSDataValidationError

@pytest.fixture
def valid_demo_data():
    return {
        "oms_orders": [
            {
                "id": "123-uuid",
                "order_number": "OR601",
                "client_name": "Test Client",
                "product_type": "Dry Container",
                "business_model": "Sale",
                "order_type": "New",
                "quantity": "3",
                "sales_exec": "Gargi",
                "commitment_date": "2026-08-19",
                "current_stage": "1.1",
                "status": "pending_approval",
                "config_id": None,
                "meta": {},
                "customer_type": "New",
                "is_sez": "No",
                "sez_certificate": "",
                "container_pi": "Yes",
                "transport_pi": "Yes",
                "pi_for": ["Transportation"],
                "product_types": ["Dry Container"],
                "product_configs": [{"product": "Dry Container", "quantity": 3, "business_model": "Sale"}],
                "containers": [],
                "po_received_date": "2026-08-01",
                "sales_enquiry_code": "EQ17681",
                "loading_city": "Delhi",
                "delivery_city": "Pune",
                "delivery_state": "Maharashtra",
                "transport_mode": "Road",
                "transport_in_po": "Yes",
                "transport_remark": "",
                "billing_name": "A",
                "billing_number": "1",
                "billing_email": "a@b.c",
                "billing_address": "Addr",
                "dispatch_name": "A",
                "dispatch_number": "1",
                "dispatch_email": "a@b.c",
                "dispatch_address": "Addr",
                "finance_name": "A",
                "finance_number": "1",
                "finance_email": "a@b.c",
                "installation_number": None
            }
        ],
        "oms_order_tasks": [
            {
                "id": "task-uuid",
                "order_id": "123-uuid",
                "stage_key": "1",
                "stage_label": "1",
                "status": "done",
                "assigned_to": None,
                "department": "sales",
                "planned_date": "2026-08-02",
                "actual_date": "2026-08-03",
                "tat_days": 1,
                "notes": "",
                "done_by": "sales",
                "done_at": "now",
                "created_at": "now",
                "updated_at": "now",
                "meta": {}
            }
        ]
    }

@pytest.fixture
def temp_json_file(valid_demo_data):
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
        json.dump(valid_demo_data, f)
        temp_name = f.name
    yield temp_name
    os.unlink(temp_name)

def test_missing_json_file():
    with pytest.raises(OMSDataSourceError):
        JSONOMSRepository("nonexistent.json")

def test_invalid_json_format():
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
        f.write("invalid json")
        temp_name = f.name
    try:
        with pytest.raises(OMSDataSourceError):
            JSONOMSRepository(temp_name)
    finally:
        os.unlink(temp_name)

def test_schema_validation_error(valid_demo_data):
    # Mess up a required field
    del valid_demo_data["oms_orders"][0]["id"]
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
        json.dump(valid_demo_data, f)
        temp_name = f.name
    
    try:
        with pytest.raises(OMSDataValidationError):
            JSONOMSRepository(temp_name)
    finally:
        os.unlink(temp_name)

def test_repository_list_orders(temp_json_file):
    repo = JSONOMSRepository(temp_json_file)
    orders = repo.list_orders()
    assert len(orders) == 1
    assert isinstance(orders[0], OrderSchema)
    assert orders[0].order_number == "OR601"

def test_repository_get_order(temp_json_file):
    repo = JSONOMSRepository(temp_json_file)
    order = repo.get_order("123-uuid")
    assert order is not None
    assert order.id == "123-uuid"

def test_repository_get_order_not_found(temp_json_file):
    repo = JSONOMSRepository(temp_json_file)
    with pytest.raises(OMSRecordNotFoundError):
        repo.get_order("unknown")

def test_repository_get_tasks(temp_json_file):
    repo = JSONOMSRepository(temp_json_file)
    tasks = repo.get_tasks_for_order("123-uuid")
    assert len(tasks) == 1
    assert tasks[0].id == "task-uuid"

def test_real_json_loads():
    # Will point to the copied actual file
    repo = JSONOMSRepository("app/data/crystal-oms-demo.json")
    orders = repo.list_orders()
    assert len(orders) > 0
    assert orders[0].order_number == "OR601"
