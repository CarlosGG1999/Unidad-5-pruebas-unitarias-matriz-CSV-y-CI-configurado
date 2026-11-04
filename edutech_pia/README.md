# EduTech Academy: pruebas de lógica de negocio (Unidad 5, E9)

Pruebas automatizadas de tres reglas aprobadas de EduTech Academy: control de cupo del grupo,
requisitos de certificación e inscripción con pago pendiente.

## Instalación

```
python -m venv .venv
.venv\Scripts\activate        # Windows (PowerShell)
pip install -r requirements.txt
```

## Comandos

```
python -m pytest -v
python -m pytest -v --cov=src --cov-report=term-missing --cov-report=html --cov-fail-under=80
python -m ruff check src tests
```

El reporte HTML de cobertura queda en `htmlcov/index.html`.

## Arquitectura

| Capa | Archivo | Responsabilidad |
|---|---|---|
| Dominio | `src/domain.py` | Reglas e invariantes: Cupo, Grupo, Curso, Inscripcion, Nota, PorcentajeAsistencia y la validación de certificación. |
| Aplicación | `src/application.py` | `InscripcionService`: coordina el caso de uso, confirma o revierte la transacción y publica eventos. |
| Infraestructura | `src/repository.py` | Repositorios con SQLAlchemy y SQLite en memoria. |

El dominio decide y el servicio coordina. Los Domain Events se publican después del commit.

## Pruebas

| Archivo | Qué prueba |
|---|---|
| `tests/test_cupo.py` | Cupo máximo de 25 por grupo (dominio). |
| `tests/test_certificacion.py` | Calificación mínima de 70, asistencia, curso concluido y pago regularizado (dominio). |
| `tests/test_inscripcion.py` | Servicio + repositorio SQLite + mock del EventBus. |

La matriz de casos está en `matriz_pruebas_edutech.csv`.

## Reglas pendientes

La asistencia mínima aún no la confirma EduTech, por eso es un parámetro (`PoliticaCertificacion`).
En las pruebas se usa 80 como valor de prueba, no como política aprobada. El cupo mínimo de 5 no se
implementó porque los documentos no definen qué ocurre con menos de 5 inscritos.
