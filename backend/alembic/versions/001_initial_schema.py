"""Esquema inicial: users, preguntas, configuracion_examen, intentos_examen, respuestas_intento

Revision ID: 001_initial_schema
Revises: 
Create Date: 2026-06-18 00:00:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
import sqlmodel
from alembic import op

revision: str = "001_initial_schema"
down_revision: Union[str, None] = None
branch_labels: Union[Sequence[str], None] = None
depends_on: Union[Sequence[str], None] = None


def upgrade() -> None:
    # Tabla: users
    op.create_table(
        "users",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("nombre_completo", sqlmodel.AutoString(length=200), nullable=False),
        sa.Column("email", sqlmodel.AutoString(length=200), nullable=False),
        sa.Column("password_hash", sqlmodel.AutoString(length=200), nullable=False),
        sa.Column(
            "rol",
            sqlmodel.AutoString(length=50),
            server_default="estudiante",
            nullable=False,
        ),
        sa.Column("activo", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_users_id", "users", ["id"])
    op.create_index("ix_users_email", "users", ["email"], unique=True)

    # Tabla: preguntas
    op.create_table(
        "preguntas",
        sa.Column("id", sa.Integer(), nullable=False, autoincrement=True),
        sa.Column("tema", sqlmodel.AutoString(length=200), nullable=False),
        sa.Column("pregunta", sqlmodel.AutoString(length=1000), nullable=False),
        sa.Column("imagen_archivo", sqlmodel.AutoString(length=500), nullable=True),
        sa.Column("descripcion_imagen", sqlmodel.AutoString(length=500), nullable=True),
        sa.Column("opcion_a", sqlmodel.AutoString(length=500), nullable=False),
        sa.Column("opcion_b", sqlmodel.AutoString(length=500), nullable=False),
        sa.Column("opcion_c", sqlmodel.AutoString(length=500), nullable=False),
        sa.Column("opcion_d", sqlmodel.AutoString(length=500), nullable=False),
        sa.Column("respuesta_correcta", sqlmodel.AutoString(length=1), nullable=False),
        sa.Column("fundamento_juridico", sqlmodel.AutoString(length=2000), nullable=True),
        sa.Column("activa", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_preguntas_tema", "preguntas", ["tema"])
    op.create_index("ix_preguntas_activa", "preguntas", ["activa"])

    # Tabla: configuracion_examen (singleton id=1)
    op.create_table(
        "configuracion_examen",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("num_preguntas", sa.Integer(), nullable=False, server_default="20"),
        sa.Column("segundos_por_pregunta", sa.Integer(), nullable=False, server_default="60"),
        sa.Column("porcentaje_aprobacion", sa.Float(), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("updated_by", sa.Uuid(), nullable=True),
        sa.ForeignKeyConstraint(["updated_by"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    # Insertar fila singleton inicial (sin porcentaje_aprobacion = sistema no configurado)
    op.execute(
        "INSERT INTO configuracion_examen (id, num_preguntas, segundos_por_pregunta) "
        "VALUES (1, 20, 60)"
    )

    # Tabla: intentos_examen
    op.create_table(
        "intentos_examen",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("estudiante_id", sa.Uuid(), nullable=False),
        sa.Column("num_preguntas", sa.Integer(), nullable=False),
        sa.Column("porcentaje_aprobacion", sa.Float(), nullable=False),
        sa.Column("puntuacion", sa.Integer(), nullable=True),
        sa.Column("resultado", sqlmodel.AutoString(length=20), nullable=True),
        sa.Column("iniciado_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("finalizado_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["estudiante_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_intentos_examen_id", "intentos_examen", ["id"])
    op.create_index("ix_intentos_examen_estudiante_id", "intentos_examen", ["estudiante_id"])
    op.create_index("ix_intentos_examen_finalizado_at", "intentos_examen", ["finalizado_at"])

    # Tabla: respuestas_intento
    op.create_table(
        "respuestas_intento",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("intento_id", sa.Uuid(), nullable=False),
        sa.Column("pregunta_id", sa.Integer(), nullable=False),
        sa.Column("orden", sa.Integer(), nullable=False),
        sa.Column("opcion_seleccionada", sqlmodel.AutoString(length=1), nullable=True),
        sa.Column("es_correcta", sa.Boolean(), nullable=True),
        sa.Column("tiempo_agotado", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("respondida_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["intento_id"], ["intentos_examen.id"]),
        sa.ForeignKeyConstraint(["pregunta_id"], ["preguntas.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("intento_id", "pregunta_id", name="uq_intento_pregunta"),
        sa.UniqueConstraint("intento_id", "orden", name="uq_intento_orden"),
    )
    op.create_index("ix_respuestas_intento_id", "respuestas_intento", ["id"])
    op.create_index("ix_respuestas_intento_intento_id", "respuestas_intento", ["intento_id"])


def downgrade() -> None:
    op.drop_table("respuestas_intento")
    op.drop_table("intentos_examen")
    op.drop_table("configuracion_examen")
    op.drop_table("preguntas")
    op.drop_table("users")
