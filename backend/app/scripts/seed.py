#!/usr/bin/env python3
"""Script to seed the initial admin user."""

import sys
from pathlib import Path

# Add the backend directory to the path so we can import app modules
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from sqlmodel import Session, select

from app.core.database import engine
from app.core.security import hash_password
from app.core.settings import settings
from app.models import User  # noqa: F401 — registers table with metadata


def seed_admin() -> None:
    with Session(engine) as session:
        existing = session.exec(select(User).where(User.email == settings.admin_email)).first()
        if existing:
            print(f"Admin user already exists: {settings.admin_email}")
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
        session.refresh(admin)
        print(f"Admin user created: {admin.email} (id={admin.id})")


if __name__ == "__main__":
    seed_admin()
