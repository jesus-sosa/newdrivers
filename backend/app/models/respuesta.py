import uuid
from datetime import datetime, timezone
from typing import Optional

from sqlmodel import Field, SQLModel, UniqueConstraint


class RespuestaIntento(SQLModel, table=True):
    __tablename__ = "respuestas_intento"

    __table_args__ = (
        UniqueConstraint("intento_id", "pregunta_id", name="uq_intento_pregunta"),
        UniqueConstraint("intento_id", "orden", name="uq_intento_orden"),
    )

    id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        primary_key=True,
        index=True,
    )
    intento_id: uuid.UUID = Field(foreign_key="intentos_examen.id", index=True)
    pregunta_id: int = Field(foreign_key="preguntas.id")
    orden: int  # posición en el examen (1 a N)
    opcion_seleccionada: Optional[str] = Field(default=None, max_length=1)  # A, B, C, D o NULL
    es_correcta: Optional[bool] = Field(default=None)
    tiempo_agotado: bool = Field(default=False)
    respondida_at: Optional[datetime] = Field(default=None)
