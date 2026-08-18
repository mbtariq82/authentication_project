"""merge transaction and profile migration heads

Revision ID: 9f1e3a2b4c5d
Revises: c2d3e4f5a6b7, d7b3e4f9a102
Create Date: 2026-08-18 00:00:00.000000

This merge resolves the split migration graph created when the transaction
schema work and the profile/account schema work were developed on separate
branches from the same parent revision.
"""
from typing import Sequence, Union


# revision identifiers, used by Alembic.
revision: str = "9f1e3a2b4c5d"
down_revision: Union[str, Sequence[str], None] = (
    "c2d3e4f5a6b7",
    "d7b3e4f9a102",
)
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
