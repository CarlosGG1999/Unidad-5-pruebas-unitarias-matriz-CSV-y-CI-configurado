from unittest.mock import Mock

import pytest

from src.application import OrderService
from src.domain import Order


def test_gateway_approved():
    gateway = Mock()
    gateway.charge.return_value = True
    assert OrderService(gateway).checkout(Order(100)) == 100
    gateway.charge.assert_called_once_with(100)
def test_gateway_rejected():
    gateway = Mock()
    gateway.charge.return_value = False
    with pytest.raises(RuntimeError):
        OrderService(gateway).checkout(Order(100))
def test_vip_payment_rejected():
    gateway = Mock()
    gateway.charge.return_value = False  # Simula rechazo del pago
    service = OrderService(gateway)
    order = Order(200, vip=True)  # Total $200, VIP -> $170 a cobrar
    with pytest.raises(RuntimeError, match="payment rejected"):
        service.checkout(order)     
    gateway.charge.assert_called_once_with(170)
def test_gateway_timeout_propagates():
    gateway = Mock()
    gateway.charge.side_effect = TimeoutError("gateway timeout")
    with pytest.raises(TimeoutError):
        OrderService(gateway).checkout(Order(100))
    gateway.charge.assert_called_once_with(100)
def test_rejected_payment_leaves_order_confirmed_known_risk():
    # RIESGO DOCUMENTADO (E5): checkout() confirma el pedido ANTES de cobrar.    # Si la pasarela rechaza el pago, el pedido queda CONFIRMED sin pago exitoso. # Esta prueba muestra el comportamiento actual; la mejora propuesta es cobrar # primero y confirmar solo si el cobro fue exitoso (o revertir el estado al fallar).
    gateway = Mock()
    gateway.charge.return_value = False
    order = Order(100)
    with pytest.raises(RuntimeError, match="payment rejected"):
        OrderService(gateway).checkout(order)
    assert order.status == "CONFIRMED"