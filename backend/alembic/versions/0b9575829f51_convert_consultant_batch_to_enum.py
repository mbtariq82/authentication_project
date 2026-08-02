"""convert consultant batch to enum

Revision ID: 0b9575829f51
Revises: a6266c15088a
Create Date: 2026-08-02 19:10:06.226740

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = '0b9575829f51'
down_revision: Union[str, Sequence[str], None] = 'a6266c15088a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


batch_enum = postgresql.ENUM(
    "PYTHON",
    "JAVA",
    "DATA",
    "ANDROID",
    name="batch",
)

def upgrade() -> None:
    bind = op.get_bind()
    batch_enum.create(bind, checkfirst=True)

    op.alter_column(
        "consultants",
        "batch",
        existing_type=sa.String(length=100),
        type_=batch_enum,
        postgresql_using="batch::text::batch",
        nullable=False,
    )


def downgrade() -> None:
    op.alter_column(
        "consultants",
        "batch",
        existing_type=batch_enum,
        type_=sa.String(length=100),
        postgresql_using="batch::text",
        nullable=False,
    )

    batch_enum.drop(op.get_bind(), checkfirst=True)