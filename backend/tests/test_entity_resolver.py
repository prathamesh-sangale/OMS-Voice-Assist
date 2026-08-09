import pytest
from unittest.mock import Mock
from app.agent.resolution.entity_resolver import EntityResolver, ResolutionResult
from app.oms.schemas.api import PaginatedResponse
from app.oms.schemas.oms import OrderSchema

@pytest.fixture
def mock_oms():
    mock = Mock()
    mock.list_orders.return_value = PaginatedResponse(
        items=[
            OrderSchema(id="1", order_number="O1", sales_exec="Rohit Menon", client_name="Everest Pharmaceuticals Ltd"),
            OrderSchema(id="2", order_number="O2", sales_exec="Rohit Sharma", client_name="Acme Corp"),
            OrderSchema(id="3", order_number="O3", sales_exec="John Doe", client_name="John's Shop")
        ],
        total=3, page=1, page_size=10, pages=1
    )
    return mock

def test_resolve_sales_exec_exact_match(mock_oms):
    resolver = EntityResolver(mock_oms)
    res = resolver.resolve_sales_exec("Rohit Menon")
    assert res.resolved_value == "Rohit Menon"
    assert res.is_ambiguous is False

def test_resolve_sales_exec_ambiguous(mock_oms):
    resolver = EntityResolver(mock_oms)
    res = resolver.resolve_sales_exec("Rohit")
    assert res.is_ambiguous is True
    assert res.resolved_value is None
    assert len(res.candidates) == 2

def test_resolve_sales_exec_no_match(mock_oms):
    resolver = EntityResolver(mock_oms)
    res = resolver.resolve_sales_exec("XYZ")
    assert res.is_ambiguous is False
    assert res.resolved_value is None
    assert len(res.candidates) == 0

def test_resolve_customer_case_insensitive(mock_oms):
    resolver = EntityResolver(mock_oms)
    res = resolver.resolve_customer("everest pharmaceuticals ltd")
    assert res.resolved_value == "Everest Pharmaceuticals Ltd"
