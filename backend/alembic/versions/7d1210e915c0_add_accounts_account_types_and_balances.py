"""add accounts, account_types and balances

Revision ID: 7d1210e915c0
Revises: 7dae6266af8f
Create Date: 2026-08-10 02:59:15.957135

"""
from typing import Sequence, Union
from decimal import Decimal
from sqlalchemy.dialects import postgresql

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7d1210e915c0'
down_revision: Union[str, Sequence[str], None] = '7dae6266af8f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    approval_status = postgresql.ENUM(
        "PENDING",
        "APPROVED",
        "REJECTED",
        name="approval_status",
        create_type=False,
    )
    account_status = postgresql.ENUM(
        "ACTIVE",
        "FROZEN",
        "CLOSED",
        name="account_status",
        create_type=False,
    )
    approval_status.create(op.get_bind(), checkfirst=True)
    account_status.create(op.get_bind(), checkfirst=True)

    account_types = op.create_table(
        "account_types",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=20), nullable=False),
        sa.Column(
            "interest_rate",
            sa.Numeric(5, 2),
            nullable=False,
            server_default="0.00",
        ),
        sa.Column(
            "minimum_balance",
            sa.Numeric(18, 2),
            nullable=False,
            server_default="0.00",
        ),
        sa.Column(
            "allows_overdraft",
            sa.Boolean(),
            nullable=False,
            server_default="false",
        ),
        sa.Column(
            "is_active", sa.Boolean(), nullable=False, server_default="true"
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )
    op.create_index(
        op.f("ix_account_types_id"), "account_types", ["id"], unique=False
    )

    op.create_table(
        "accounts",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("account_type_id", sa.Integer(), nullable=False),
        sa.Column("account_number", sa.String(length=20), nullable=True),
        sa.Column(
            "admin_approved",
            approval_status,
            nullable=False,
            server_default="PENDING",
        ),
        sa.Column(
            "status", account_status, nullable=False, server_default="ACTIVE"
        ),
        sa.Column("approved_by", sa.Integer(), nullable=True),
        sa.Column("approved_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("rejection_reason", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column("closed_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(
            ["account_type_id"], ["account_types.id"], ondelete="RESTRICT"
        ),
        sa.ForeignKeyConstraint(
            ["approved_by"], ["users.id"], ondelete="SET NULL"
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "user_id", "account_type_id", name="uq_accounts_user_type"
        ),
    )
    op.create_index(op.f("ix_accounts_id"), "accounts", ["id"], unique=False)
    op.create_index(
        op.f("ix_accounts_user_id"), "accounts", ["user_id"], unique=False
    )
    op.create_index(
        op.f("ix_accounts_account_number"),
        "accounts",
        ["account_number"],
        unique=True,
    )

    op.create_table(
        "balances",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("account_id", sa.Integer(), nullable=False),
        sa.Column(
            "ledger_balance",
            sa.Numeric(18, 2),
            nullable=False,
            server_default="0.00",
        ),
        sa.Column(
            "available_balance",
            sa.Numeric(18, 2),
            nullable=False,
            server_default="0.00",
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.ForeignKeyConstraint(
            ["account_id"], ["accounts.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("account_id"),
        sa.CheckConstraint(
            "ledger_balance >= 0", name="ck_balances_ledger_non_negative"
        ),
        sa.CheckConstraint(
            "available_balance >= 0", name="ck_balances_available_non_negative"
        ),
    )
    op.create_index(op.f("ix_balances_id"), "balances", ["id"], unique=False)

    op.bulk_insert(
        account_types,
        [
            {
                "name": "savings",
                "interest_rate": Decimal("4.00"),
                "minimum_balance": Decimal("500.00"),
                "allows_overdraft": False,
                "is_active": True,
            },
            {
                "name": "current",
                "interest_rate": Decimal("0.00"),
                "minimum_balance": Decimal("0.00"),
                "allows_overdraft": True,
                "is_active": True,
            },
        ],
    )


def downgrade() -> None:
    op.drop_table("balances")
    op.drop_table("accounts")
    op.drop_table("account_types")
    postgresql.ENUM(name="account_status", create_type=False).drop(
        op.get_bind(), checkfirst=True
    )
    postgresql.ENUM(name="approval_status", create_type=False).drop(
        op.get_bind(), checkfirst=True
    )
