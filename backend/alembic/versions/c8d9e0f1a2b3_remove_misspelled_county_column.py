"""rename misspelled county column to country

Revision ID: c8d9e0f1a2b3
Revises: 9f1e3a2b4c5d
Create Date: 2026-08-19 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "c8d9e0f1a2b3"
down_revision: Union[str, Sequence[str], None] = "9f1e3a2b4c5d"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column(
        "users",
        "county",
        new_column_name="country",
        existing_type=sa.String(length=100),
        existing_nullable=True,
    )


def downgrade() -> None:
    op.alter_column(
        "users",
        "country",
        new_column_name="county",
        existing_type=sa.String(length=100),
        existing_nullable=True,
    )