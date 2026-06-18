from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Cookie, Depends, HTTPException, Response, status
from pydantic import BaseModel, EmailStr
from sqlmodel import Session

from app.core.database import get_session
from app.core.dependencies import get_current_user
from app.models.user import User
from app.services import auth_service

router = APIRouter()

REFRESH_COOKIE_NAME = "refresh_token"
REFRESH_COOKIE_MAX_AGE = 60 * 60 * 24 * 7  # 7 días en segundos


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class RegisterRequest(BaseModel):
    nombre_completo: str
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: str
    nombre_completo: str
    email: str
    rol: str
    activo: bool
    created_at: datetime


class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse


class RefreshResponse(BaseModel):
    access_token: str
    token_type: str


@router.post("/login", response_model=TokenResponse)
def login(
    request: LoginRequest,
    response: Response,
    session: Annotated[Session, Depends(get_session)],
):
    result = auth_service.login(request.email, request.password, session)
    response.set_cookie(
        key=REFRESH_COOKIE_NAME,
        value=result["refresh_token"],
        httponly=True,
        secure=False,  # True en producción con HTTPS
        samesite="strict",
        max_age=REFRESH_COOKIE_MAX_AGE,
        path="/api/auth",
    )
    return {
        "access_token": result["access_token"],
        "token_type": result["token_type"],
        "user": result["user"],
    }


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(
    request: RegisterRequest,
    session: Annotated[Session, Depends(get_session)],
):
    user = auth_service.register(
        request.nombre_completo, request.email, request.password, session
    )
    return {
        "id": str(user.id),
        "nombre_completo": user.nombre_completo,
        "email": user.email,
        "rol": user.rol,
        "activo": user.activo,
        "created_at": user.created_at,
    }


@router.post("/refresh", response_model=RefreshResponse)
def refresh(
    response: Response,
    session: Annotated[Session, Depends(get_session)],
    refresh_token: Annotated[str | None, Cookie(alias=REFRESH_COOKIE_NAME)] = None,
):
    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token no proporcionado",
        )
    result = auth_service.refresh_access_token(refresh_token, session)
    response.set_cookie(
        key=REFRESH_COOKIE_NAME,
        value=result["refresh_token"],
        httponly=True,
        secure=False,
        samesite="strict",
        max_age=REFRESH_COOKIE_MAX_AGE,
        path="/api/auth",
    )
    return {
        "access_token": result["access_token"],
        "token_type": result["token_type"],
    }


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(response: Response):
    response.delete_cookie(
        key=REFRESH_COOKIE_NAME,
        httponly=True,
        path="/api/auth",
    )


@router.get("/me", response_model=UserResponse)
def me(current_user: Annotated[User, Depends(get_current_user)]):
    return {
        "id": str(current_user.id),
        "nombre_completo": current_user.nombre_completo,
        "email": current_user.email,
        "rol": current_user.rol,
        "activo": current_user.activo,
        "created_at": current_user.created_at,
    }
