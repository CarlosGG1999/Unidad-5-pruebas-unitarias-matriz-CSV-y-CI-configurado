"""Regla 2: requisitos de certificacion (US-10, US-11). Nota minima aprobada: 70.

La asistencia minima aun no esta confirmada por EduTech: 80 es un valor de PRUEBA
pasado como configuracion, no una politica aprobada.
"""
import pytest

from src.domain import (
    EstudianteNoApto,
    Nota,
    PoliticaCertificacion,
    PorcentajeAsistencia,
    validar_requisitos_certificacion,
)

ASISTENCIA_MINIMA_DE_PRUEBA = 80.0
POLITICA = PoliticaCertificacion(asistencia_minima=ASISTENCIA_MINIMA_DE_PRUEBA)


def validar(nota=85, asistencia=95.0, concluido=True, pagado=True):
    return validar_requisitos_certificacion(
        Nota(nota), PorcentajeAsistencia(asistencia), concluido, pagado, POLITICA
    )


def test_estudiante_que_cumple_todo_es_apto():
    assert validar() == "Apto para certificación"


@pytest.mark.parametrize(
    "kwargs, motivo",
    [
        ({"nota": 69}, "calificación"),
        ({"asistencia": ASISTENCIA_MINIMA_DE_PRUEBA - 0.1}, "asistencia"),
        ({"concluido": False}, "curso no concluido"),
        ({"pagado": False}, "pago pendiente"),
    ],
    ids=["nota_69", "asistencia_bajo_minimo", "curso_no_concluido", "pago_pendiente"],
)
def test_incumplir_un_requisito_no_es_apto(kwargs, motivo):
    with pytest.raises(EstudianteNoApto, match="no apto para certificación") as error:
        validar(**kwargs)
    assert motivo in str(error.value)


def test_nota_exactamente_70_es_apto():
    assert validar(nota=70) == "Apto para certificación"


def test_asistencia_exactamente_en_el_minimo_es_apto():
    assert validar(asistencia=ASISTENCIA_MINIMA_DE_PRUEBA) == "Apto para certificación"
