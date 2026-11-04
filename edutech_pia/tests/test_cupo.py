"""Regla 1: control de cupo del grupo (BR-03, US-04). Maximo aprobado: 25."""
import pytest

from src.domain import Cupo, CupoMaximoAlcanzado, Curso, Grupo, GrupoSinCupo


def test_ocupar_lugar_con_cupo_disponible():
    curso = Curso("C1", grupos={"G1": Grupo("G1", Cupo(10))})
    curso.ocupar_lugar("G1")
    assert curso.grupos["G1"].cupo.ocupados == 11
    assert curso.eventos == []


def test_grupo_lleno_rechaza_inscripcion():
    grupo = Grupo("G1", Cupo(25))
    with pytest.raises(GrupoSinCupo, match="Grupo sin cupo"):
        grupo.ocupar_lugar()
    assert grupo.cupo.ocupados == 25


def test_ultimo_lugar_llena_el_grupo_y_registra_evento():
    curso = Curso("C1", grupos={"G1": Grupo("G1", Cupo(24))})
    curso.ocupar_lugar("G1")
    assert curso.grupos["G1"].cupo.ocupados == 25
    assert curso.grupos["G1"].cupo.lleno is True
    assert curso.eventos == [CupoMaximoAlcanzado("C1", "G1")]
