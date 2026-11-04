"""Infraestructura: persistencia con SQLAlchemy (SQLite en memoria para pruebas)."""
from sqlalchemy import ForeignKey, create_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column

from src.domain import Cupo, Curso, Grupo, Inscripcion


class Base(DeclarativeBase):
    pass


class CursoRow(Base):
    __tablename__ = "cursos"
    id: Mapped[str] = mapped_column(primary_key=True)
    nombre: Mapped[str]


class GrupoRow(Base):
    __tablename__ = "grupos"
    id: Mapped[str] = mapped_column(primary_key=True)
    curso_id: Mapped[str] = mapped_column(ForeignKey("cursos.id"))
    ocupados: Mapped[int]


class InscripcionRow(Base):
    __tablename__ = "inscripciones"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    estudiante_id: Mapped[str]
    curso_id: Mapped[str] = mapped_column(ForeignKey("cursos.id"))
    grupo_id: Mapped[str] = mapped_column(ForeignKey("grupos.id"))
    estado: Mapped[str]
    pago_estado: Mapped[str]


def make_engine(url: str = "sqlite+pysqlite:///:memory:"):
    engine = create_engine(url)
    Base.metadata.create_all(engine)
    return engine


class CursoRepository:
    def __init__(self, session: Session):
        self.session = session

    def add(self, curso: Curso) -> None:
        self.session.add(CursoRow(id=curso.id, nombre=curso.nombre))
        for grupo in curso.grupos.values():
            self.session.add(GrupoRow(id=grupo.id, curso_id=curso.id, ocupados=grupo.cupo.ocupados))

    def find_by_id(self, curso_id: str) -> Curso:
        row = self.session.get(CursoRow, curso_id)
        grupos = self.session.query(GrupoRow).filter_by(curso_id=curso_id).all()
        return Curso(
            id=row.id,
            nombre=row.nombre,
            grupos={g.id: Grupo(g.id, Cupo(g.ocupados)) for g in grupos},
        )

    def save(self, curso: Curso) -> None:
        for grupo in curso.grupos.values():
            self.session.get(GrupoRow, grupo.id).ocupados = grupo.cupo.ocupados


class InscripcionRepository:
    def __init__(self, session: Session):
        self.session = session

    def add(self, inscripcion: Inscripcion) -> None:
        row = InscripcionRow(
            estudiante_id=inscripcion.estudiante_id,
            curso_id=inscripcion.curso_id,
            grupo_id=inscripcion.grupo_id,
            estado=inscripcion.estado,
            pago_estado=inscripcion.pago_estado,
        )
        self.session.add(row)
        self.session.flush()
        inscripcion.id = row.id

    def find_by_id(self, inscripcion_id: int) -> Inscripcion:
        row = self.session.get(InscripcionRow, inscripcion_id)
        return Inscripcion(
            estudiante_id=row.estudiante_id,
            curso_id=row.curso_id,
            grupo_id=row.grupo_id,
            id=row.id,
            estado=row.estado,
            pago_estado=row.pago_estado,
        )

    def save(self, inscripcion: Inscripcion) -> None:
        row = self.session.get(InscripcionRow, inscripcion.id)
        row.estado = inscripcion.estado
        row.pago_estado = inscripcion.pago_estado
