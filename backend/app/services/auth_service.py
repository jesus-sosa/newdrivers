from datetime import datetime, timezone
from uuid import UUID

from fastapi import HTTPException, status
from sqlmodel import Session, select

from app.core.security import (
    create_access_token,
    create_refresh_token,
    hash_password,
    verify_password,
    verify_token,
)
from app.models.user import User


def login(email: str, password: str, session: Session) -> dict:
    user = session.exec(select(User).where(User.email == email)).first()
    if not user or not verify_password(password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email o contraseña incorrectos",
        )
    if not user.activo:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Cuenta desactivada. Contacta al administrador.",
        )

    token_data = {"sub": str(user.id), "email": user.email, "rol": user.rol}
    access_token = create_access_token(token_data)
    refresh_token = create_refresh_token(token_data)

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "user": {
            "id": str(user.id),
            "nombre_completo": user.nombre_completo,
            "email": user.email,
            "rol": user.rol,
        },
    }


def refresh_access_token(refresh_token: str, session: Session) -> dict:
    payload = verify_token(refresh_token)
    if not payload or payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token inválido o expirado",
        )

    user_id = payload.get("sub")
    user = session.get(User, UUID(user_id))
    if not user or not user.activo:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario no encontrado o desactivado",
        )

    token_data = {"sub": str(user.id), "email": user.email, "rol": user.rol}
    access_token = create_access_token(token_data)
    new_refresh = create_refresh_token(token_data)

    return {
        "access_token": access_token,
        "refresh_token": new_refresh,
        "token_type": "bearer",
    }


def register(
    nombre_completo: str,
    email: str,
    password: str,
    session: Session,
) -> User:
    existing = session.exec(select(User).where(User.email == email)).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="El email ya está registrado",
        )
    user = User(
        nombre_completo=nombre_completo,
        email=email,
        password_hash=hash_password(password),
        rol="estudiante",
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


def get_user_by_id(user_id: UUID, session: Session) -> User | None:
    return session.get(User, user_id)
