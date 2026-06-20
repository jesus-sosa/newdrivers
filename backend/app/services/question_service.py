"""Service layer for question bank management (T070)."""

import csv
import io
from datetime import datetime, timezone
from typing import Optional

from fastapi import HTTPException, status
from sqlmodel import Session, select

from app.models.intento import IntentoExamen
from app.models.pregunta import Pregunta
from app.models.respuesta import RespuestaIntento


_VALID_ANSWERS = {"A", "B", "C", "D"}


def _has_active_attempt_for_question(question_id: int, session: Session) -> bool:
    """Return True if any active (non-finalizado) exam attempt references this question."""
    active_intento = session.exec(
        select(IntentoExamen)
        .join(RespuestaIntento, RespuestaIntento.intento_id == IntentoExamen.id)
        .where(
            RespuestaIntento.pregunta_id == question_id,
            IntentoExamen.finalizado_at.is_(None),  # type: ignore[union-attr]
        )
    ).first()
    return active_intento is not None


def list_questions(
    tema: Optional[str],
    activa: Optional[bool],
    q: Optional[str],
    page: int,
    page_size: int,
    session: Session,
) -> dict:
    """Return paginated list of questions plus available temas."""
    statement = select(Pregunta)

    if tema is not None:
        statement = statement.where(Pregunta.tema == tema)
    if activa is not None:
        statement = statement.where(Pregunta.activa == activa)
    if q is not None:
        statement = statement.where(Pregunta.pregunta.contains(q))  # type: ignore[union-attr]

    all_results = session.exec(statement).all()
    total = len(all_results)

    offset = (page - 1) * page_size
    items = all_results[offset : offset + page_size]

    temas_disponibles = sorted(
        {p.tema for p in session.exec(select(Pregunta)).all()}
    )

    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "items": [_pregunta_to_dict(p) for p in items],
        "temas_disponibles": temas_disponibles,
    }


def create_question(data: dict, session: Session) -> dict:
    """Create a new Pregunta. Raises 400 if respuesta_correcta is invalid."""
    respuesta = data.get("respuesta_correcta", "")
    if str(respuesta).upper() not in _VALID_ANSWERS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="respuesta_correcta debe ser A, B, C o D.",
        )

    now = datetime.now(timezone.utc)
    pregunta = Pregunta(
        tema=data["tema"],
        pregunta=data["pregunta"],
        opcion_a=data["opcion_a"],
        opcion_b=data["opcion_b"],
        opcion_c=data["opcion_c"],
        opcion_d=data["opcion_d"],
        respuesta_correcta=str(respuesta).upper(),
        imagen_archivo=data.get("imagen_archivo"),
        descripcion_imagen=data.get("descripcion_imagen"),
        fundamento_juridico=data.get("fundamento_juridico"),
        activa=data.get("activa", True),
        created_at=now,
        updated_at=now,
    )
    session.add(pregunta)
    session.commit()
    session.refresh(pregunta)
    return _pregunta_to_dict(pregunta)


def get_question(question_id: int, session: Session) -> dict:
    """Return Pregunta by id or raise 404."""
    pregunta = session.get(Pregunta, question_id)
    if pregunta is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Pregunta {question_id} no encontrada.",
        )
    return _pregunta_to_dict(pregunta)


def update_question(question_id: int, data: dict, session: Session) -> dict:
    """Partial update of a question.

    If respuesta_correcta is being changed, verifies no active exam attempt
    references this question (active = finalizado_at IS NULL).
    Raises 409 if active attempt found.
    """
    pregunta = session.get(Pregunta, question_id)
    if pregunta is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Pregunta {question_id} no encontrada.",
        )

    # Validate respuesta_correcta if provided
    if "respuesta_correcta" in data and data["respuesta_correcta"] is not None:
        new_answer = str(data["respuesta_correcta"]).upper()
        if new_answer not in _VALID_ANSWERS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="respuesta_correcta debe ser A, B, C o D.",
            )
        # Check for active attempts if the answer is actually changing
        if new_answer != pregunta.respuesta_correcta.upper():
            if _has_active_attempt_for_question(question_id, session):
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=(
                        "No se puede modificar la respuesta correcta: "
                        "hay intentos de examen activos que referencian esta pregunta."
                    ),
                )
        data = {**data, "respuesta_correcta": new_answer}

    updatable_fields = {
        "tema", "pregunta", "opcion_a", "opcion_b", "opcion_c", "opcion_d",
        "respuesta_correcta", "imagen_archivo", "descripcion_imagen",
        "fundamento_juridico", "activa",
    }
    for field, value in data.items():
        if field in updatable_fields:
            setattr(pregunta, field, value)

    pregunta.updated_at = datetime.now(timezone.utc)
    session.add(pregunta)
    session.commit()
    session.refresh(pregunta)
    return _pregunta_to_dict(pregunta)


def soft_delete(question_id: int, session: Session) -> None:
    """Set activa=False. Raises 404 if not found; 409 if active attempt references it."""
    pregunta = session.get(Pregunta, question_id)
    if pregunta is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Pregunta {question_id} no encontrada.",
        )

    if _has_active_attempt_for_question(question_id, session):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "No se puede desactivar la pregunta: "
                "hay intentos de examen activos que la referencian."
            ),
        )

    pregunta.activa = False
    pregunta.updated_at = datetime.now(timezone.utc)
    session.add(pregunta)
    session.commit()


def import_csv(file_content: bytes, session: Session) -> dict:
    """Parse CSV and upsert questions. Returns insertadas/actualizadas/errores."""
    text = file_content.decode("utf-8")
    reader = csv.DictReader(io.StringIO(text))

    insertadas = 0
    actualizadas = 0
    errores: list[dict] = []

    for row_number, row in enumerate(reader, start=2):  # start=2: row 1 is header
        respuesta = row.get("respuesta_correcta", "").strip().upper()
        if respuesta not in _VALID_ANSWERS:
            errores.append({
                "fila": row_number,
                "error": f"respuesta_correcta inválida: '{row.get('respuesta_correcta', '')}'",
            })
            continue

        # Required fields check
        required = ["tema", "pregunta", "opcion_a", "opcion_b", "opcion_c", "opcion_d"]
        missing = [f for f in required if not row.get(f, "").strip()]
        if missing:
            errores.append({
                "fila": row_number,
                "error": f"Campos requeridos vacíos: {', '.join(missing)}",
            })
            continue

        row_id_str = row.get("id", "").strip()
        existing: Optional[Pregunta] = None

        if row_id_str:
            try:
                row_id = int(row_id_str)
                existing = session.get(Pregunta, row_id)
            except ValueError:
                errores.append({
                    "fila": row_number,
                    "error": f"id inválido: '{row_id_str}'",
                })
                continue

        now = datetime.now(timezone.utc)

        if existing is not None:
            # Update existing
            existing.tema = row["tema"].strip()
            existing.pregunta = row["pregunta"].strip()
            existing.opcion_a = row["opcion_a"].strip()
            existing.opcion_b = row["opcion_b"].strip()
            existing.opcion_c = row["opcion_c"].strip()
            existing.opcion_d = row["opcion_d"].strip()
            existing.respuesta_correcta = respuesta
            existing.fundamento_juridico = row.get("fundamento_juridico", "").strip() or None
            existing.imagen_archivo = row.get("imagen_archivo", "").strip() or None
            existing.descripcion_imagen = row.get("descripcion_imagen", "").strip() or None
            existing.updated_at = now
            session.add(existing)
            actualizadas += 1
        else:
            # Insert new
            pregunta = Pregunta(
                tema=row["tema"].strip(),
                pregunta=row["pregunta"].strip(),
                opcion_a=row["opcion_a"].strip(),
                opcion_b=row["opcion_b"].strip(),
                opcion_c=row["opcion_c"].strip(),
                opcion_d=row["opcion_d"].strip(),
                respuesta_correcta=respuesta,
                fundamento_juridico=row.get("fundamento_juridico", "").strip() or None,
                imagen_archivo=row.get("imagen_archivo", "").strip() or None,
                descripcion_imagen=row.get("descripcion_imagen", "").strip() or None,
                activa=True,
                created_at=now,
                updated_at=now,
            )
            session.add(pregunta)
            insertadas += 1

    session.commit()
    return {"insertadas": insertadas, "actualizadas": actualizadas, "errores": errores}


def list_temas(session: Session) -> list[str]:
    """Return sorted list of distinct tema values."""
    preguntas = session.exec(select(Pregunta)).all()
    return sorted({p.tema for p in preguntas})


def _pregunta_to_dict(p: Pregunta) -> dict:
    """Serialize a Pregunta to a plain dict."""
    return {
        "id": p.id,
        "tema": p.tema,
        "pregunta": p.pregunta,
        "imagen_archivo": p.imagen_archivo,
        "descripcion_imagen": p.descripcion_imagen,
        "opcion_a": p.opcion_a,
        "opcion_b": p.opcion_b,
        "opcion_c": p.opcion_c,
        "opcion_d": p.opcion_d,
        "respuesta_correcta": p.respuesta_correcta,
        "fundamento_juridico": p.fundamento_juridico,
        "activa": p.activa,
        "created_at": p.created_at.isoformat() if p.created_at else None,
        "updated_at": p.updated_at.isoformat() if p.updated_at else None,
    }
