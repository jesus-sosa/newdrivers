"""Admin service — exam configuration management (T080) and student management (T087)."""

from datetime import datetime, timezone
from typing import Optional
from uuid import UUID

from fastapi import HTTPException, status
from sqlmodel import Session, func, select

from app.core.security import hash_password
from app.models.config import ConfiguracionExamen
from app.models.intento import IntentoExamen
from app.models.pregunta import Pregunta
from app.models.user import User


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


# ---------------------------------------------------------------------------
# Student management (T087)
# ---------------------------------------------------------------------------

def list_students(
    q: Optional[str],
    activo: Optional[bool],
    page: int,
    page_size: int,
    session: Session,
) -> dict:
    """List students with pagination and optional filters.

    - q: searches nombre_completo and email (case-insensitive)
    - activo: defaults to True if not specified
    - Returns items with total_intentos and ultimo_resultado
    """
    effective_activo = activo if activo is not None else True

    stmt = select(User).where(User.rol == "estudiante").where(User.activo == effective_activo)

    if q:
        q_lower = q.lower()
        stmt = stmt.where(
            (func.lower(User.nombre_completo).contains(q_lower))
            | (func.lower(User.email).contains(q_lower))
        )

    # Count total before pagination
    count_stmt = select(func.count()).select_from(stmt.subquery())
    total = session.exec(count_stmt).one()

    # Apply pagination
    offset = (page - 1) * page_size
    stmt = stmt.offset(offset).limit(page_size)
    users = session.exec(stmt).all()

    # Batch-load intento stats to avoid N+1 queries
    user_ids = [u.id for u in users]
    intentos_count_map: dict[UUID, int] = {}
    ultimo_resultado_map: dict[UUID, Optional[str]] = {}

    if user_ids:
        count_rows = session.exec(
            select(IntentoExamen.estudiante_id, func.count().label("cnt"))
            .where(IntentoExamen.estudiante_id.in_(user_ids))
            .group_by(IntentoExamen.estudiante_id)
        ).all()
        intentos_count_map = {row[0]: row[1] for row in count_rows}

        finalizados = session.exec(
            select(IntentoExamen)
            .where(IntentoExamen.estudiante_id.in_(user_ids))
            .where(IntentoExamen.finalizado_at.is_not(None))  # type: ignore[union-attr]
            .order_by(IntentoExamen.finalizado_at.desc())  # type: ignore[union-attr]
        ).all()
        for intento in finalizados:
            if intento.estudiante_id not in ultimo_resultado_map:
                ultimo_resultado_map[intento.estudiante_id] = intento.resultado

    items = []
    for user in users:
        items.append(
            {
                "id": str(user.id),
                "nombre_completo": user.nombre_completo,
                "email": user.email,
                "activo": user.activo,
                "created_at": user.created_at.isoformat(),
                "total_intentos": intentos_count_map.get(user.id, 0),
                "ultimo_resultado": ultimo_resultado_map.get(user.id),
            }
        )

    return {
        "items": items,
        "total": total,
        "page": page,
        "page_size": page_size,
    }


def create_student(
    nombre_completo: str,
    email: str,
    password: str,
    session: Session,
) -> dict:
    """Create a new student user.

    Raises 409 if email already exists.
    Returns user dict without password_hash.
    """
    existing = session.exec(select(User).where(User.email == email)).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="El email ya está registrado",
        )

    user = User(
        nombre_completo=nombre_completo,
        email=email,
        password_hash=hash_password(password),
        rol="estudiante",
        activo=True,
    )
    session.add(user)
    session.commit()
    session.refresh(user)

    return {
        "id": str(user.id),
        "nombre_completo": user.nombre_completo,
        "email": user.email,
        "rol": user.rol,
        "activo": user.activo,
        "created_at": user.created_at.isoformat(),
    }


def get_student_with_history(student_id: UUID, session: Session) -> dict:
    """Return student details with exam attempt history.

    Raises 404 if not found or not rol=estudiante.
    """
    user = session.get(User, student_id)
    if user is None or user.rol != "estudiante":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Estudiante no encontrado",
        )

    intentos_rows = session.exec(
        select(IntentoExamen)
        .where(IntentoExamen.estudiante_id == student_id)
        .order_by(IntentoExamen.iniciado_at.desc())  # type: ignore[union-attr]
    ).all()

    intentos = [
        {
            "attempt_id": str(i.id),
            "iniciado_at": i.iniciado_at.isoformat(),
            "finalizado_at": i.finalizado_at.isoformat() if i.finalizado_at else None,
            "puntuacion": i.puntuacion,
            "total_preguntas": i.num_preguntas,
            "resultado": i.resultado,
        }
        for i in intentos_rows
    ]

    return {
        "id": str(user.id),
        "nombre_completo": user.nombre_completo,
        "email": user.email,
        "activo": user.activo,
        "created_at": user.created_at.isoformat(),
        "intentos": intentos,
    }


def toggle_student_status(
    student_id: UUID, activo: bool, session: Session, current_user_id: Optional[UUID] = None
) -> dict:
    """Activate or deactivate a student.

    Raises 400 if the admin tries to deactivate their own account.
    Raises 404 if student not found or not rol=estudiante.
    Returns updated user dict.
    """
    user = session.get(User, student_id)
    if user is None or user.rol != "estudiante":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Estudiante no encontrado",
        )

    if current_user_id is not None and student_id == current_user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No puedes desactivar tu propia cuenta.",
        )

    user.activo = activo
    session.add(user)
    session.commit()
    session.refresh(user)

    return {
        "id": str(user.id),
        "nombre_completo": user.nombre_completo,
        "email": user.email,
        "rol": user.rol,
        "activo": user.activo,
        "created_at": user.created_at.isoformat(),
    }
