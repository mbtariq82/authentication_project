from sqlalchemy import (
    CheckConstraint,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    func,
)
from sqlalchemy.orm import relationship

from models.base import Base


class BalanceRow(Base):
    __tablename__ = "balances"

    id = Column(Integer, primary_key=True, index=True)
    account_id = Column(
        Integer,
        ForeignKey("accounts.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
    )
    ledger_balance = Column(
        Numeric(18, 2), nullable=False, server_default="0.00"
    )
    available_balance = Column(
        Numeric(18, 2), nullable=False, server_default="0.00"
    )
    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    account = relationship("AccountRow", back_populates="balance")

    __table_args__ = (
        CheckConstraint(
            "ledger_balance >= 0", name="ck_balances_ledger_non_negative"
        ),
        CheckConstraint(
            "available_balance >= 0", name="ck_balances_available_non_negative"
        ),
    )