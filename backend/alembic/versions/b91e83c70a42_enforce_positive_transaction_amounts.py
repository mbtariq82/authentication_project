"""enforce positive transaction amounts

Revision ID: b91e83c70a42
Revises: g7h8i9j0k1l2
Create Date: 2026-08-13 17:00:00.000000

"""
from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = "b91e83c70a42"
down_revision: Union[str, Sequence[str], None] = "g7h8i9j0k1l2"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_check_constraint(
        "ck_transactions_amount_positive",
        "transactions",
        "amount > 0",
    )


def downgrade() -> None:
    op.drop_constraint(
        "ck_transactions_amount_positive",
        "transactions",
        type_="check",
    )
