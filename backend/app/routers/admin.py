"""Router for exam configuration management (T081) and student management (T088).

All endpoints require the 'admin' role (or editor for some student endpoints).
Mounted at /api/admin in main.py.
"""

from typing import Annotated, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel, Field
from sqlmodel import Session

from app.core.database import get_session
from app.core.dependencies import require_roles
from app.services import admin_service

router = APIRouter()

_admin_only = require_roles(["admin"])
_admin_or_editor = require_roles(["admin", "editor"])


# ---------------------------------------------------------------------------
# Pydantic schemas
# ---------------------------------------------------------------------------

class ConfigUpdate(BaseModel):
    num_preguntas: Optional[int] = Field(default=None, ge=1)
    segundos_por_pregunta: Optional[int] = Field(default=None, ge=1)
    porcentaje_aprobacion: Optional[float] = None


class StudentCreate(BaseModel):
    nombre_completo: str
    email: str
    password: str


class StudentStatusUpdate(BaseModel):
    activo: bool


# ---------------------------------------------------------------------------
# Config endpoints
# ---------------------------------------------------------------------------

@router.get("/config")
def get_config(
    session: Annotated[Session, Depends(get_session)],
    _current_user=Depends(_admin_only),
):
    """GET /config — returns current exam configuration."""
    return admin_service.get_config(session)


@router.put("/config")
def update_config(
    data: ConfigUpdate,
    session: Annotated[Session, Depends(get_session)],
    current_user=Depends(_admin_only),
):
    """PUT /config — partial update of exam configuration.

    Returns 400 if:
    - num_preguntas > count of active questions
    - porcentaje_aprobacion is not in 0.0–100.0
    """
    payload = data.model_dump(exclude_unset=True)
    return admin_service.update_config(payload, current_user.id, session)


# ---------------------------------------------------------------------------
# Student endpoints (T088)
# ---------------------------------------------------------------------------

@router.get("/students")
def list_students(
    session: Annotated[Session, Depends(get_session)],
    _current_user=Depends(_admin_or_editor),
    q: Optional[str] = Query(default=None),
    activo: Optional[bool] = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
):
    """GET /students — list students (admin or editor)."""
    return admin_service.list_students(q, activo, page, page_size, session)


@router.post("/students", status_code=201)
def create_student(
    data: StudentCreate,
    session: Annotated[Session, Depends(get_session)],
    _current_user=Depends(_admin_or_editor),
):
    """POST /students — create a new student (admin or editor)."""
    return admin_service.create_student(
        data.nombre_completo, data.email, data.password, session
    )


@router.get("/students/{student_id}")
def get_student(
    student_id: UUID,
    session: Annotated[Session, Depends(get_session)],
    _current_user=Depends(_admin_only),
):
    """GET /students/{id} — student detail with history (admin only)."""
    return admin_service.get_student_with_history(student_id, session)


@router.patch("/students/{student_id}/status")
def toggle_student_status(
    student_id: UUID,
    data: StudentStatusUpdate,
    session: Annotated[Session, Depends(get_session)],
    current_user=Depends(_admin_only),
):
    """PATCH /students/{id}/status — activate/deactivate student (admin only)."""
    return admin_service.toggle_student_status(
        student_id, data.activo, session, current_user_id=current_user.id
    )
