import uuid
from datetime import datetime, timezone

from sqlmodel import Field, SQLModel


class User(SQLModel, table=True):
    __tablename__ = "users"

    id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        primary_key=True,
        index=True,
    )
    nombre_completo: str = Field(max_length=200)
    email: str = Field(unique=True, index=True, max_length=200)
    password_hash: str = Field(max_length=200)
    rol: str = Field(
        default="estudiante",
        sa_column_kwargs={"server_default": "estudiante"},
    )
    activo: bool = Field(default=True)
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
