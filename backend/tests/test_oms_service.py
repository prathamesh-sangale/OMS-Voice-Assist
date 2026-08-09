import pytest
from app.oms.schemas.oms import OrderSchema, OrderTaskSchema
from app.oms.services.oms_service import OMSService
from app.oms.contracts.queries import OrderQuery, TaskQuery, CustomerQuery

class MockRepository:
    def __init__(self, orders, tasks):
        self._orders = orders
        self._tasks = tasks
        
    def list_orders(self, search=None, status=None, business_model=None, product=None, sales_exec=None):
        return self._orders
        
    def get_order(self, order_id):
        for o in self._orders:
            if o.id == order_id: return o
        return None
        
    def list_tasks(self, search=None, status=None, department=None, stage=None, order_id=None):
        return self._tasks
        
    def get_tasks_for_order(self, order_id):
        return [t for t in self._tasks if t.order_id == order_id]

@pytest.fixture
def mock_service():
    orders = [
        # Normal complete order
        OrderSchema(
            id="1", order_number="OR1", client_name="Client A", status="completed",
            customer_type="Enterprise", business_model="Sale", sales_exec="Alice",
            loading_city="City X", delivery_city="City Y",
            product_types=["Dry Container"], product_configs=[{"product": "Dry Container", "quantity": 1, "business_model": "Sale"}]
        ),
        # Sparse order missing many fields
        OrderSchema(
            id="2", order_number="OR2", client_name="Client B", status="pending",
            customer_type=None, business_model=None, sales_exec=None,
            loading_city=None, delivery_city=None,
            product_types=None, product_configs=None
        ),
        # Order with multiple sales execs for the same client (simulating another order by same client)
        OrderSchema(
            id="3", order_number="OR3", client_name="Client A", status="pending",
            customer_type="Enterprise", business_model="Rental", sales_exec="Bob",
            loading_city="City Z", delivery_city="City Y",
            product_types=None, product_configs=[{"product": "Reefer", "quantity": 2, "business_model": "Rental"}]
        )
    ]
    tasks = [
        OrderTaskSchema(id="t1", order_id="1", stage_key="1", stage_label="1", status="done", department="sales", created_at="now", updated_at="now"),
        OrderTaskSchema(id="t2", order_id="2", stage_key="1", stage_label="1", status="pending", department="logistics", created_at="now", updated_at="now")
    ]
    return OMSService(MockRepository(orders, tasks))

def test_get_customer_summary_aggregates_sparse_data(mock_service):
    # Customer summary should group by client_name
    query = CustomerQuery(page_size=10)
    response = mock_service.get_customer_summary(query)
    
    assert response.total == 2
    
    # Client A should have 2 orders, 1 active, sales execs Alice and Bob, cities aggregated
    client_a = next(c for c in response.items if c.client_name == "Client A")
    assert client_a.total_orders == 2
    assert client_a.active_orders == 1
    assert set(client_a.sales_execs) == {"Alice", "Bob"}
    assert set(client_a.loading_cities) == {"City X", "City Z"}
    assert set(client_a.delivery_cities) == {"City Y"} # Deduped
    
    # Client B should have 1 order, sparse data safely handled
    client_b = next(c for c in response.items if c.client_name == "Client B")
    assert client_b.total_orders == 1
    assert client_b.active_orders == 1
    assert client_b.sales_execs == []
    assert client_b.loading_cities == []

def test_get_overview_metrics_with_sparse_status(mock_service):
    response = mock_service.get_overview_metrics()
    
    metrics = response.metrics
    assert metrics.completed_orders == 1
    assert metrics.pending_orders == 2
    assert metrics.needs_revision == 0
    assert metrics.active_orders == 0
    assert metrics.total_order_value is None

def test_get_order_analytics_with_sparse_data(mock_service):
    response = mock_service.get_order_analytics()
    
    # Business model (Client B has None, so only 2 counted)
    bm_total = sum(d.value for d in response.business_model)
    assert bm_total == 2
    assert any(d.label == "Sale" and d.value == 1 for d in response.business_model)
    
    # Products (Client A has both types and configs but handled safely, Client B has none, Client C has only config)
    # Total products = 1 (Dry) + 1 (Reefer) = 2
    prod_total = sum(d.value for d in response.product)
    assert prod_total == 2
