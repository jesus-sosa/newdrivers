"""Router for exam configuration management (T081).

All endpoints require the 'admin' role.
Mounted at /api/admin in main.py.
"""

from typing import Annotated, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlmodel import Session

from app.core.database import get_session
from app.core.dependencies import require_roles
from app.services import admin_service

router = APIRouter()

_admin_only = require_roles(["admin"])


# ---------------------------------------------------------------------------
# Pydantic schemas
# ---------------------------------------------------------------------------

class ConfigUpdate(BaseModel):
    num_preguntas: Optional[int] = Field(default=None, ge=1)
    segundos_por_pregunta: Optional[int] = Field(default=None, ge=1)
    porcentaje_aprobacion: Optional[float] = None


# ---------------------------------------------------------------------------
# Endpoints
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
