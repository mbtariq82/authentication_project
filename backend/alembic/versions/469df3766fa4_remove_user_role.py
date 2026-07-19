"""remove user role

Revision ID: 469df3766fa4
Revises: 404c6f62a231
Create Date: 2026-07-19 19:39:40.258901

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '469df3766fa4'
down_revision: Union[str, Sequence[str], None] = '404c6f62a231'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.drop_column("users", "role")

def downgrade():
    op.add_column(
        "users",
        sa.Column("role", sa.String(), nullable=False)
    )