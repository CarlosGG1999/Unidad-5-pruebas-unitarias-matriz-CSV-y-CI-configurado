"""Service Layer: coordina casos de uso; las reglas viven en el dominio."""
from sqlalchemy.orm import Session

from src.domain import Inscripcion, InscripcionRealizada, PagoRegistrado
from src.repository import CursoRepository, InscripcionRepository


class InscripcionService:
    def __init__(self, session: Session, event_bus):
        self.session = session
        self.event_bus = event_bus

    def registrar_inscripcion(self, estudiante_id: str, curso_id: str, grupo_id: str) -> Inscripcion:
        cursos = CursoRepository(self.session)
        inscripciones = InscripcionRepository(self.session)
        try:
            curso = cursos.find_by_id(curso_id)
            curso.ocupar_lugar(grupo_id)
            inscripcion = Inscripcion(estudiante_id, curso_id, grupo_id)
            cursos.save(curso)
            inscripciones.add(inscripcion)
            self.session.commit()
        except Exception:
            self.session.rollback()
            raise
        self.event_bus.publish(InscripcionRealizada(estudiante_id, curso_id, grupo_id))
        for evento in curso.eventos:
            self.event_bus.publish(evento)
        return inscripcion

    def registrar_pago(self, inscripcion_id: int) -> Inscripcion:
        inscripciones = InscripcionRepository(self.session)
        try:
            inscripcion = inscripciones.find_by_id(inscripcion_id)
            inscripcion.registrar_pago()
            inscripciones.save(inscripcion)
            self.session.commit()
        except Exception:
            self.session.rollback()
            raise
        self.event_bus.publish(PagoRegistrado(inscripcion_id))
        return inscripcion
