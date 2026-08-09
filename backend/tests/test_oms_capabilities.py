import pytest
from app.oms.services.oms_service import OMSService
from app.oms.contracts.queries import OrderQuery, TaskQuery, CustomerQuery
from app.oms.repositories.json_repository import JSONOMSRepository
from app.oms.schemas.api import PaginatedResponse, OverviewResponse, AnalyticsData

@pytest.fixture
def real_service():
    # Points to actual dataset
    repo = JSONOMSRepository("app/data/crystal-oms-demo.json")
    return OMSService(repo)

def test_capability_list_orders(real_service):
    # Capability: List orders, Search orders, Filter orders
    q = OrderQuery(status="completed", page_size=2)
    res = real_service.list_orders(q)
    assert isinstance(res, PaginatedResponse)
    assert len(res.items) <= 2
    if len(res.items) > 0:
        assert res.items[0].status == "completed"

def test_capability_retrieve_order(real_service):
    # Capability: Retrieve order
    # Grab an ID from the list
    orders = real_service.list_orders(OrderQuery(page_size=1)).items
    if orders:
        order_id = orders[0].id
        order = real_service.retrieve_order_details(order_id)
        assert order.id == order_id

def test_capability_list_tasks(real_service):
    # Capability: List tasks
    q = TaskQuery(page_size=2)
    res = real_service.list_tasks(q)
    assert isinstance(res, PaginatedResponse)

def test_capability_customers_summary(real_service):
    # Capability: Derived customer summary
    q = CustomerQuery(page_size=1)
    res = real_service.get_customer_summary(q)
    assert isinstance(res, PaginatedResponse)
    
def test_capability_overview_metrics(real_service):
    # Capability: Derived OMS metrics
    res = real_service.get_overview_metrics()
    assert isinstance(res, OverviewResponse)
    assert res.metrics.total_order_value is None

def test_capability_analytics(real_service):
    # Capability: Order distributions
    res = real_service.get_order_analytics()
    assert isinstance(res, AnalyticsData)
    assert isinstance(res.business_model, list)
