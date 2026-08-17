"""merge profile and main migration heads

Revision ID: d7b3e4f9a102
Revises: a62c9f083d14, c3f6a91d2e47
Create Date: 2026-08-14 13:00:00.000000

"""
from typing import Sequence, Union


# revision identifiers, used by Alembic.
revision: str = "d7b3e4f9a102"
down_revision: Union[str, Sequence[str], None] = (
    "a62c9f083d14",
    "c3f6a91d2e47",
)
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
