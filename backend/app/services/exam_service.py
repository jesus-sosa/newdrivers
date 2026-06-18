import random
from datetime import datetime, timezone
from uuid import UUID

from fastapi import HTTPException, status
from sqlmodel import Session, select

from app.models.config import ConfiguracionExamen
from app.models.intento import IntentoExamen
from app.models.pregunta import Pregunta
from app.models.respuesta import RespuestaIntento
from app.models.user import User


# ---------------------------------------------------------------------------
# Helpers privados (también usados en tests unitarios)
# ---------------------------------------------------------------------------

def _shuffle_preguntas(preguntas: list[Pregunta], count: int) -> list[Pregunta]:
    """Fisher-Yates shuffle — selecciona `count` preguntas sin repetición."""
    pool = list(preguntas)
    random.shuffle(pool)
    return pool[:count]


def _calculate_result(correctas: int, total: int, porcentaje_aprobacion: float) -> dict:
    """Calcula puntuación y resultado. Maneja total=0 sin ZeroDivisionError."""
    porcentaje_obtenido = round((correctas / total * 100), 2) if total > 0 else 0.0
    resultado = "aprobado" if porcentaje_obtenido >= porcentaje_aprobacion else "reprobado"
    return {
        "puntuacion": correctas,
        "total_preguntas": total,
        "porcentaje_obtenido": porcentaje_obtenido,
        "porcentaje_aprobacion": porcentaje_aprobacion,
        "resultado": resultado,
    }


def _get_config(session: Session) -> ConfiguracionExamen:
    """Obtiene la configuración singleton (id=1). Lanza 409 si no existe."""
    config = session.get(ConfiguracionExamen, 1)
    if config is None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Sistema no configurado. Contacta al administrador.",
        )
    return config


def _build_pregunta_response(pregunta: Pregunta, orden: int, include_answer: bool = False) -> dict:
    """Serializa una Pregunta para la respuesta de la API.

    Durante el examen, omite respuesta_correcta y fundamento_juridico.
    En resultados, los incluye.
    """
    data: dict = {
        "orden": orden,
        "id": pregunta.id,
        "tema": pregunta.tema,
        "pregunta": pregunta.pregunta,
        "imagen_archivo": pregunta.imagen_archivo,
        "descripcion_imagen": pregunta.descripcion_imagen,
        "opciones": {
            "A": pregunta.opcion_a,
            "B": pregunta.opcion_b,
            "C": pregunta.opcion_c,
            "D": pregunta.opcion_d,
        },
    }
    if include_answer:
        data["respuesta_correcta"] = pregunta.respuesta_correcta
        data["fundamento_juridico"] = pregunta.fundamento_juridico
    return data


# ---------------------------------------------------------------------------
# Servicio público
# ---------------------------------------------------------------------------

def start_exam(student_id: UUID, session: Session) -> dict:
    """Inicia un nuevo intento de examen para el estudiante."""
    config = _get_config(session)

    # Validación 1: porcentaje_aprobacion debe estar configurado
    if config.porcentaje_aprobacion is None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="El porcentaje de aprobación no ha sido configurado.",
        )

    # Validación 2: suficientes preguntas activas
    preguntas_activas = session.exec(
        select(Pregunta).where(Pregunta.activa == True)  # noqa: E712
    ).all()

    if len(preguntas_activas) < config.num_preguntas:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                f"Banco de preguntas insuficiente. "
                f"Se requieren {config.num_preguntas}, "
                f"hay {len(preguntas_activas)} activas."
            ),
        )

    # Selección aleatoria de preguntas (Fisher-Yates)
    seleccionadas = _shuffle_preguntas(list(preguntas_activas), config.num_preguntas)

    # Crear intento (snapshot de config en el momento del inicio)
    intento = IntentoExamen(
        estudiante_id=student_id,
        num_preguntas=config.num_preguntas,
        porcentaje_aprobacion=config.porcentaje_aprobacion,
        segundos_por_pregunta=config.segundos_por_pregunta,
    )
    session.add(intento)
    session.flush()  # obtiene intento.id sin commit completo

    # Crear filas de respuesta (una por pregunta, en orden)
    for i, pregunta in enumerate(seleccionadas, start=1):
        respuesta = RespuestaIntento(
            intento_id=intento.id,
            pregunta_id=pregunta.id,
            orden=i,
        )
        session.add(respuesta)

    session.commit()
    session.refresh(intento)

    # Primera pregunta (orden=1)
    primera_respuesta = session.exec(
        select(RespuestaIntento).where(
            RespuestaIntento.intento_id == intento.id,
            RespuestaIntento.orden == 1,
        )
    ).first()
    primera_pregunta = session.get(Pregunta, primera_respuesta.pregunta_id)

    return {
        "attempt_id": str(intento.id),
        "total_preguntas": intento.num_preguntas,
        "segundos_por_pregunta": intento.segundos_por_pregunta,
        "pregunta_actual": _build_pregunta_response(primera_pregunta, orden=1),
    }


def get_exam_state(attempt_id: UUID, student_id: UUID, session: Session) -> dict:
    """Recupera el estado actual del examen (reconexión)."""
    intento = session.get(IntentoExamen, attempt_id)
    if intento is None or intento.estudiante_id != student_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Intento no encontrado.",
        )

    respondidas = session.exec(
        select(RespuestaIntento).where(
            RespuestaIntento.intento_id == attempt_id,
            RespuestaIntento.respondida_at.is_not(None),  # type: ignore[union-attr]
        )
    ).all()
    count_respondidas = len(respondidas)

    if intento.finalizado_at is not None:
        return {
            "attempt_id": str(intento.id),
            "total_preguntas": intento.num_preguntas,
            "segundos_por_pregunta": intento.segundos_por_pregunta,
            "respondidas": count_respondidas,
            "estado": "finalizado",
            "pregunta_actual": None,
        }

    # Buscar siguiente pregunta pendiente
    siguiente_respuesta = session.exec(
        select(RespuestaIntento)
        .where(
            RespuestaIntento.intento_id == attempt_id,
            RespuestaIntento.respondida_at.is_(None),  # type: ignore[union-attr]
        )
        .order_by(RespuestaIntento.orden)
    ).first()

    pregunta_actual = None
    if siguiente_respuesta:
        pregunta = session.get(Pregunta, siguiente_respuesta.pregunta_id)
        pregunta_actual = _build_pregunta_response(pregunta, siguiente_respuesta.orden)

    return {
        "attempt_id": str(intento.id),
        "total_preguntas": intento.num_preguntas,
        "segundos_por_pregunta": intento.segundos_por_pregunta,
        "respondidas": count_respondidas,
        "estado": "en_curso",
        "pregunta_actual": pregunta_actual,
    }


def submit_answer(
    attempt_id: UUID,
    orden: int,
    opcion_seleccionada: str | None,
    tiempo_agotado: bool,
    student_id: UUID,
    session: Session,
) -> dict:
    """Registra la respuesta del estudiante para la pregunta actual."""
    intento = session.get(IntentoExamen, attempt_id)
    if intento is None or intento.estudiante_id != student_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Intento no encontrado.",
        )

    if intento.finalizado_at is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="El intento ya está finalizado.",
        )

    # Validar opción
    if opcion_seleccionada is not None and opcion_seleccionada.upper() not in ("A", "B", "C", "D"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="opcion_seleccionada debe ser A, B, C o D (o null para tiempo agotado).",
        )

    # Buscar la respuesta pendiente con ese orden
    respuesta = session.exec(
        select(RespuestaIntento).where(
            RespuestaIntento.intento_id == attempt_id,
            RespuestaIntento.orden == orden,
        )
    ).first()

    if respuesta is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"No hay pregunta pendiente con orden {orden}.",
        )

    if respuesta.respondida_at is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"La pregunta con orden {orden} ya fue respondida.",
        )

    # Verificar si es la siguiente pendiente en orden
    primera_pendiente = session.exec(
        select(RespuestaIntento)
        .where(
            RespuestaIntento.intento_id == attempt_id,
            RespuestaIntento.respondida_at.is_(None),  # type: ignore[union-attr]
        )
        .order_by(RespuestaIntento.orden)
    ).first()

    if primera_pendiente is None or primera_pendiente.orden != orden:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"El orden {orden} no corresponde a la siguiente pregunta pendiente.",
        )

    # Obtener la pregunta para evaluar correctitud
    pregunta = session.get(Pregunta, respuesta.pregunta_id)
    es_correcta = (
        opcion_seleccionada is not None
        and opcion_seleccionada.upper() == pregunta.respuesta_correcta.upper()
    )

    # Registrar respuesta
    respuesta.opcion_seleccionada = opcion_seleccionada.upper() if opcion_seleccionada else None
    respuesta.es_correcta = es_correcta
    respuesta.tiempo_agotado = tiempo_agotado
    respuesta.respondida_at = datetime.now(timezone.utc)
    session.add(respuesta)
    session.commit()

    # Buscar siguiente pregunta pendiente
    siguiente = session.exec(
        select(RespuestaIntento)
        .where(
            RespuestaIntento.intento_id == attempt_id,
            RespuestaIntento.respondida_at.is_(None),  # type: ignore[union-attr]
        )
        .order_by(RespuestaIntento.orden)
    ).first()

    if siguiente is None:
        # Era la última — finalizar automáticamente
        result = _finish_and_score(intento, attempt_id, session)
        return {
            "orden_respondido": orden,
            "siguiente_pregunta": None,
            "examen_finalizado": True,
            "resumen": result,
        }

    siguiente_pregunta_obj = session.get(Pregunta, siguiente.pregunta_id)
    return {
        "orden_respondido": orden,
        "siguiente_pregunta": _build_pregunta_response(siguiente_pregunta_obj, siguiente.orden),
    }


def _finish_and_score(intento: IntentoExamen, attempt_id: UUID, session: Session) -> dict:
    """Calcula el puntaje y finaliza el intento."""
    todas = session.exec(
        select(RespuestaIntento).where(RespuestaIntento.intento_id == attempt_id)
    ).all()

    correctas = sum(1 for r in todas if r.es_correcta is True)
    total = intento.num_preguntas

    calc = _calculate_result(correctas, total, intento.porcentaje_aprobacion)

    intento.puntuacion = correctas
    intento.resultado = calc["resultado"]
    intento.finalizado_at = datetime.now(timezone.utc)
    session.add(intento)
    session.commit()
    session.refresh(intento)

    return {
        "attempt_id": str(intento.id),
        **calc,
    }


def finish_exam(attempt_id: UUID, student_id: UUID, session: Session) -> dict:
    """Finaliza manualmente el examen. Las preguntas pendientes se marcan sin responder."""
    intento = session.get(IntentoExamen, attempt_id)
    if intento is None or intento.estudiante_id != student_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Intento no encontrado.",
        )

    if intento.finalizado_at is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="El intento ya está finalizado.",
        )

    # Marcar preguntas pendientes como no respondidas (tiempo_agotado=False, es_correcta=False)
    pendientes = session.exec(
        select(RespuestaIntento).where(
            RespuestaIntento.intento_id == attempt_id,
            RespuestaIntento.respondida_at.is_(None),  # type: ignore[union-attr]
        )
    ).all()

    now = datetime.now(timezone.utc)
    for resp in pendientes:
        resp.es_correcta = False
        resp.tiempo_agotado = False
        resp.respondida_at = now
        session.add(resp)

    session.commit()

    return _finish_and_score(intento, attempt_id, session)


def get_results(attempt_id: UUID, student_id: UUID | None, session: Session) -> dict:
    """Retorna resultados completos de un intento finalizado.

    student_id=None significa que la llamada es de un admin (sin restricción de propietario).
    """
    intento = session.get(IntentoExamen, attempt_id)
    if intento is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Intento no encontrado.",
        )

    # Verificar propiedad (si no es admin)
    if student_id is not None and intento.estudiante_id != student_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Intento no encontrado.",
        )

    if intento.finalizado_at is None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="El intento aún no ha finalizado.",
        )

    respuestas = session.exec(
        select(RespuestaIntento)
        .where(RespuestaIntento.intento_id == attempt_id)
        .order_by(RespuestaIntento.orden)
    ).all()

    preguntas_data = []
    for respuesta in respuestas:
        pregunta = session.get(Pregunta, respuesta.pregunta_id)
        pregunta_dict = _build_pregunta_response(pregunta, respuesta.orden, include_answer=True)
        pregunta_dict["opcion_seleccionada"] = respuesta.opcion_seleccionada
        pregunta_dict["es_correcta"] = respuesta.es_correcta
        pregunta_dict["tiempo_agotado"] = respuesta.tiempo_agotado
        preguntas_data.append(pregunta_dict)

    return {
        "attempt_id": str(intento.id),
        "iniciado_at": intento.iniciado_at.isoformat(),
        "finalizado_at": intento.finalizado_at.isoformat(),
        "puntuacion": intento.puntuacion,
        "total_preguntas": intento.num_preguntas,
        "porcentaje_obtenido": round(
            (intento.puntuacion / intento.num_preguntas * 100), 2
        ) if intento.num_preguntas > 0 else 0.0,
        "porcentaje_aprobacion": intento.porcentaje_aprobacion,
        "resultado": intento.resultado,
        "preguntas": preguntas_data,
    }


def get_history(student_id: UUID, page: int, page_size: int, session: Session) -> dict:
    """Retorna el historial paginado de intentos del estudiante."""
    all_intentos = session.exec(
        select(IntentoExamen)
        .where(IntentoExamen.estudiante_id == student_id)
        .order_by(IntentoExamen.iniciado_at.desc())  # type: ignore[union-attr]
    ).all()

    total = len(all_intentos)
    offset = (page - 1) * page_size
    page_items = all_intentos[offset : offset + page_size]

    items = []
    for intento in page_items:
        items.append({
            "attempt_id": str(intento.id),
            "iniciado_at": intento.iniciado_at.isoformat(),
            "finalizado_at": intento.finalizado_at.isoformat() if intento.finalizado_at else None,
            "puntuacion": intento.puntuacion,
            "total_preguntas": intento.num_preguntas,
            "resultado": intento.resultado,
        })

    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "items": items,
    }
