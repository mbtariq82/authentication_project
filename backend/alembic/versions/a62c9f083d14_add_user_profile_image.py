"""add user profile image

Revision ID: a62c9f083d14
Revises: f18b7a42c6d1
Create Date: 2026-08-13 16:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "a62c9f083d14"
down_revision: Union[str, Sequence[str], None] = "f18b7a42c6d1"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "users",
        sa.Column("profile_image_key", sa.String(length=512), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("users", "profile_image_key")
