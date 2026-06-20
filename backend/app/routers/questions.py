"""Router for question bank management (T071)."""

from typing import Annotated, Optional

from fastapi import APIRouter, Depends, File, Query, UploadFile, status
from pydantic import BaseModel
from sqlmodel import Session

from app.core.database import get_session
from app.core.dependencies import require_roles
from app.services import question_service

router = APIRouter()

_admin_or_editor = require_roles(["admin", "editor"])


# ---------------------------------------------------------------------------
# Pydantic schemas
# ---------------------------------------------------------------------------

class QuestionCreate(BaseModel):
    tema: str
    pregunta: str
    opcion_a: str
    opcion_b: str
    opcion_c: str
    opcion_d: str
    respuesta_correcta: str
    imagen_archivo: Optional[str] = None
    descripcion_imagen: Optional[str] = None
    fundamento_juridico: Optional[str] = None
    activa: bool = True


class QuestionUpdate(BaseModel):
    tema: Optional[str] = None
    pregunta: Optional[str] = None
    opcion_a: Optional[str] = None
    opcion_b: Optional[str] = None
    opcion_c: Optional[str] = None
    opcion_d: Optional[str] = None
    respuesta_correcta: Optional[str] = None
    imagen_archivo: Optional[str] = None
    descripcion_imagen: Optional[str] = None
    fundamento_juridico: Optional[str] = None
    activa: Optional[bool] = None


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@router.get("/temas")
def list_temas(
    session: Annotated[Session, Depends(get_session)],
    _current_user=Depends(_admin_or_editor),
):
    """GET /temas — returns sorted list of distinct tema values."""
    temas = question_service.list_temas(session)
    return {"temas": temas}


@router.get("/")
def list_questions(
    session: Annotated[Session, Depends(get_session)],
    _current_user=Depends(_admin_or_editor),
    tema: Optional[str] = Query(default=None),
    activa: Optional[bool] = Query(default=True),
    q: Optional[str] = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
):
    """GET / — paginated list + temas_disponibles."""
    return question_service.list_questions(tema, activa, q, page, page_size, session)


@router.post("/", status_code=status.HTTP_201_CREATED)
def create_question(
    data: QuestionCreate,
    session: Annotated[Session, Depends(get_session)],
    _current_user=Depends(_admin_or_editor),
):
    """POST / — create a new question."""
    return question_service.create_question(data.model_dump(), session)


@router.get("/{question_id}")
def get_question(
    question_id: int,
    session: Annotated[Session, Depends(get_session)],
    _current_user=Depends(_admin_or_editor),
):
    """GET /{id} — fetch single question by id."""
    return question_service.get_question(question_id, session)


@router.put("/{question_id}")
def update_question(
    question_id: int,
    data: QuestionUpdate,
    session: Annotated[Session, Depends(get_session)],
    _current_user=Depends(_admin_or_editor),
):
    """PUT /{id} — partial update of a question."""
    return question_service.update_question(
        question_id, data.model_dump(exclude_unset=True), session
    )


@router.delete("/{question_id}", status_code=status.HTTP_204_NO_CONTENT)
def soft_delete_question(
    question_id: int,
    session: Annotated[Session, Depends(get_session)],
    _current_user=Depends(_admin_or_editor),
):
    """DELETE /{id} — soft-delete (sets activa=False)."""
    question_service.soft_delete(question_id, session)


@router.post("/import")
def import_csv(
    file: Annotated[UploadFile, File(...)],
    session: Annotated[Session, Depends(get_session)],
    _current_user=Depends(_admin_or_editor),
):
    """POST /import — multipart CSV upload, upserts questions."""
    file_content = file.file.read()
    return question_service.import_csv(file_content, session)
