"""RBAC contract tests (T102).

Verifies that each role can only access its permitted endpoints.
Uses HTTP-level tests via the TestClient (client fixture).
"""

import uuid

import pytest


FAKE_UUID = str(uuid.uuid4())


class TestAdminOnlyEndpoints:
    """Endpoints that only admins may access."""

    def test_get_config_admin_allowed(self, client, admin_token):
        resp = client.get(
            "/api/admin/config",
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert resp.status_code == 200

    def test_get_config_editor_forbidden(self, client, editor_token):
        resp = client.get(
            "/api/admin/config",
            headers={"Authorization": f"Bearer {editor_token}"},
        )
        assert resp.status_code == 403

    def test_get_config_estudiante_forbidden(self, client, estudiante_token):
        resp = client.get(
            "/api/admin/config",
            headers={"Authorization": f"Bearer {estudiante_token}"},
        )
        assert resp.status_code == 403

    def test_put_config_admin_allowed(self, client, admin_token):
        resp = client.put(
            "/api/admin/config",
            json={},
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        # 200 (successful empty update) or 400 (validation error) — both prove access granted
        assert resp.status_code in {200, 400}

    def test_put_config_editor_forbidden(self, client, editor_token):
        resp = client.put(
            "/api/admin/config",
            json={},
            headers={"Authorization": f"Bearer {editor_token}"},
        )
        assert resp.status_code == 403

    def test_put_config_estudiante_forbidden(self, client, estudiante_token):
        resp = client.put(
            "/api/admin/config",
            json={},
            headers={"Authorization": f"Bearer {estudiante_token}"},
        )
        assert resp.status_code == 403

    def test_get_student_detail_admin_gets_404(self, client, admin_token):
        """Admin on non-existent student → 404 (proves access granted, resource missing)."""
        resp = client.get(
            f"/api/admin/students/{FAKE_UUID}",
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert resp.status_code == 404

    def test_get_student_detail_editor_forbidden(self, client, editor_token):
        resp = client.get(
            f"/api/admin/students/{FAKE_UUID}",
            headers={"Authorization": f"Bearer {editor_token}"},
        )
        assert resp.status_code == 403

    def test_get_student_detail_estudiante_forbidden(self, client, estudiante_token):
        resp = client.get(
            f"/api/admin/students/{FAKE_UUID}",
            headers={"Authorization": f"Bearer {estudiante_token}"},
        )
        assert resp.status_code == 403

    def test_patch_student_status_admin_gets_404(self, client, admin_token):
        """Admin on non-existent student status → 404 (proves access granted)."""
        resp = client.patch(
            f"/api/admin/students/{FAKE_UUID}/status",
            json={"activo": True},
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert resp.status_code == 404

    def test_patch_student_status_editor_forbidden(self, client, editor_token):
        resp = client.patch(
            f"/api/admin/students/{FAKE_UUID}/status",
            json={"activo": True},
            headers={"Authorization": f"Bearer {editor_token}"},
        )
        assert resp.status_code == 403

    def test_patch_student_status_estudiante_forbidden(self, client, estudiante_token):
        resp = client.patch(
            f"/api/admin/students/{FAKE_UUID}/status",
            json={"activo": True},
            headers={"Authorization": f"Bearer {estudiante_token}"},
        )
        assert resp.status_code == 403


class TestAdminOrEditorEndpoints:
    """Endpoints accessible to admin and editor, but not estudiante."""

    def test_list_students_admin_allowed(self, client, admin_token):
        resp = client.get(
            "/api/admin/students",
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert resp.status_code == 200

    def test_list_students_editor_allowed(self, client, editor_token):
        resp = client.get(
            "/api/admin/students",
            headers={"Authorization": f"Bearer {editor_token}"},
        )
        assert resp.status_code == 200

    def test_list_students_estudiante_forbidden(self, client, estudiante_token):
        resp = client.get(
            "/api/admin/students",
            headers={"Authorization": f"Bearer {estudiante_token}"},
        )
        assert resp.status_code == 403

    def test_list_questions_admin_allowed(self, client, admin_token):
        resp = client.get(
            "/api/questions",
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert resp.status_code == 200

    def test_list_questions_editor_allowed(self, client, editor_token):
        resp = client.get(
            "/api/questions",
            headers={"Authorization": f"Bearer {editor_token}"},
        )
        assert resp.status_code == 200

    def test_list_questions_estudiante_forbidden(self, client, estudiante_token):
        resp = client.get(
            "/api/questions",
            headers={"Authorization": f"Bearer {estudiante_token}"},
        )
        assert resp.status_code == 403

    def test_create_question_admin_gets_access(self, client, admin_token):
        """Admin sending incomplete body → 422 (access granted, validation failed)."""
        resp = client.post(
            "/api/questions",
            json={"tema": "incomplete"},
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        # 422 = validation error (access was granted); 400 = also access granted
        assert resp.status_code in {200, 201, 400, 422}

    def test_create_question_editor_gets_access(self, client, editor_token):
        """Editor sending incomplete body → 422 (access granted, validation failed)."""
        resp = client.post(
            "/api/questions",
            json={"tema": "incomplete"},
            headers={"Authorization": f"Bearer {editor_token}"},
        )
        assert resp.status_code in {200, 201, 400, 422}

    def test_create_question_estudiante_forbidden(self, client, estudiante_token):
        resp = client.post(
            "/api/questions",
            json={"tema": "incomplete"},
            headers={"Authorization": f"Bearer {estudiante_token}"},
        )
        assert resp.status_code == 403


class TestEstudianteOnlyEndpoints:
    """Endpoints that only students may access."""

    def test_start_exam_estudiante_gets_access(self, client, estudiante_token):
        """Estudiante starting exam → 409 (not configured) or 201 — both prove access."""
        resp = client.post(
            "/api/exams/start",
            headers={"Authorization": f"Bearer {estudiante_token}"},
        )
        # 409 = system not configured; 201 = started successfully
        assert resp.status_code in {201, 409}

    def test_start_exam_admin_forbidden(self, client, admin_token):
        resp = client.post(
            "/api/exams/start",
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert resp.status_code == 403

    def test_start_exam_editor_forbidden(self, client, editor_token):
        resp = client.post(
            "/api/exams/start",
            headers={"Authorization": f"Bearer {editor_token}"},
        )
        assert resp.status_code == 403

    def test_get_history_estudiante_allowed(self, client, estudiante_token):
        resp = client.get(
            "/api/exams/history",
            headers={"Authorization": f"Bearer {estudiante_token}"},
        )
        assert resp.status_code == 200

    def test_get_history_admin_forbidden(self, client, admin_token):
        resp = client.get(
            "/api/exams/history",
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert resp.status_code == 403

    def test_get_history_editor_forbidden(self, client, editor_token):
        resp = client.get(
            "/api/exams/history",
            headers={"Authorization": f"Bearer {editor_token}"},
        )
        assert resp.status_code == 403
