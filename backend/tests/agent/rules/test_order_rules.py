from app.agent.rules.order_rules import GetOrderRule, ListOrdersFilterRule, ListOrdersGenericRule
from app.agent.models.intent import AgentIntent

def test_get_order_rule_match():
    rule = GetOrderRule()
    res = rule.match("show order or615")
    assert res is not None
    assert res.intent == AgentIntent.GET_ORDER
    assert res.entities["order_id"] == "OR615"
    assert res.query == "OR615"

def test_get_order_rule_no_match():
    rule = GetOrderRule()
    res = rule.match("show orders")
    assert res is None

def test_list_orders_filter_rule_match():
    rule = ListOrdersFilterRule()
    res = rule.match("show pending orders for rohit menon")
    assert res is not None
    assert res.intent == AgentIntent.LIST_ORDERS
    assert res.entities["status"] == "pending"
    assert res.entities["sales_exec_candidate"] == "rohit menon"
    assert res.query.status == "pending"
    # Note: query.sales_exec is NOT set here. The resolver handles that in the Engine.
    assert res.query.sales_exec is None 

def test_list_orders_generic_rule_match():
    rule = ListOrdersGenericRule()
    res = rule.match("show orders")
    assert res is not None
    assert res.intent == AgentIntent.LIST_ORDERS
