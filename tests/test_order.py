import pytest
from src.domain import CustomerHasDebt, Order
def test_vip_discount():
    o = Order(100, vip=True)
    assert o.confirm() == 85
    assert o.status == "CONFIRMED"
def test_regular_no_discount():
    assert Order(100).confirm() == 100
def test_customer_debt():
    with pytest.raises(CustomerHasDebt):
        Order(100).confirm(customer_debt=50)
@pytest.mark.parametrize("total", [0, -1])
def test_invalid_total(total):
    with pytest.raises(ValueError):
        Order(total).confirm()
def test_cannot_confirm_twice():
    order = Order(100)
    order.confirm()
    with pytest.raises(ValueError, match="already confirmed"):
        order.confirm()
# --- E2: casos con total 200 ---
def test_vip_discount_200():
    order = Order(200, vip=True)
    assert order.confirm() == 170
    assert order.discount == 30
    assert order.status == "CONFIRMED"
def test_regular_no_discount_200():
    order = Order(200)
    assert order.confirm() == 200
    assert order.discount == 0
# --- Casos límite ---
def test_minimum_positive_total_is_valid():
    order = Order(0.01)
    assert order.confirm() == 0.01
    assert order.status == "CONFIRMED"
def test_zero_debt_allows_confirmation():
    order = Order(100)
    assert order.confirm(customer_debt=0) == 100
    assert order.status == "CONFIRMED"