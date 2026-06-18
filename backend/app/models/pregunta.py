from datetime import datetime, timezone
from typing import Optional

from sqlmodel import Field, SQLModel


class Pregunta(SQLModel, table=True):
    __tablename__ = "preguntas"

    id: Optional[int] = Field(default=None, primary_key=True)
    tema: str = Field(max_length=200, index=True)
    pregunta: str = Field(max_length=1000)
    imagen_archivo: Optional[str] = Field(default=None, max_length=500)
    descripcion_imagen: Optional[str] = Field(default=None, max_length=500)
    opcion_a: str = Field(max_length=500)
    opcion_b: str = Field(max_length=500)
    opcion_c: str = Field(max_length=500)
    opcion_d: str = Field(max_length=500)
    respuesta_correcta: str = Field(max_length=1)  # A, B, C o D
    fundamento_juridico: Optional[str] = Field(default=None, max_length=2000)
    activa: bool = Field(default=True, index=True)
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
