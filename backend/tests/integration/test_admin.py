"""Integration tests for /api/admin config endpoints (T077–T079) and student management (T084–T086)."""

import uuid

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, select

from app.core.security import hash_password
from app.models import ConfiguracionExamen, Pregunta, User
from app.models.intento import IntentoExamen


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _seed_preguntas(session: Session, count: int, activa: bool = True) -> list[Pregunta]:
    """Insert `count` active Pregunta rows and return them."""
    rows = []
    for i in range(count):
        p = Pregunta(
            tema=f"Tema {i}",
            pregunta=f"Pregunta de prueba número {i}?",
            opcion_a="Opción A",
            opcion_b="Opción B",
            opcion_c="Opción C",
            opcion_d="Opción D",
            respuesta_correcta="A",
            activa=activa,
        )
        session.add(p)
        rows.append(p)
    session.commit()
    for p in rows:
        session.refresh(p)
    return rows


def _seed_config(
    session: Session,
    num_preguntas: int = 5,
    segundos_por_pregunta: int = 60,
    porcentaje_aprobacion: float | None = 70.0,
) -> ConfiguracionExamen:
    """Create or update the singleton ConfiguracionExamen."""
    config = session.get(ConfiguracionExamen, 1)
    if config is None:
        config = ConfiguracionExamen(
            id=1,
            num_preguntas=num_preguntas,
            segundos_por_pregunta=segundos_por_pregunta,
            porcentaje_aprobacion=porcentaje_aprobacion,
        )
        session.add(config)
    else:
        config.num_preguntas = num_preguntas
        config.segundos_por_pregunta = segundos_por_pregunta
        config.porcentaje_aprobacion = porcentaje_aprobacion
        session.add(config)
    session.commit()
    session.refresh(config)
    return config


# ---------------------------------------------------------------------------
# T077 — GET /api/admin/config RBAC
# ---------------------------------------------------------------------------

class TestGetConfigAdminOnly:
    """T077: GET /api/admin/config is accessible to admin only."""

    def test_admin_can_get_config(self, client: TestClient, admin_token: str):
        """200 for admin token."""
        response = client.get(
            "/api/admin/config",
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert response.status_code == 200
        body = response.json()
        assert "num_preguntas" in body
        assert "segundos_por_pregunta" in body
        assert "porcentaje_aprobacion" in body
        assert "estado_sistema" in body

    def test_editor_cannot_get_config(self, client: TestClient, editor_token: str):
        """403 for editor token."""
        response = client.get(
            "/api/admin/config",
            headers={"Authorization": f"Bearer {editor_token}"},
        )
        assert response.status_code == 403

    def test_estudiante_cannot_get_config(
        self, client: TestClient, estudiante_token: str
    ):
        """403 for estudiante token."""
        response = client.get(
            "/api/admin/config",
            headers={"Authorization": f"Bearer {estudiante_token}"},
        )
        assert response.status_code == 403


# ---------------------------------------------------------------------------
# T078 — PUT /api/admin/config validation
# ---------------------------------------------------------------------------

class TestUpdateConfigValidation:
    """T078: PUT /api/admin/config validates input data."""

    def test_valid_update_returns_200(
        self, client: TestClient, session: Session, admin_token: str
    ):
        """200 with valid data when there are >= num_preguntas active questions."""
        _seed_preguntas(session, count=10)

        response = client.put(
            "/api/admin/config",
            json={
                "num_preguntas": 5,
                "segundos_por_pregunta": 30,
                "porcentaje_aprobacion": 70.0,
            },
            headers={"Authorization": f"Bearer {admin_token}"},
        )

        assert response.status_code == 200
        body = response.json()
        assert body["num_preguntas"] == 5
        assert body["segundos_por_pregunta"] == 30
        assert body["porcentaje_aprobacion"] == 70.0
        assert body["estado_sistema"] == "activo"

    def test_num_preguntas_exceeds_active_returns_400(
        self, client: TestClient, session: Session, admin_token: str
    ):
        """400 when num_preguntas > count of active questions."""
        _seed_preguntas(session, count=3)

        response = client.put(
            "/api/admin/config",
            json={"num_preguntas": 10},
            headers={"Authorization": f"Bearer {admin_token}"},
        )

        assert response.status_code == 400

    def test_porcentaje_aprobacion_above_100_returns_400(
        self, client: TestClient, admin_token: str
    ):
        """400 when porcentaje_aprobacion > 100."""
        response = client.put(
            "/api/admin/config",
            json={"porcentaje_aprobacion": 101.0},
            headers={"Authorization": f"Bearer {admin_token}"},
        )

        assert response.status_code == 400

    def test_porcentaje_aprobacion_negative_returns_400(
        self, client: TestClient, admin_token: str
    ):
        """400 when porcentaje_aprobacion < 0."""
        response = client.put(
            "/api/admin/config",
            json={"porcentaje_aprobacion": -1.0},
            headers={"Authorization": f"Bearer {admin_token}"},
        )

        assert response.status_code == 400

    def test_no_config_estado_sistema_is_no_configurado(
        self, client: TestClient, admin_token: str
    ):
        """GET returns estado_sistema=no_configurado when porcentaje_aprobacion is null."""
        response = client.get(
            "/api/admin/config",
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert response.status_code == 200
        body = response.json()
        # Fresh DB: porcentaje_aprobacion is None → estado_sistema is no_configurado
        assert body["estado_sistema"] == "no_configurado"
        assert body["porcentaje_aprobacion"] is None


# ---------------------------------------------------------------------------
# T079 — Config snapshot isolation
# ---------------------------------------------------------------------------

class TestConfigSnapshotIsolation:
    """T079: Changing config does NOT affect already-started exam attempts.

    IntentoExamen stores num_preguntas, segundos_por_pregunta, and
    porcentaje_aprobacion as a snapshot at the time the exam started.
    Updating the config later must not change these values in the intento.
    """

    def test_snapshot_isolation(
        self,
        client: TestClient,
        session: Session,
        admin_token: str,
        estudiante_token: str,
        estudiante_user,
    ):
        """After updating config, a pre-existing intento keeps its original snapshot."""
        # Seed enough questions and config
        _seed_preguntas(session, count=10)
        _seed_config(
            session,
            num_preguntas=3,
            segundos_por_pregunta=45,
            porcentaje_aprobacion=60.0,
        )

        # Student starts an exam — creates IntentoExamen with snapshot
        start_resp = client.post(
            "/api/exams/start",
            headers={"Authorization": f"Bearer {estudiante_token}"},
        )
        assert start_resp.status_code == 201
        attempt_id = start_resp.json()["attempt_id"]

        # Verify snapshot was captured correctly
        intento = session.get(IntentoExamen, uuid.UUID(attempt_id))
        assert intento is not None
        assert intento.num_preguntas == 3
        assert intento.segundos_por_pregunta == 45
        assert intento.porcentaje_aprobacion == 60.0

        # Admin updates config with different values
        update_resp = client.put(
            "/api/admin/config",
            json={
                "num_preguntas": 5,
                "segundos_por_pregunta": 90,
                "porcentaje_aprobacion": 80.0,
            },
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert update_resp.status_code == 200

        # Re-read the intento — snapshot must be unchanged
        session.expire(intento)
        intento_after = session.get(IntentoExamen, uuid.UUID(attempt_id))
        assert intento_after.num_preguntas == 3
        assert intento_after.segundos_por_pregunta == 45
        assert intento_after.porcentaje_aprobacion == 60.0


# ---------------------------------------------------------------------------
# Helpers for student tests
# ---------------------------------------------------------------------------

def _seed_student(
    session: Session,
    nombre_completo: str,
    email: str,
    password: str = "Test1234!",
    activo: bool = True,
) -> User:
    """Insert a student User row and return it."""
    user = User(
        nombre_completo=nombre_completo,
        email=email,
        password_hash=hash_password(password),
        rol="estudiante",
        activo=activo,
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


# ---------------------------------------------------------------------------
# T084 — GET /api/admin/students
# ---------------------------------------------------------------------------

class TestListStudents:
    """T084: GET /api/admin/students listing, pagination, and filtering."""

    def test_admin_can_list_students(self, client: TestClient, admin_token: str):
        """200 for admin token."""
        response = client.get(
            "/api/admin/students",
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert response.status_code == 200
        body = response.json()
        assert "items" in body
        assert "total" in body

    def test_editor_can_list_students(self, client: TestClient, editor_token: str):
        """200 for editor token."""
        response = client.get(
            "/api/admin/students",
            headers={"Authorization": f"Bearer {editor_token}"},
        )
        assert response.status_code == 200

    def test_pagination_page_size(
        self, client: TestClient, session: Session, admin_token: str
    ):
        """Create 3 students, page_size=2 returns 2 items but total=3."""
        _seed_student(session, "Ana García", "ana@test.com")
        _seed_student(session, "Carlos López", "carlos@test.com")
        _seed_student(session, "Diana Martínez", "diana@test.com")

        response = client.get(
            "/api/admin/students?page=1&page_size=2",
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert response.status_code == 200
        body = response.json()
        assert len(body["items"]) == 2
        assert body["total"] == 3

    def test_filter_by_name(
        self, client: TestClient, session: Session, admin_token: str
    ):
        """?q=Juan returns only students whose name matches."""
        _seed_student(session, "Juan Pérez", "juan@test.com")
        _seed_student(session, "María Torres", "maria@test.com")

        response = client.get(
            "/api/admin/students?q=Juan",
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert response.status_code == 200
        body = response.json()
        assert body["total"] == 1
        assert body["items"][0]["nombre_completo"] == "Juan Pérez"


# ---------------------------------------------------------------------------
# T085 — POST /api/admin/students
# ---------------------------------------------------------------------------

class TestCreateStudentByEditor:
    """T085: Editor creates a student and new student can authenticate."""

    def test_editor_creates_student_returns_201(
        self, client: TestClient, editor_token: str
    ):
        """201 when editor creates a student."""
        response = client.post(
            "/api/admin/students",
            json={
                "nombre_completo": "Nuevo Estudiante",
                "email": "nuevo@test.com",
                "password": "Nuevo1234!",
            },
            headers={"Authorization": f"Bearer {editor_token}"},
        )
        assert response.status_code == 201
        body = response.json()
        assert body["email"] == "nuevo@test.com"
        assert body["rol"] == "estudiante"
        assert "password_hash" not in body

    def test_new_student_can_login(
        self, client: TestClient, editor_token: str
    ):
        """New student created by editor can authenticate via /api/auth/login."""
        # Create the student
        create_resp = client.post(
            "/api/admin/students",
            json={
                "nombre_completo": "Login Test",
                "email": "logintest@test.com",
                "password": "Login1234!",
            },
            headers={"Authorization": f"Bearer {editor_token}"},
        )
        assert create_resp.status_code == 201

        # New student should be able to log in
        login_resp = client.post(
            "/api/auth/login",
            json={"email": "logintest@test.com", "password": "Login1234!"},
        )
        assert login_resp.status_code == 200
        assert "access_token" in login_resp.json()

    def test_duplicate_email_returns_409(
        self, client: TestClient, session: Session, editor_token: str
    ):
        """409 when creating a student with an existing email."""
        _seed_student(session, "Existing", "existing@test.com")

        response = client.post(
            "/api/admin/students",
            json={
                "nombre_completo": "Duplicate",
                "email": "existing@test.com",
                "password": "Test1234!",
            },
            headers={"Authorization": f"Bearer {editor_token}"},
        )
        assert response.status_code == 409


# ---------------------------------------------------------------------------
# T086 — PATCH /api/admin/students/{id}/status
# ---------------------------------------------------------------------------

class TestToggleStudentStatus:
    """T086: Admin deactivates a student; deactivated student cannot log in."""

    def test_admin_deactivates_student(
        self, client: TestClient, session: Session, admin_token: str
    ):
        """200 when admin deactivates a student."""
        student = _seed_student(session, "Activo Estudiante", "activo@test.com")

        response = client.patch(
            f"/api/admin/students/{student.id}/status",
            json={"activo": False},
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert response.status_code == 200
        assert response.json()["activo"] is False

    def test_deactivated_student_cannot_login(
        self, client: TestClient, session: Session, admin_token: str
    ):
        """Deactivated student receives 403 on login attempt."""
        password = "Temp1234!"
        student = _seed_student(
            session, "Inactive Student", "inactive@test.com", password=password
        )

        # Deactivate
        patch_resp = client.patch(
            f"/api/admin/students/{student.id}/status",
            json={"activo": False},
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert patch_resp.status_code == 200

        # Login attempt should return 403
        login_resp = client.post(
            "/api/auth/login",
            json={"email": "inactive@test.com", "password": password},
        )
        assert login_resp.status_code == 403

    def test_editor_cannot_toggle_status(
        self, client: TestClient, session: Session, editor_token: str
    ):
        """403 when editor tries to toggle student status."""
        student = _seed_student(session, "Some Student", "some@test.com")

        response = client.patch(
            f"/api/admin/students/{student.id}/status",
            json={"activo": False},
            headers={"Authorization": f"Bearer {editor_token}"},
        )
        assert response.status_code == 403

    def test_toggle_nonexistent_student_returns_404(
        self, client: TestClient, admin_token: str
    ):
        """404 when toggling status of a non-existent student."""
        fake_id = uuid.uuid4()
        response = client.patch(
            f"/api/admin/students/{fake_id}/status",
            json={"activo": False},
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert response.status_code == 404
