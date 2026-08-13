"""add banking schema

Revision ID: d4c96b27e31a
Revises: 7d1210e915c0
Create Date: 2026-08-12 17:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "d4c96b27e31a"
down_revision: Union[str, Sequence[str], None] = "7d1210e915c0"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column(
        "users",
        "hashed_password",
        new_column_name="password_hash",
        existing_type=sa.String(length=255),
        existing_nullable=True,
    )
    op.add_column(
        "users",
        sa.Column(
            "refresh_token",
            sa.Boolean(),
            server_default=sa.false(),
            nullable=False,
        ),
    )

    op.drop_index("ix_refresh_tokens_id", table_name="refresh_tokens")
    op.drop_index("ix_refresh_tokens_token", table_name="refresh_tokens")
    op.drop_constraint(
        "refresh_tokens_pkey",
        "refresh_tokens",
        type_="primary",
    )
    op.drop_column("refresh_tokens", "id")
    op.create_primary_key(
        "refresh_tokens_pkey",
        "refresh_tokens",
        ["token"],
    )

    op.create_table(
        "documents",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("document_type", sa.String(length=50), nullable=True),
        sa.Column("document_url", sa.String(length=2048), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_documents_id", "documents", ["id"])

    op.add_column(
        "accounts",
        sa.Column("document_id", sa.Integer(), nullable=True),
    )
    op.add_column(
        "accounts",
        sa.Column("sort_code", sa.String(length=20), nullable=True),
    )
    op.add_column(
        "accounts",
        sa.Column("account_number", sa.String(length=50), nullable=True),
    )
    op.add_column(
        "accounts",
        sa.Column("account_status", sa.String(length=20), nullable=True),
    )
    op.alter_column(
        "accounts",
        "created_at",
        new_column_name="opened_at",
        existing_type=sa.DateTime(timezone=True),
        existing_nullable=False,
    )
    op.add_column(
        "accounts",
        sa.Column("closed_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_foreign_key(
        "accounts_document_id_fkey",
        "accounts",
        "documents",
        ["document_id"],
        ["id"],
    )
    op.create_unique_constraint(
        "accounts_account_number_key",
        "accounts",
        ["account_number"],
    )

    op.create_table(
        "loans",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("account_id", sa.Integer(), nullable=True),
        sa.Column("document_id", sa.Integer(), nullable=True),
        sa.Column("loan_amount", sa.Integer(), nullable=True),
        sa.Column("duration", sa.Integer(), nullable=True),
        sa.Column("current_loan_status", sa.String(length=50), nullable=True),
        sa.Column("loan_type", sa.String(length=50), nullable=True),
        sa.Column("interest", sa.Integer(), nullable=True),
        sa.Column("emi", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(["account_id"], ["accounts.id"]),
        sa.ForeignKeyConstraint(["document_id"], ["documents.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_loans_id", "loans", ["id"])

    op.create_table(
        "cards",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("account_id", sa.Integer(), nullable=True),
        sa.Column("card_number", sa.String(length=50), nullable=True),
        sa.Column("expiry_date", sa.DateTime(timezone=True), nullable=True),
        sa.Column("cvc", sa.String(length=10), nullable=True),
        sa.Column("status", sa.String(length=20), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["account_id"], ["accounts.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_cards_id", "cards", ["id"])

    op.create_table(
        "transactions",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_transactions_id", "transactions", ["id"])


def downgrade() -> None:
    op.drop_index("ix_transactions_id", table_name="transactions")
    op.drop_table("transactions")

    op.drop_index("ix_cards_id", table_name="cards")
    op.drop_table("cards")

    op.drop_index("ix_loans_id", table_name="loans")
    op.drop_table("loans")

    op.drop_constraint(
        "accounts_account_number_key",
        "accounts",
        type_="unique",
    )
    op.drop_constraint(
        "accounts_document_id_fkey",
        "accounts",
        type_="foreignkey",
    )
    op.drop_column("accounts", "closed_at")
    op.alter_column(
        "accounts",
        "opened_at",
        new_column_name="created_at",
        existing_type=sa.DateTime(timezone=True),
        existing_nullable=False,
    )
    op.drop_column("accounts", "account_status")
    op.drop_column("accounts", "account_number")
    op.drop_column("accounts", "sort_code")
    op.drop_column("accounts", "document_id")

    op.drop_index("ix_documents_id", table_name="documents")
    op.drop_table("documents")

    op.drop_constraint(
        "refresh_tokens_pkey",
        "refresh_tokens",
        type_="primary",
    )
    op.add_column(
        "refresh_tokens",
        sa.Column(
            "id",
            sa.Integer(),
            sa.Identity(),
            nullable=False,
        ),
    )
    op.create_primary_key(
        "refresh_tokens_pkey",
        "refresh_tokens",
        ["id"],
    )
    op.create_index(
        "ix_refresh_tokens_token",
        "refresh_tokens",
        ["token"],
        unique=True,
    )
    op.create_index(
        "ix_refresh_tokens_id",
        "refresh_tokens",
        ["id"],
    )

    op.drop_column("users", "refresh_token")
    op.alter_column(
        "users",
        "password_hash",
        new_column_name="hashed_password",
        existing_type=sa.String(length=255),
        existing_nullable=True,
    )
