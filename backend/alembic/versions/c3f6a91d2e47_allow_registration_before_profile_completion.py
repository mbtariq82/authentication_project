"""allow registration before profile completion

Revision ID: c3f6a91d2e47
Revises: e142528b46cd
Create Date: 2026-08-14 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "c3f6a91d2e47"
down_revision: Union[str, Sequence[str], None] = "e142528b46cd"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Allow users to complete personal details after registration."""
    op.alter_column(
        "users",
        "dob",
        existing_type=sa.Date(),
        nullable=True,
    )
    op.alter_column(
        "users",
        "address_line",
        existing_type=sa.String(length=255),
        nullable=True,
    )
    op.alter_column(
        "users",
        "city",
        existing_type=sa.String(length=100),
        nullable=True,
    )
    op.alter_column(
        "users",
        "county",
        existing_type=sa.String(length=100),
        nullable=True,
    )
    op.alter_column(
        "users",
        "postcode",
        existing_type=sa.String(length=20),
        nullable=True,
    )
    op.execute(
        "UPDATE accounts SET account_status = 'PENDING' "
        "WHERE account_status IS NULL"
    )
    op.alter_column(
        "accounts",
        "account_status",
        existing_type=sa.String(length=20),
        nullable=False,
        server_default="PENDING",
    )


def downgrade() -> None:
    """Restore the schema introduced by revision 100."""
    op.alter_column(
        "accounts",
        "account_status",
        existing_type=sa.String(length=20),
        nullable=False,
        server_default=None,
    )
    op.alter_column(
        "users",
        "postcode",
        existing_type=sa.String(length=20),
        nullable=False,
    )
    op.alter_column(
        "users",
        "county",
        existing_type=sa.String(length=100),
        nullable=False,
    )
    op.alter_column(
        "users",
        "city",
        existing_type=sa.String(length=100),
        nullable=False,
    )
    op.alter_column(
        "users",
        "address_line",
        existing_type=sa.String(length=255),
        nullable=False,
    )
    op.alter_column(
        "users",
        "dob",
        existing_type=sa.Date(),
        nullable=False,
    )
