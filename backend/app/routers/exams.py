from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel, field_validator
from sqlmodel import Session

from app.core.database import get_session
from app.core.dependencies import get_current_user, require_roles
from app.models.user import User
from app.services import exam_service

router = APIRouter()


# ---------------------------------------------------------------------------
# Schemas de request/response
# ---------------------------------------------------------------------------

class AnswerRequest(BaseModel):
    orden: int
    opcion_seleccionada: str | None = None
    tiempo_agotado: bool = False

    @field_validator("opcion_seleccionada")
    @classmethod
    def validate_opcion(cls, v: str | None) -> str | None:
        if v is not None and v.upper() not in ("A", "B", "C", "D"):
            raise ValueError("opcion_seleccionada debe ser A, B, C o D")
        return v.upper() if v else v


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@router.post("/start", status_code=201)
def start_exam(
    session: Annotated[Session, Depends(get_session)],
    current_user: Annotated[User, Depends(require_roles(["estudiante"]))],
):
    return exam_service.start_exam(current_user.id, session)


@router.get("/history")
def get_history(
    session: Annotated[Session, Depends(get_session)],
    current_user: Annotated[User, Depends(require_roles(["estudiante"]))],
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=100),
):
    return exam_service.get_history(current_user.id, page, page_size, session)


@router.get("/{attempt_id}")
def get_exam_state(
    attempt_id: UUID,
    session: Annotated[Session, Depends(get_session)],
    current_user: Annotated[User, Depends(require_roles(["estudiante"]))],
):
    return exam_service.get_exam_state(attempt_id, current_user.id, session)


@router.post("/{attempt_id}/answer")
def submit_answer(
    attempt_id: UUID,
    request: AnswerRequest,
    session: Annotated[Session, Depends(get_session)],
    current_user: Annotated[User, Depends(require_roles(["estudiante"]))],
):
    return exam_service.submit_answer(
        attempt_id=attempt_id,
        orden=request.orden,
        opcion_seleccionada=request.opcion_seleccionada,
        tiempo_agotado=request.tiempo_agotado,
        student_id=current_user.id,
        session=session,
    )


@router.post("/{attempt_id}/finish")
def finish_exam(
    attempt_id: UUID,
    session: Annotated[Session, Depends(get_session)],
    current_user: Annotated[User, Depends(require_roles(["estudiante"]))],
):
    return exam_service.finish_exam(attempt_id, current_user.id, session)


@router.get("/{attempt_id}/results")
def get_results(
    attempt_id: UUID,
    session: Annotated[Session, Depends(get_session)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    # Admin puede ver cualquier intento; estudiante solo los suyos
    student_id = None if current_user.rol == "admin" else current_user.id
    return exam_service.get_results(attempt_id, student_id, session)
