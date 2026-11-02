from datetime import UTC, datetime, timedelta

from src.security import can_cancel


def test_owner_within_24h():
    now = datetime.now(UTC)
    assert can_cancel("NEW", 1, 1, False, now - timedelta(hours=1), now)
def test_stranger_denied():
    now = datetime.now(UTC)
    assert not can_cancel("NEW", 1, 2, False, now, now)
def test_shipped_denied_even_admin():
    now = datetime.now(UTC)
    assert not can_cancel("SHIPPED", 1, 1, True, now, now)
def test_expired_denied():
    now = datetime.now(UTC)
    assert not can_cancel("NEW", 1, 1, False, now - timedelta(hours=25), now)
def test_admin_can_cancel_others_new_order():
    # Un administrador (id=99) cancela un pedido NUEVO de otro usuario (id=1) -> Permitido
    now = datetime.now(UTC)
    created_at = now
    # Parámetros: status, owner_id, user_id, is_admin, created_at, now
    assert can_cancel("NEW", 1, 99, True, created_at, now) is True
def test_owner_cannot_cancel_at_exact_24h():
    # El propietario (id=1) intenta cancelar exactamente a las 24 horas -> Denegado (False)
    now = datetime.now(UTC)
    created_at = now - timedelta(hours=24)
    # Parámetros: status, owner_id, user_id, is_admin, created_at, now
    assert can_cancel("NEW", 1, 1, False, created_at, now) is False
FIXED_NOW = datetime(2026, 1, 15, 12, 0, tzinfo=UTC)

def test_owner_can_cancel_at_23h59():
    created_at = FIXED_NOW - timedelta(hours=23, minutes=59)
    assert can_cancel("NEW", 1, 1, False, created_at, FIXED_NOW) is True