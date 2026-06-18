"""Tests de integración para el módulo de exámenes (US1)."""

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, select

from app.models import ConfiguracionExamen, Pregunta


def create_exam_config(session: Session, num_preguntas: int = 5, porcentaje: float = 70.0) -> ConfiguracionExamen:
    """Crea o actualiza la configuración de examen en la BD de test."""
    config = session.get(ConfiguracionExamen, 1)
    if config is None:
        config = ConfiguracionExamen(
            id=1,
            num_preguntas=num_preguntas,
            segundos_por_pregunta=60,
            porcentaje_aprobacion=porcentaje,
        )
        session.add(config)
    else:
        config.num_preguntas = num_preguntas
        config.porcentaje_aprobacion = porcentaje
        session.add(config)
    session.commit()
    session.refresh(config)
    return config


def create_preguntas(session: Session, count: int = 5) -> list[Pregunta]:
    """Crea preguntas de prueba en la BD."""
    preguntas = []
    for i in range(1, count + 1):
        pregunta = Pregunta(
            tema=f"Tema {i}",
            pregunta=f"¿Pregunta de prueba número {i}?",
            opcion_a="Opción A",
            opcion_b="Opción B",
            opcion_c="Opción C",
            opcion_d="Opción D",
            respuesta_correcta="A",
            activa=True,
        )
        session.add(pregunta)
    session.commit()
    # Obtener con IDs asignados
    preguntas = session.exec(select(Pregunta)).all()
    return list(preguntas)


class TestStartExam:
    def test_start_exam_success(
        self,
        client: TestClient,
        session: Session,
        estudiante_token: str,
    ):
        """201: inicio exitoso con config válida y suficientes preguntas."""
        create_exam_config(session, num_preguntas=3)
        create_preguntas(session, count=5)

        response = client.post(
            "/api/exams/start",
            headers={"Authorization": f"Bearer {estudiante_token}"},
        )

        assert response.status_code == 201
        data = response.json()
        assert "attempt_id" in data
        assert "total_preguntas" in data
        assert data["total_preguntas"] == 3
        assert "segundos_por_pregunta" in data
        assert "pregunta_actual" in data

        pregunta = data["pregunta_actual"]
        assert "orden" in pregunta
        assert pregunta["orden"] == 1
        assert "id" in pregunta
        assert "pregunta" in pregunta
        assert "opciones" in pregunta
        opciones = pregunta["opciones"]
        assert set(opciones.keys()) == {"A", "B", "C", "D"}
        # Verificar que respuesta_correcta NO está expuesta durante el examen
        assert "respuesta_correcta" not in pregunta
        assert "fundamento_juridico" not in pregunta


class TestStartExamNoConfig:
    def test_start_exam_no_config(
        self,
        client: TestClient,
        session: Session,
        estudiante_token: str,
    ):
        """409: cuando porcentaje_aprobacion es NULL (sistema no configurado)."""
        # Asegurarse de que la config tiene porcentaje_aprobacion = NULL
        config = session.get(ConfiguracionExamen, 1)
        if config is None:
            config = ConfiguracionExamen(
                id=1,
                num_preguntas=5,
                segundos_por_pregunta=60,
                porcentaje_aprobacion=None,
            )
            session.add(config)
            session.commit()
        else:
            config.porcentaje_aprobacion = None
            session.add(config)
            session.commit()

        response = client.post(
            "/api/exams/start",
            headers={"Authorization": f"Bearer {estudiante_token}"},
        )

        assert response.status_code == 409

    def test_start_exam_insufficient_questions(
        self,
        client: TestClient,
        session: Session,
        estudiante_token: str,
    ):
        """409: cuando hay menos preguntas activas que num_preguntas en config."""
        create_exam_config(session, num_preguntas=10)
        # Solo creamos 2 preguntas, pero la config requiere 10
        create_preguntas(session, count=2)

        response = client.post(
            "/api/exams/start",
            headers={"Authorization": f"Bearer {estudiante_token}"},
        )

        assert response.status_code == 409


class TestAnswerQuestion:
    def _start_exam(self, client: TestClient, token: str, session: Session) -> str:
        """Helper: inicia un examen y retorna el attempt_id."""
        create_exam_config(session, num_preguntas=3)
        create_preguntas(session, count=5)
        response = client.post(
            "/api/exams/start",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 201
        return response.json()["attempt_id"]

    def test_answer_question_correct(
        self,
        client: TestClient,
        session: Session,
        estudiante_token: str,
    ):
        """Respuesta correcta (opcion A = respuesta_correcta) es aceptada y avanza al orden 2.
        La verificación de es_correcta=True se realiza vía /results en T037."""
        attempt_id = self._start_exam(client, estudiante_token, session)

        response = client.post(
            f"/api/exams/{attempt_id}/answer",
            headers={"Authorization": f"Bearer {estudiante_token}"},
            json={"orden": 1, "opcion_seleccionada": "A", "tiempo_agotado": False},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["orden_respondido"] == 1
        assert data["siguiente_pregunta"] is not None
        assert data["siguiente_pregunta"]["orden"] == 2

    def test_answer_timeout(
        self,
        client: TestClient,
        session: Session,
        estudiante_token: str,
    ):
        """Tiempo agotado se registra correctamente (opcion_seleccionada=null)."""
        attempt_id = self._start_exam(client, estudiante_token, session)

        response = client.post(
            f"/api/exams/{attempt_id}/answer",
            headers={"Authorization": f"Bearer {estudiante_token}"},
            json={"orden": 1, "opcion_seleccionada": None, "tiempo_agotado": True},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["orden_respondido"] == 1
        # siguiente pregunta disponible (no era la última)
        assert data["siguiente_pregunta"] is not None


class TestGetResults:
    def _complete_exam(self, client: TestClient, token: str, session: Session) -> str:
        """Helper: completa un examen de 3 preguntas y retorna el attempt_id."""
        create_exam_config(session, num_preguntas=3)
        create_preguntas(session, count=5)

        start_resp = client.post(
            "/api/exams/start",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert start_resp.status_code == 201
        attempt_id = start_resp.json()["attempt_id"]

        # Responder 3 preguntas (todas con opción A)
        for orden in range(1, 4):
            resp = client.post(
                f"/api/exams/{attempt_id}/answer",
                headers={"Authorization": f"Bearer {token}"},
                json={"orden": orden, "opcion_seleccionada": "A", "tiempo_agotado": False},
            )
            assert resp.status_code == 200

        return attempt_id

    def test_get_results_after_finish(
        self,
        client: TestClient,
        session: Session,
        estudiante_token: str,
    ):
        """Los resultados incluyen respuesta_correcta y fundamento_juridico por pregunta."""
        attempt_id = self._complete_exam(client, estudiante_token, session)

        response = client.get(
            f"/api/exams/{attempt_id}/results",
            headers={"Authorization": f"Bearer {estudiante_token}"},
        )

        assert response.status_code == 200
        data = response.json()
        assert "attempt_id" in data
        assert "puntuacion" in data
        assert "resultado" in data
        assert data["resultado"] in ("aprobado", "reprobado")
        assert "preguntas" in data
        assert len(data["preguntas"]) == 3

        # Verificar estructura de cada pregunta en resultados
        primera = data["preguntas"][0]
        assert "respuesta_correcta" in primera  # visible en resultados
        assert "es_correcta" in primera
        assert "tiempo_agotado" in primera
        # fundamento_juridico puede ser None si no fue configurado, pero el campo debe existir
        assert "fundamento_juridico" in primera
