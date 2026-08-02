"""add ending soon placement status

Revision ID: 962fbd89c297
Revises: 0b9575829f51
Create Date: 2026-08-02 19:19:36.259779

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '962fbd89c297'
down_revision: Union[str, Sequence[str], None] = '0b9575829f51'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        "ALTER TYPE placement_status "
        "ADD VALUE IF NOT EXISTS 'ONBOARDING' BEFORE 'AVAILABLE'"
    )

    op.execute(
        "ALTER TYPE placement_status "
        "ADD VALUE IF NOT EXISTS 'TRAINING' BEFORE 'AVAILABLE'"
    )

    op.execute(
        "ALTER TYPE placement_status "
        "ADD VALUE IF NOT EXISTS 'ENDING_SOON' AFTER 'PLACED'"
    )


def downgrade() -> None:
    # PostgreSQL cannot directly remove an individual enum value.
    pass