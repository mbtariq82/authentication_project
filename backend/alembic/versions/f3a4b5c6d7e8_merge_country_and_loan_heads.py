"""merge country and loan migration heads

Revision ID: f3a4b5c6d7e8
Revises: c8d9e0f1a2b3, e21df71fa184
Create Date: 2026-08-20 12:15:00.000000

"""
from typing import Sequence, Union


revision: str = "f3a4b5c6d7e8"
down_revision: Union[str, Sequence[str], None] = (
    "c8d9e0f1a2b3",
    "e21df71fa184",
)
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass