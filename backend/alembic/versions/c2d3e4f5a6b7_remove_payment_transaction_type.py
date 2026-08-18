"""remove payment transaction type

Revision ID: c2d3e4f5a6b7
Revises: b91e83c70a42
Create Date: 2026-08-14 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op


revision: str = "c2d3e4f5a6b7"
down_revision: Union[str, Sequence[str], None] = "b91e83c70a42"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        """
        DO $$
        BEGIN
            IF EXISTS (
                SELECT 1
                FROM transactions
                WHERE transaction_type::text = 'PAYMENT'
            ) THEN
                RAISE EXCEPTION
                    'Cannot remove PAYMENT: existing transactions use this type';
            END IF;
        END
        $$;
        """
    )
    op.execute("ALTER TABLE transactions ALTER COLUMN transaction_type DROP DEFAULT")
    op.execute("ALTER TYPE transaction_type RENAME TO transaction_type_old")
    op.execute(
        """
        CREATE TYPE transaction_type AS ENUM (
            'TRANSFER',
            'DEPOSIT',
            'WITHDRAWAL'
        )
        """
    )
    op.execute(
        """
        ALTER TABLE transactions
        ALTER COLUMN transaction_type TYPE transaction_type
        USING transaction_type::text::transaction_type
        """
    )
    op.execute("DROP TYPE transaction_type_old")


def downgrade() -> None:
    op.execute("ALTER TABLE transactions ALTER COLUMN transaction_type DROP DEFAULT")
    op.execute("ALTER TYPE transaction_type RENAME TO transaction_type_old")
    op.execute(
        """
        CREATE TYPE transaction_type AS ENUM (
            'TRANSFER',
            'PAYMENT',
            'DEPOSIT',
            'WITHDRAWAL'
        )
        """
    )
    op.execute(
        """
        ALTER TABLE transactions
        ALTER COLUMN transaction_type TYPE transaction_type
        USING transaction_type::text::transaction_type
        """
    )
    op.execute("DROP TYPE transaction_type_old")