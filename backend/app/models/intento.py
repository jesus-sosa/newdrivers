import uuid
from datetime import datetime, timezone
from typing import Optional

from sqlmodel import Field, SQLModel


class IntentoExamen(SQLModel, table=True):
    __tablename__ = "intentos_examen"

    id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        primary_key=True,
        index=True,
    )
    estudiante_id: uuid.UUID = Field(foreign_key="users.id", index=True)
    # Snapshot de la configuración al momento de iniciar el examen
    num_preguntas: int
    porcentaje_aprobacion: float
    puntuacion: Optional[int] = Field(default=None)
    resultado: Optional[str] = Field(default=None, max_length=20)  # aprobado | reprobado
    iniciado_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    # NULL = examen en curso
    finalizado_at: Optional[datetime] = Field(default=None, index=True)
