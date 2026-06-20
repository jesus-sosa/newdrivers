"""Admin service — exam configuration management (T080)."""

from datetime import datetime, timezone
from uuid import UUID

from fastapi import HTTPException, status
from sqlmodel import Session, func, select

from app.models.config import ConfiguracionExamen
from app.models.pregunta import Pregunta


def get_config(session: Session) -> dict:
    """Return the singleton ConfiguracionExamen (creates with defaults if absent).

    Computes estado_sistema:
    - "no_configurado"  when porcentaje_aprobacion is None
    - "activo"          otherwise
    """
    config = session.get(ConfiguracionExamen, 1)
    if config is None:
        config = ConfiguracionExamen(
            id=1,
            num_preguntas=20,
            segundos_por_pregunta=60,
            porcentaje_aprobacion=None,
        )
        session.add(config)
        session.commit()
        session.refresh(config)

    estado_sistema = (
        "no_configurado" if config.porcentaje_aprobacion is None else "activo"
    )

    return {
        "num_preguntas": config.num_preguntas,
        "segundos_por_pregunta": config.segundos_por_pregunta,
        "porcentaje_aprobacion": config.porcentaje_aprobacion,
        "updated_at": config.updated_at.isoformat() if config.updated_at else None,
        "updated_by": str(config.updated_by) if config.updated_by else None,
        "estado_sistema": estado_sistema,
    }


def update_config(data: dict, updated_by_id: UUID, session: Session) -> dict:
    """Partial update of the exam configuration.

    Validations:
    - num_preguntas must be <= count of active Pregunta rows (400 if not)
    - porcentaje_aprobacion must be 0.0–100.0 (400 if out of range)
    """
    # Validate porcentaje_aprobacion if provided
    if "porcentaje_aprobacion" in data and data["porcentaje_aprobacion"] is not None:
        pct = data["porcentaje_aprobacion"]
        if pct < 0.0 or pct > 100.0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="porcentaje_aprobacion debe estar entre 0.0 y 100.0.",
            )

    # Validate num_preguntas if provided
    if "num_preguntas" in data:
        count_activas = session.exec(
            select(func.count()).where(Pregunta.activa == True)  # noqa: E712
        ).one()
        if data["num_preguntas"] > count_activas:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    f"num_preguntas ({data['num_preguntas']}) excede el número de "
                    f"preguntas activas ({count_activas})."
                ),
            )

    # Get or create config
    config = session.get(ConfiguracionExamen, 1)
    if config is None:
        config = ConfiguracionExamen(
            id=1,
            num_preguntas=20,
            segundos_por_pregunta=60,
            porcentaje_aprobacion=None,
        )
        session.add(config)

    # Apply partial update
    for field, value in data.items():
        setattr(config, field, value)

    config.updated_at = datetime.now(timezone.utc)
    config.updated_by = updated_by_id

    session.add(config)
    session.commit()
    session.refresh(config)

    return get_config(session)
