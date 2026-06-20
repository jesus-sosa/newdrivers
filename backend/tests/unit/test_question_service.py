"""Unit tests for question_service.py (T101)."""

import io
import uuid

import pytest
from fastapi import HTTPException

from app.services import question_service
from app.models.pregunta import Pregunta
from app.models.config import ConfiguracionExamen
from app.models.intento import IntentoExamen
from app.models.respuesta import RespuestaIntento


def _make_csv_bytes(rows: list[dict]) -> bytes:
    """Helper: build CSV bytes from a list of row dicts."""
    headers = [
        "tema", "pregunta", "opcion_a", "opcion_b", "opcion_c", "opcion_d",
        "respuesta_correcta", "fundamento_juridico", "imagen_archivo", "descripcion_imagen",
    ]
    buf = io.StringIO()
    buf.write(",".join(headers) + "\n")
    for row in rows:
        buf.write(",".join(row.get(h, "") for h in headers) + "\n")
    return buf.getvalue().encode("utf-8")


class TestImportCsvEncoding:
    """T101a: import_csv correctly handles UTF-8 with Spanish characters."""

    def test_import_csv_utf8_spanish_chars(self, session):
        """CSV with ñ and accented vowels imports without errors."""
        rows = [
            {
                "tema": "Señales de tránsito",
                "pregunta": "¿Qué significa esta señal?",
                "opcion_a": "Precaución",
                "opcion_b": "Prohibición",
                "opcion_c": "Información",
                "opcion_d": "Obligación",
                "respuesta_correcta": "A",
                "fundamento_juridico": "Artículo 1º",
                "imagen_archivo": "",
                "descripcion_imagen": "",
            },
            {
                "tema": "Velocidades máximas",
                "pregunta": "¿Cuál es la velocidad máxima en vías urbanas?",
                "opcion_a": "40 km/h",
                "opcion_b": "60 km/h",
                "opcion_c": "80 km/h",
                "opcion_d": "100 km/h",
                "respuesta_correcta": "B",
                "fundamento_juridico": "",
                "imagen_archivo": "",
                "descripcion_imagen": "",
            },
        ]
        csv_bytes = _make_csv_bytes(rows)

        result = question_service.import_csv(csv_bytes, session)

        assert result["insertadas"] > 0
        assert result["errores"] == []


class TestSoftDeleteBlockedWhenActiveAttempt:
    """T101b: soft_delete raises 409 when an active exam attempt references the question."""

    def test_soft_delete_blocked_when_active_attempt(self, session):
        """Active (non-finalized) attempt referencing a question → 409 on soft_delete."""
        # Create a question
        from datetime import datetime, timezone
        now = datetime.now(timezone.utc)
        pregunta = Pregunta(
            tema="Test",
            pregunta="¿Pregunta de prueba?",
            opcion_a="A",
            opcion_b="B",
            opcion_c="C",
            opcion_d="D",
            respuesta_correcta="A",
            activa=True,
            created_at=now,
            updated_at=now,
        )
        session.add(pregunta)
        session.commit()
        session.refresh(pregunta)

        # Create a student user to satisfy FK constraint on IntentoExamen
        from app.models.user import User
        from app.core.security import hash_password
        student = User(
            nombre_completo="Test Student",
            email="sofdelete_test@example.com",
            password_hash=hash_password("Test1234!"),
            rol="estudiante",
            activo=True,
        )
        session.add(student)
        session.commit()
        session.refresh(student)

        # Create an active (non-finalized) exam attempt
        intento = IntentoExamen(
            estudiante_id=student.id,
            num_preguntas=1,
            porcentaje_aprobacion=70.0,
            segundos_por_pregunta=60,
            finalizado_at=None,  # active attempt
        )
        session.add(intento)
        session.commit()
        session.refresh(intento)

        # Link the question to the attempt via RespuestaIntento
        respuesta = RespuestaIntento(
            intento_id=intento.id,
            pregunta_id=pregunta.id,
            orden=1,
        )
        session.add(respuesta)
        session.commit()

        # soft_delete should raise 409
        with pytest.raises(HTTPException) as exc_info:
            question_service.soft_delete(pregunta.id, session)

        assert exc_info.value.status_code == 409
