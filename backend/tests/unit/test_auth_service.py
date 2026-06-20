"""Unit tests for auth_service.py (T100).

Tests the login() function directly without going through HTTP layer.
"""

import pytest
from fastapi import HTTPException

from app.services.auth_service import login
from app.core.security import hash_password
from app.models.user import User


_CORRECT_PASSWORD = "Student1234!"
_WRONG_PASSWORD = "WrongPass999!"


class TestAuthServiceLogin:
    """Direct unit tests for auth_service.login()."""

    def test_login_success_returns_access_token(self, session):
        """Correct credentials → dict containing access_token."""
        user = User(
            nombre_completo="Test Student",
            email="student@example.com",
            password_hash=hash_password(_CORRECT_PASSWORD),
            rol="estudiante",
            activo=True,
        )
        session.add(user)
        session.commit()

        result = login("student@example.com", _CORRECT_PASSWORD, session)

        assert "access_token" in result
        assert result["token_type"] == "bearer"
        assert result["user"]["email"] == "student@example.com"

    def test_login_wrong_password_raises_401(self, session):
        """Wrong password → HTTPException with status 401."""
        user = User(
            nombre_completo="Test Student",
            email="student2@example.com",
            password_hash=hash_password(_CORRECT_PASSWORD),
            rol="estudiante",
            activo=True,
        )
        session.add(user)
        session.commit()

        with pytest.raises(HTTPException) as exc_info:
            login("student2@example.com", _WRONG_PASSWORD, session)

        assert exc_info.value.status_code == 401

    def test_login_inactive_user_raises_403(self, session):
        """Inactive user → HTTPException with status 403."""
        user = User(
            nombre_completo="Inactive Student",
            email="inactive@example.com",
            password_hash=hash_password(_CORRECT_PASSWORD),
            rol="estudiante",
            activo=False,
        )
        session.add(user)
        session.commit()

        with pytest.raises(HTTPException) as exc_info:
            login("inactive@example.com", _CORRECT_PASSWORD, session)

        assert exc_info.value.status_code == 403
