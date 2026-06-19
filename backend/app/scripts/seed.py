#!/usr/bin/env python3
"""Script to seed initial admin user and exam configuration."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from sqlmodel import Session, select

from app.core.database import engine
from app.core.security import hash_password
from app.core.settings import settings
from app.models import ConfiguracionExamen, User  # noqa: F401


def seed_admin(session: Session) -> None:
    existing = session.exec(select(User).where(User.email == settings.admin_email)).first()
    if existing:
        print(f"Admin already exists: {settings.admin_email}")
        return
    admin = User(
        nombre_completo="Administrador",
        email=settings.admin_email,
        password_hash=hash_password(settings.admin_password),
        rol="admin",
        activo=True,
    )
    session.add(admin)
    session.commit()
    print(f"Admin created: {admin.email}")


def seed_config(session: Session) -> None:
    config = session.get(ConfiguracionExamen, 1)
    if config and config.porcentaje_aprobacion is not None:
        print(f"Exam config already set (porcentaje_aprobacion={config.porcentaje_aprobacion})")
        return
    if config is None:
        config = ConfiguracionExamen(id=1, num_preguntas=20, segundos_por_pregunta=60, porcentaje_aprobacion=70.0)
        session.add(config)
    else:
        config.num_preguntas = 20
        config.segundos_por_pregunta = 60
        config.porcentaje_aprobacion = 70.0
        session.add(config)
    session.commit()
    print("Exam config set: 20 questions, 60s/question, 70% to pass")


def seed_all() -> None:
    with Session(engine) as session:
        seed_admin(session)
        seed_config(session)


if __name__ == "__main__":
    seed_all()
