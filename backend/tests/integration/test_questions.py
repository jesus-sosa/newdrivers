"""Integration tests for /api/questions endpoints (T065–T068).

These tests target the contract that will be implemented in T070–T071.
They will FAIL with 404 until the router is wired into app.main, which is
expected and intentional.
"""

import io

import pytest
from fastapi.testclient import TestClient

from app.models import Pregunta


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_pregunta(**overrides) -> dict:
    """Return a minimal valid Pregunta payload dict, allowing field overrides."""
    base = {
        "tema": "Señales",
        "pregunta": "¿Qué indica la señal de STOP?",
        "opcion_a": "Detenerse completamente",
        "opcion_b": "Ceder el paso",
        "opcion_c": "Girar a la derecha",
        "opcion_d": "Acelerar",
        "respuesta_correcta": "A",
    }
    base.update(overrides)
    return base


def _seed_preguntas(session, preguntas: list[dict]) -> list[Pregunta]:
    """Insert Pregunta rows directly via session and return them."""
    created = []
    for data in preguntas:
        p = Pregunta(**data)
        session.add(p)
    session.commit()
    for p in session.exec(  # type: ignore[attr-defined]
        __import__("sqlmodel").select(Pregunta)
    ).all():
        created.append(p)
    return created


# ---------------------------------------------------------------------------
# T065 — List with filters and pagination
# ---------------------------------------------------------------------------

class TestListQuestionsWithFilters:
    """T065: GET /api/questions supports pagination and filters."""

    def test_pagination_returns_page_size_items(self, client: TestClient, session, admin_token: str):
        """With 3 questions in DB, page_size=2 returns 2 items and total>=3."""
        _seed_preguntas(session, [
            _make_pregunta(tema="Señales", pregunta=f"Pregunta {i}") for i in range(3)
        ])

        response = client.get(
            "/api/questions",
            params={"page": 1, "page_size": 2},
            headers={"Authorization": f"Bearer {admin_token}"},
        )

        assert response.status_code == 200
        body = response.json()
        assert len(body["items"]) == 2
        assert body["total"] >= 3
        assert body["page"] == 1
        assert body["page_size"] == 2

    def test_filter_by_tema(self, client: TestClient, session, admin_token: str):
        """?tema=Señales returns only questions matching that tema."""
        _seed_preguntas(session, [
            _make_pregunta(tema="Señales", pregunta="Señal uno"),
            _make_pregunta(tema="Señales", pregunta="Señal dos"),
            _make_pregunta(tema="Velocidad", pregunta="Límite de velocidad"),
        ])

        response = client.get(
            "/api/questions",
            params={"tema": "Señales"},
            headers={"Authorization": f"Bearer {admin_token}"},
        )

        assert response.status_code == 200
        body = response.json()
        assert body["total"] == 2
        for item in body["items"]:
            assert item["tema"] == "Señales"

    def test_filter_by_activa_false(self, client: TestClient, session, admin_token: str):
        """?activa=false returns only inactive questions."""
        _seed_preguntas(session, [
            _make_pregunta(tema="Señales", pregunta="Activa question", activa=True),
            _make_pregunta(tema="Señales", pregunta="Inactiva question", activa=False),
        ])

        response = client.get(
            "/api/questions",
            params={"activa": "false"},
            headers={"Authorization": f"Bearer {admin_token}"},
        )

        assert response.status_code == 200
        body = response.json()
        assert body["total"] >= 1
        for item in body["items"]:
            assert item["activa"] is False

    def test_editor_can_list_questions(self, client: TestClient, session, editor_token: str):
        """Editor role also has read access to the questions list."""
        _seed_preguntas(session, [_make_pregunta()])

        response = client.get(
            "/api/questions",
            headers={"Authorization": f"Bearer {editor_token}"},
        )

        assert response.status_code == 200

    def test_student_cannot_list_questions(self, client: TestClient, session, estudiante_token: str):
        """Student role must be denied access (403)."""
        response = client.get(
            "/api/questions",
            headers={"Authorization": f"Bearer {estudiante_token}"},
        )

        assert response.status_code == 403


# ---------------------------------------------------------------------------
# T066 — Create question validation
# ---------------------------------------------------------------------------

class TestCreateQuestionValidation:
    """T066: POST /api/questions validates required fields."""

    def test_create_question_success(self, client: TestClient, admin_token: str):
        """201 returned when all required fields are provided and respuesta_correcta='B'."""
        payload = _make_pregunta(respuesta_correcta="B")

        response = client.post(
            "/api/questions",
            json=payload,
            headers={"Authorization": f"Bearer {admin_token}"},
        )

        assert response.status_code == 201
        body = response.json()
        assert body["respuesta_correcta"] == "B"
        assert body["tema"] == payload["tema"]
        assert "id" in body

    def test_create_question_invalid_respuesta_correcta(self, client: TestClient, admin_token: str):
        """400 or 422 returned when respuesta_correcta is not A/B/C/D."""
        payload = _make_pregunta(respuesta_correcta="E")

        response = client.post(
            "/api/questions",
            json=payload,
            headers={"Authorization": f"Bearer {admin_token}"},
        )

        assert response.status_code in {400, 422}

    def test_create_question_missing_required_field(self, client: TestClient, admin_token: str):
        """422 returned when a required field (tema) is missing."""
        payload = _make_pregunta()
        del payload["tema"]

        response = client.post(
            "/api/questions",
            json=payload,
            headers={"Authorization": f"Bearer {admin_token}"},
        )

        assert response.status_code == 422


# ---------------------------------------------------------------------------
# T067 — Soft-delete question
# ---------------------------------------------------------------------------

class TestSoftDeleteQuestion:
    """T067: DELETE /api/questions/{id} performs a soft-delete."""

    def test_soft_delete_returns_204(self, client: TestClient, session, admin_token: str):
        """DELETE returns 204 No Content."""
        created = _seed_preguntas(session, [_make_pregunta(activa=True)])
        question_id = created[0].id

        response = client.delete(
            f"/api/questions/{question_id}",
            headers={"Authorization": f"Bearer {admin_token}"},
        )

        assert response.status_code == 204

    def test_soft_deleted_question_absent_from_active_list(
        self, client: TestClient, session, admin_token: str
    ):
        """After soft-delete, question does NOT appear in ?activa=true listing."""
        created = _seed_preguntas(session, [_make_pregunta(activa=True)])
        question_id = created[0].id

        client.delete(
            f"/api/questions/{question_id}",
            headers={"Authorization": f"Bearer {admin_token}"},
        )

        response = client.get(
            "/api/questions",
            params={"activa": "true"},
            headers={"Authorization": f"Bearer {admin_token}"},
        )

        assert response.status_code == 200
        ids = [item["id"] for item in response.json()["items"]]
        assert question_id not in ids

    def test_soft_deleted_question_present_in_inactive_list(
        self, client: TestClient, session, admin_token: str
    ):
        """After soft-delete, question DOES appear in ?activa=false listing."""
        created = _seed_preguntas(session, [_make_pregunta(activa=True)])
        question_id = created[0].id

        client.delete(
            f"/api/questions/{question_id}",
            headers={"Authorization": f"Bearer {admin_token}"},
        )

        response = client.get(
            "/api/questions",
            params={"activa": "false"},
            headers={"Authorization": f"Bearer {admin_token}"},
        )

        assert response.status_code == 200
        ids = [item["id"] for item in response.json()["items"]]
        assert question_id in ids


# ---------------------------------------------------------------------------
# T068 — Import CSV
# ---------------------------------------------------------------------------

class TestImportCsv:
    """T068: POST /api/questions/import processes a CSV upload."""

    _CSV_HEADER = (
        "id,tema,pregunta,opcion_a,opcion_b,opcion_c,opcion_d,"
        "respuesta_correcta,fundamento_juridico,imagen_archivo,descripcion_imagen\n"
    )

    def _build_csv(self, rows: list[dict]) -> bytes:
        lines = [self._CSV_HEADER]
        for r in rows:
            lines.append(
                "{id},{tema},{pregunta},{opcion_a},{opcion_b},{opcion_c},{opcion_d},"
                "{respuesta_correcta},{fundamento_juridico},{imagen_archivo},{descripcion_imagen}\n".format(
                    id=r.get("id", ""),
                    tema=r.get("tema", "Señales"),
                    pregunta=r.get("pregunta", "¿Pregunta?"),
                    opcion_a=r.get("opcion_a", "Opción A"),
                    opcion_b=r.get("opcion_b", "Opción B"),
                    opcion_c=r.get("opcion_c", "Opción C"),
                    opcion_d=r.get("opcion_d", "Opción D"),
                    respuesta_correcta=r.get("respuesta_correcta", "A"),
                    fundamento_juridico=r.get("fundamento_juridico", ""),
                    imagen_archivo=r.get("imagen_archivo", ""),
                    descripcion_imagen=r.get("descripcion_imagen", ""),
                )
            )
        return "".join(lines).encode("utf-8")

    def test_import_csv_returns_counters(self, client: TestClient, admin_token: str):
        """Uploading a valid CSV returns insertadas/actualizadas/errores counters."""
        csv_bytes = self._build_csv([
            {
                "id": "",
                "tema": "Señales",
                "pregunta": "¿Qué es un STOP?",
                "opcion_a": "Detenerse",
                "opcion_b": "Girar",
                "opcion_c": "Acelerar",
                "opcion_d": "Ceder",
                "respuesta_correcta": "A",
            }
        ])

        response = client.post(
            "/api/questions/import",
            files={"file": ("questions.csv", csv_bytes, "text/csv")},
            headers={"Authorization": f"Bearer {admin_token}"},
        )

        assert response.status_code == 200
        body = response.json()
        assert "insertadas" in body
        assert "actualizadas" in body
        assert "errores" in body
        assert isinstance(body["insertadas"], int)
        assert isinstance(body["actualizadas"], int)
        assert isinstance(body["errores"], list)

    def test_import_csv_questions_available_after_import(
        self, client: TestClient, admin_token: str
    ):
        """After import, the new questions appear in GET /api/questions."""
        csv_bytes = self._build_csv([
            {
                "id": "",
                "tema": "Velocidad",
                "pregunta": "¿Cuál es el límite en ciudad?",
                "opcion_a": "50 km/h",
                "opcion_b": "80 km/h",
                "opcion_c": "100 km/h",
                "opcion_d": "120 km/h",
                "respuesta_correcta": "A",
            }
        ])

        import_response = client.post(
            "/api/questions/import",
            files={"file": ("questions.csv", csv_bytes, "text/csv")},
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert import_response.status_code == 200
        assert import_response.json()["insertadas"] >= 1

        list_response = client.get(
            "/api/questions",
            params={"tema": "Velocidad"},
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert list_response.status_code == 200
        assert list_response.json()["total"] >= 1

    def test_import_csv_with_invalid_rows_reports_errors(
        self, client: TestClient, admin_token: str
    ):
        """A CSV row with invalid respuesta_correcta ends up in errores list."""
        csv_bytes = self._build_csv([
            {
                "id": "",
                "tema": "Señales",
                "pregunta": "Fila inválida",
                "opcion_a": "A",
                "opcion_b": "B",
                "opcion_c": "C",
                "opcion_d": "D",
                "respuesta_correcta": "Z",  # invalid
            }
        ])

        response = client.post(
            "/api/questions/import",
            files={"file": ("questions.csv", csv_bytes, "text/csv")},
            headers={"Authorization": f"Bearer {admin_token}"},
        )

        assert response.status_code == 200
        body = response.json()
        assert body["errores"] is not None
        assert len(body["errores"]) >= 1
