"""add beneficiaries and transaction details

Revision ID: f1a2b3c4d5e6
Revises: d4c96b27e31a
Create Date: 2026-08-13 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = "f1a2b3c4d5e6"
down_revision: Union[str, Sequence[str], None] = "d4c96b27e31a"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


transaction_type = postgresql.ENUM(
    "TRANSFER",
    "PAYMENT",
    "DEPOSIT",
    "WITHDRAWAL",
    name="transaction_type",
    create_type=False,
)
transaction_direction = postgresql.ENUM(
    "DEBIT",
    "CREDIT",
    name="transaction_direction",
    create_type=False,
)
transaction_status = postgresql.ENUM(
    "PENDING",
    "COMPLETED",
    "FAILED",
    "CANCELLED",
    name="transaction_status",
    create_type=False,
)


def upgrade() -> None:
    op.drop_index("ix_transactions_id", table_name="transactions")
    op.drop_table("transactions")

    transaction_type.create(op.get_bind(), checkfirst=True)
    transaction_direction.create(op.get_bind(), checkfirst=True)
    transaction_status.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "beneficiaries",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=150), nullable=False),
        sa.Column("account_number", sa.String(length=50), nullable=False),
        sa.Column("sort_code", sa.String(length=20), nullable=False),
        sa.Column("bank_name", sa.String(length=150), nullable=False),
        sa.Column("reference", sa.String(length=255), nullable=True),
        sa.Column(
            "is_active",
            sa.Boolean(),
            server_default=sa.text("true"),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["user_id"], ["users.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_beneficiaries_user_id", "beneficiaries", ["user_id"])
    op.create_index(
        "ix_beneficiaries_account_number",
        "beneficiaries",
        ["account_number"],
    )
    op.create_index(
        "ix_beneficiaries_sort_code", "beneficiaries", ["sort_code"]
    )

    op.create_table(
        "transactions",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("account_id", sa.Integer(), nullable=False),
        sa.Column("beneficiary_id", sa.Integer(), nullable=True),
        sa.Column("transaction_type", transaction_type, nullable=False),
        sa.Column("direction", transaction_direction, nullable=False),
        sa.Column("amount", sa.Numeric(precision=18, scale=2), nullable=False),
        sa.Column(
            "status",
            transaction_status,
            server_default=sa.text("'PENDING'"),
            nullable=False,
        ),
        sa.Column("reference", sa.String(length=100), nullable=False),
        sa.Column("transfer_reference", sa.String(length=100), nullable=True),
        sa.Column("description", sa.String(length=255), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["account_id"], ["accounts.id"], ondelete="RESTRICT"
        ),
        sa.ForeignKeyConstraint(
            ["beneficiary_id"], ["beneficiaries.id"], ondelete="RESTRICT"
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("reference"),
    )
    op.create_index("ix_transactions_account_id", "transactions", ["account_id"])
    op.create_index(
        "ix_transactions_beneficiary_id", "transactions", ["beneficiary_id"]
    )
    op.create_index(
        "ix_transactions_transfer_reference",
        "transactions",
        ["transfer_reference"],
    )
    op.create_index("ix_transactions_created_at", "transactions", ["created_at"])
    op.create_index("ix_transactions_status", "transactions", ["status"])

    op.create_table(
        "transaction_logs",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("transaction_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=True),
        sa.Column("action", sa.String(length=100), nullable=False),
        sa.Column("status", sa.String(length=50), nullable=False),
        sa.Column("message", sa.Text(), nullable=True),
        sa.Column("metadata", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["transaction_id"], ["transactions.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(
            ["user_id"], ["users.id"], ondelete="SET NULL"
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_transaction_logs_transaction_id", "transaction_logs", ["transaction_id"]
    )
    op.create_index("ix_transaction_logs_user_id", "transaction_logs", ["user_id"])
    op.create_index(
        "ix_transaction_logs_created_at", "transaction_logs", ["created_at"]
    )


def downgrade() -> None:
    op.drop_index("ix_transaction_logs_created_at", table_name="transaction_logs")
    op.drop_index("ix_transaction_logs_user_id", table_name="transaction_logs")
    op.drop_index(
        "ix_transaction_logs_transaction_id", table_name="transaction_logs"
    )
    op.drop_table("transaction_logs")

    op.drop_index("ix_transactions_status", table_name="transactions")
    op.drop_index("ix_transactions_created_at", table_name="transactions")
    op.drop_index("ix_transactions_transfer_reference", table_name="transactions")
    op.drop_index("ix_transactions_beneficiary_id", table_name="transactions")
    op.drop_index("ix_transactions_account_id", table_name="transactions")
    op.drop_table("transactions")

    op.drop_index("ix_beneficiaries_sort_code", table_name="beneficiaries")
    op.drop_index("ix_beneficiaries_account_number", table_name="beneficiaries")
    op.drop_index("ix_beneficiaries_user_id", table_name="beneficiaries")
    op.drop_table("beneficiaries")

    transaction_status.drop(op.get_bind(), checkfirst=True)
    transaction_direction.drop(op.get_bind(), checkfirst=True)
    transaction_type.drop(op.get_bind(), checkfirst=True)

    op.create_table(
        "transactions",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_transactions_id", "transactions", ["id"])
