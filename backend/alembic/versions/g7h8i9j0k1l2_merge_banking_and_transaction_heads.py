"""merge banking and transaction migration heads

Revision ID: g7h8i9j0k1l2
Revises: f18b7a42c6d1, f1a2b3c4d5e6
Create Date: 2026-08-13 00:00:00.000000

"""
from typing import Sequence, Union


revision: str = "g7h8i9j0k1l2"
down_revision: Union[str, Sequence[str], None] = (
    "f18b7a42c6d1",
    "f1a2b3c4d5e6",
)
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
