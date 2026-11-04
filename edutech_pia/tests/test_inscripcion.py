"""Regla 3: inscripcion y pago (CU-02, US-02, US-05).

Integra Service Layer + Repository (SQLite en memoria). El EventBus se simula con un Mock:
EduTech no define una integracion externa en su alcance, solo la publicacion de eventos.
"""
from unittest.mock import Mock, call

import pytest
from sqlalchemy.orm import Session

from src.application import InscripcionService
from src.domain import (
    Cupo,
    CupoMaximoAlcanzado,
    Curso,
    Grupo,
    GrupoSinCupo,
    InscripcionRealizada,
    PagoRegistrado,
    PagoYaRegistrado,
)
from src.repository import CursoRepository, GrupoRow, InscripcionRow, make_engine


@pytest.fixture
def engine():
    return make_engine()


def preparar_curso(engine, ocupados):
    with Session(engine) as session:
        CursoRepository(session).add(Curso("C1", "Python", {"G1": Grupo("G1", Cupo(ocupados))}))
        session.commit()


def leer(engine):
    with Session(engine) as session:
        ocupados = session.get(GrupoRow, "G1").ocupados
        inscripciones = session.query(InscripcionRow).all()
        return ocupados, [(i.estado, i.pago_estado) for i in inscripciones]


def test_inscripcion_ocupa_lugar_y_crea_pago_pendiente(engine):
    preparar_curso(engine, 10)
    bus = Mock()
    with Session(engine) as session:
        inscripcion = InscripcionService(session, bus).registrar_inscripcion("E1", "C1", "G1")
    assert inscripcion.id is not None
    assert leer(engine) == (11, [("Pago pendiente", "Pendiente")])
    bus.publish.assert_called_once_with(InscripcionRealizada("E1", "C1", "G1"))


def test_grupo_sin_cupo_rechaza_y_no_guarda_nada(engine):
    preparar_curso(engine, 25)
    bus = Mock()
    with Session(engine) as session, pytest.raises(GrupoSinCupo, match="Grupo sin cupo"):
        InscripcionService(session, bus).registrar_inscripcion("E1", "C1", "G1")
    assert leer(engine) == (25, [])
    bus.publish.assert_not_called()


def test_ultimo_lugar_publica_cupo_maximo_alcanzado(engine):
    preparar_curso(engine, 24)
    bus = Mock()
    with Session(engine) as session:
        InscripcionService(session, bus).registrar_inscripcion("E1", "C1", "G1")
    assert leer(engine)[0] == 25
    assert bus.publish.call_args_list == [
        call(InscripcionRealizada("E1", "C1", "G1")),
        call(CupoMaximoAlcanzado("C1", "G1")),
    ]


def test_registrar_pago_cambia_inscripcion_y_pago_juntos(engine):
    preparar_curso(engine, 10)
    bus = Mock()
    with Session(engine) as session:
        servicio = InscripcionService(session, bus)
        inscripcion = servicio.registrar_inscripcion("E1", "C1", "G1")
        servicio.registrar_pago(inscripcion.id)
    assert leer(engine)[1] == [("Inscrito", "Pagado")]
    assert bus.publish.call_args_list[-1] == call(PagoRegistrado(inscripcion.id))


def test_pago_duplicado_se_rechaza_y_conserva_el_estado(engine):
    preparar_curso(engine, 10)
    bus = Mock()
    with Session(engine) as session:
        servicio = InscripcionService(session, bus)
        inscripcion = servicio.registrar_inscripcion("E1", "C1", "G1")
        servicio.registrar_pago(inscripcion.id)
        with pytest.raises(PagoYaRegistrado, match="Pago ya registrado"):
            servicio.registrar_pago(inscripcion.id)
    assert leer(engine)[1] == [("Inscrito", "Pagado")]
