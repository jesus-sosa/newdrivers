"""Add segundos_por_pregunta column to intentos_examen

Revision ID: 002_add_segundos_por_pregunta
Revises: 001_initial_schema
Create Date: 2026-06-20 00:00:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "002_add_segundos_por_pregunta"
down_revision: Union[str, None] = "001_initial_schema"
branch_labels: Union[Sequence[str], None] = None
depends_on: Union[Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "intentos_examen",
        sa.Column(
            "segundos_por_pregunta",
            sa.Integer(),
            nullable=False,
            server_default="60",
        ),
    )


def downgrade() -> None:
    op.drop_column("intentos_examen", "segundos_por_pregunta")
