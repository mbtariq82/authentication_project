"""reconcile banking schema

Revision ID: f18b7a42c6d1
Revises: e784ab294c06
Create Date: 2026-08-13 15:00:00.000000

This compatibility migration repairs databases that applied the original
version of d4c96b27e31a before that revision was corrected on this branch.
On a fresh database, the canonical d4c96b27e31a migration already produces
the desired schema, so these operations are intentionally conditional.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.engine import Connection


# revision identifiers, used by Alembic.
revision: str = "f18b7a42c6d1"
down_revision: Union[str, Sequence[str], None] = "e784ab294c06"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _column_names(connection: Connection, table_name: str) -> set[str]:
    return {
        column["name"]
        for column in sa.inspect(connection).get_columns(table_name)
    }


def _has_unique_constraint(
    connection: Connection,
    table_name: str,
    column_names: list[str],
) -> bool:
    return any(
        constraint["column_names"] == column_names
        for constraint in sa.inspect(connection).get_unique_constraints(
            table_name
        )
    )


def _foreign_keys_for_column(
    connection: Connection,
    table_name: str,
    column_name: str,
) -> list[str]:
    return [
        foreign_key["name"]
        for foreign_key in sa.inspect(connection).get_foreign_keys(table_name)
        if foreign_key["constrained_columns"] == [column_name]
        and foreign_key["name"] is not None
    ]


def upgrade() -> None:
    connection = op.get_bind()

    if "google_subject" not in _column_names(connection, "users"):
        op.add_column(
            "users",
            sa.Column("google_subject", sa.String(), nullable=True),
        )

    google_indexes = {
        index["name"]
        for index in sa.inspect(connection).get_indexes("users")
    }
    if "ix_users_google_subject" not in google_indexes:
        op.create_index(
            "ix_users_google_subject",
            "users",
            ["google_subject"],
            unique=True,
        )

    if not _has_unique_constraint(
        connection,
        "accounts",
        ["user_id"],
    ):
        duplicate_user_id = connection.execute(
            sa.text(
                """
                SELECT user_id
                FROM accounts
                GROUP BY user_id
                HAVING COUNT(*) > 1
                LIMIT 1
                """
            )
        ).scalar_one_or_none()
        if duplicate_user_id is not None:
            raise RuntimeError(
                "Cannot enforce one account per user: "
                f"user {duplicate_user_id} has multiple accounts"
            )
        op.create_unique_constraint(
            "accounts_user_id_key",
            "accounts",
            ["user_id"],
        )

    account_columns = _column_names(connection, "accounts")
    loan_columns = _column_names(connection, "loans")

    if "account_id" not in loan_columns:
        op.add_column(
            "loans",
            sa.Column("account_id", sa.Integer(), nullable=True),
        )

    if "loan_id" in account_columns:
        shared_loan_id = connection.execute(
            sa.text(
                """
                SELECT loan_id
                FROM accounts
                WHERE loan_id IS NOT NULL
                GROUP BY loan_id
                HAVING COUNT(*) > 1
                LIMIT 1
                """
            )
        ).scalar_one_or_none()
        if shared_loan_id is not None:
            raise RuntimeError(
                "Cannot assign each loan to one account: "
                f"loan {shared_loan_id} is linked to multiple accounts"
            )

        connection.execute(
            sa.text(
                """
                UPDATE loans AS loan
                SET account_id = account.id
                FROM accounts AS account
                WHERE account.loan_id = loan.id
                """
            )
        )

    if not _foreign_keys_for_column(
        connection,
        "loans",
        "account_id",
    ):
        op.create_foreign_key(
            "loans_account_id_fkey",
            "loans",
            "accounts",
            ["account_id"],
            ["id"],
        )

    if "loan_id" in account_columns:
        for constraint_name in _foreign_keys_for_column(
            connection,
            "accounts",
            "loan_id",
        ):
            op.drop_constraint(
                constraint_name,
                "accounts",
                type_="foreignkey",
            )
        op.drop_column("accounts", "loan_id")

    if "account_number" in loan_columns:
        for constraint in sa.inspect(connection).get_unique_constraints(
            "loans"
        ):
            if constraint["column_names"] == ["account_number"]:
                op.drop_constraint(
                    constraint["name"],
                    "loans",
                    type_="unique",
                )
        op.drop_column("loans", "account_number")


def downgrade() -> None:
    # This revision reconciles already-applied copies of d4c96b27e31a with
    # its canonical schema. Keeping that schema here allows the corrected
    # d4c96b27e31a downgrade to run safely afterward.
    pass
