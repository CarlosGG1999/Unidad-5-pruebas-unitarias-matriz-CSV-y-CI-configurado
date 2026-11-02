import pytest
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from src.domain import Order
from src.repository import OrderRow, SqlOrderRepository, make_engine
def test_repository_commit():
    engine = make_engine()
    with Session(engine) as session:
        SqlOrderRepository(session).save(1, Order(120))
        session.commit()
        assert session.scalar(select(OrderRow).where(OrderRow.id == 1)).total == 120
def test_repository_rollback():
    engine = make_engine()
    with Session(engine) as session:
        SqlOrderRepository(session).save(1, Order(120))
        session.rollback()
        assert session.scalar(select(OrderRow).where(OrderRow.id == 1)) is None
def test_repository_custom_order():
    engine = make_engine()
    with Session(engine) as session:
        SqlOrderRepository(session).save(2, Order(250))
        session.commit()
        row = session.scalar(select(OrderRow).where(OrderRow.id == 2))
        assert row is not None
        assert row.id == 2
        assert row.total == 250
        assert row.status == "NEW"
def test_repository_duplicate_id_violates_uniqueness(tmp_path):
    # Base en archivo temporal para usar dos sesiones independientes sobre la misma BD
    engine = make_engine(f"sqlite+pysqlite:///{tmp_path / 'unicidad.sqlite3'}")
    with Session(engine) as first:
        SqlOrderRepository(first).save(1, Order(100))
        first.commit()
    with Session(engine) as second:
        SqlOrderRepository(second).save(1, Order(200))
        with pytest.raises(IntegrityError):
            second.commit()
        second.rollback()
    with Session(engine) as check:
        row = check.scalar(select(OrderRow).where(OrderRow.id == 1))
        assert row.total == 100  # el registro original no fue modificado