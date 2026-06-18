import uuid
from datetime import datetime, timezone
from typing import Optional

from sqlmodel import Field, SQLModel


class ConfiguracionExamen(SQLModel, table=True):
    __tablename__ = "configuracion_examen"

    id: int = Field(default=1, primary_key=True)
    num_preguntas: int = Field(default=20)
    segundos_por_pregunta: int = Field(default=60)
    # NULL = sistema no configurado, bloquea inicio de exámenes
    porcentaje_aprobacion: Optional[float] = Field(default=None)
    updated_at: Optional[datetime] = Field(default=None)
    updated_by: Optional[uuid.UUID] = Field(
        default=None,
        foreign_key="users.id",
    )
