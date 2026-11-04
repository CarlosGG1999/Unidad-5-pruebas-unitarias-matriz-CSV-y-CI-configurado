"""Dominio de EduTech Academy.

Solo implementa reglas aprobadas en el BRD y en la Unidad 3: cupo de grupo (5-25),
calificación mínima aprobatoria (70) y el ciclo Inscripcion/Pago. Los valores que el
negocio aun no confirma (asistencia minima) se reciben como configuracion.
"""
from dataclasses import dataclass, field

NOTA_MINIMA_APROBATORIA = 75
CUPO_MAXIMO = 25


class GrupoSinCupo(Exception):
    pass


class EstudianteNoApto(Exception):
    pass


class PagoYaRegistrado(Exception):
    pass


@dataclass(frozen=True)
class InscripcionRealizada:
    estudiante_id: str
    curso_id: str
    grupo_id: str


@dataclass(frozen=True)
class CupoMaximoAlcanzado:
    curso_id: str
    grupo_id: str


@dataclass(frozen=True)
class PagoRegistrado:
    inscripcion_id: int


@dataclass(frozen=True)
class Cupo:
    """Value Object: solo importan sus valores, no tiene identidad."""

    ocupados: int = 0

    @property
    def lleno(self) -> bool:
        return self.ocupados >= CUPO_MAXIMO

    def ocupar(self) -> "Cupo":
        if self.lleno:
            raise GrupoSinCupo("Grupo sin cupo")
        return Cupo(self.ocupados + 1)


@dataclass
class Grupo:
    id: str
    cupo: Cupo = field(default_factory=Cupo)

    def ocupar_lugar(self) -> None:
        self.cupo = self.cupo.ocupar()


@dataclass
class Curso:
    """Aggregate root: todo cambio de cupo pasa por el curso."""

    id: str
    nombre: str = ""
    grupos: dict = field(default_factory=dict)
    eventos: list = field(default_factory=list)

    def ocupar_lugar(self, grupo_id: str) -> None:
        grupo = self.grupos[grupo_id]
        grupo.ocupar_lugar()
        if grupo.cupo.lleno:
            self.eventos.append(CupoMaximoAlcanzado(self.id, grupo_id))


@dataclass
class Inscripcion:
    estudiante_id: str
    curso_id: str
    grupo_id: str
    id: int | None = None
    estado: str = "Pago pendiente"
    pago_estado: str = "Pendiente"

    def registrar_pago(self) -> None:
        if self.pago_estado == "Pagado":
            raise PagoYaRegistrado("Pago ya registrado")
        self.pago_estado = "Pagado"
        self.estado = "Inscrito"


@dataclass(frozen=True)
class Nota:
    valor: float

    @property
    def aprobatoria(self) -> bool:
        return self.valor >= NOTA_MINIMA_APROBATORIA


@dataclass(frozen=True)
class PorcentajeAsistencia:
    valor: float

    def cumple(self, minimo: float) -> bool:
        return self.valor >= minimo


@dataclass(frozen=True)
class PoliticaCertificacion:
    """Reglas configurables: EduTech aun no confirma la asistencia minima."""

    asistencia_minima: float


def validar_requisitos_certificacion(
    nota: Nota,
    asistencia: PorcentajeAsistencia,
    curso_concluido: bool,
    pago_regularizado: bool,
    politica: PoliticaCertificacion,
) -> str:
    motivos = []
    if not nota.aprobatoria:
        motivos.append("calificación menor a 70")
    if not asistencia.cumple(politica.asistencia_minima):
        motivos.append("asistencia insuficiente")
    if not curso_concluido:
        motivos.append("curso no concluido")
    if not pago_regularizado:
        motivos.append("pago pendiente")
    if motivos:
        raise EstudianteNoApto("Estudiante no apto para certificación: " + ", ".join(motivos))
    return "Apto para certificación"
