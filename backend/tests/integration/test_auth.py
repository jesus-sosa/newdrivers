"""Integration tests for authentication endpoints (US2: student self-registration)."""

import pytest
from fastapi.testclient import TestClient


class TestRegister:
    """Tests for POST /api/auth/register."""

    def test_register_success(self, client: TestClient):
        """T058: Registering a new student returns 201 with correct fields."""
        payload = {
            "nombre_completo": "Maria Garcia",
            "email": "maria.garcia@example.com",
            "password": "SecurePass1!",
        }

        response = client.post("/api/auth/register", json=payload)

        assert response.status_code == 201
        body = response.json()

        # Role must default to "estudiante"
        assert body["rol"] == "estudiante"

        # Email must match what was sent
        assert body["email"] == payload["email"]

        # password_hash must NOT appear anywhere in the response
        assert "password_hash" not in body
        assert "password" not in body

        # Other expected fields present
        assert "id" in body
        assert body["nombre_completo"] == payload["nombre_completo"]
        assert "activo" in body
        assert "created_at" in body

    def test_register_duplicate_email(self, client: TestClient):
        """T059: Registering with an already-used email returns 409."""
        payload = {
            "nombre_completo": "Juan Perez",
            "email": "juan.perez@example.com",
            "password": "SecurePass1!",
        }

        # First registration must succeed
        first_response = client.post("/api/auth/register", json=payload)
        assert first_response.status_code == 201

        # Second registration with the same email must be rejected
        second_response = client.post("/api/auth/register", json=payload)
        assert second_response.status_code == 409
