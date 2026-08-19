"""add country to users

Revision ID: b7c8d9e0f1a2
Revises: 9f1e3a2b4c5d
Create Date: 2026-08-19 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "b7c8d9e0f1a2"
down_revision: Union[str, Sequence[str], None] = "9f1e3a2b4c5d"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("users", sa.Column("country", sa.String(length=100), nullable=True))


def downgrade() -> None:
    op.drop_column("users", "country")