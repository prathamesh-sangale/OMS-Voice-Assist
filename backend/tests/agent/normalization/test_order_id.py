import pytest
from app.agent.normalization.order_id import normalize_order_id

def test_order_id_normalization():
    # Explicit OMS order ID
    assert normalize_order_id("OR612") == "OR612"
    
    # Natural variations with spaces and words
    assert normalize_order_id("order 612") == "OR612"
    assert normalize_order_id("order number 612") == "OR612"
    assert normalize_order_id("order no 612") == "OR612"
    assert normalize_order_id("order no. 612") == "OR612"
    
    # Spaced letters
    assert normalize_order_id("O R 6 1 2") == "OR612"
    assert normalize_order_id("OR 612") == "OR612"
    
    # Just digits
    assert normalize_order_id("612") == "OR612"
    
    # Empty cases
    assert normalize_order_id("") == ""
    assert normalize_order_id(None) == None
