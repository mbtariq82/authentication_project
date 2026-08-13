from sqlalchemy import (
    CheckConstraint,
    Column,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB

from enums import TransactionDirection, TransactionStatus, TransactionType
from models.base import Base


class TransactionRow(Base):
    __tablename__ = "transactions"
    __table_args__ = (
        CheckConstraint(
            "amount > 0",
            name="ck_transactions_amount_positive",
        ),
    )

    id = Column(Integer, primary_key=True)
    account_id = Column(
        Integer,
        ForeignKey("accounts.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    beneficiary_id = Column(
        Integer,
        ForeignKey("beneficiaries.id", ondelete="RESTRICT"),
        nullable=True,
        index=True,
    )
    transaction_type = Column(
        Enum(TransactionType, name="transaction_type"),
        nullable=False,
    )
    direction = Column(
        Enum(TransactionDirection, name="transaction_direction"),
        nullable=False,
    )
    amount = Column(Numeric(18, 2), nullable=False)
    status = Column(
        Enum(TransactionStatus, name="transaction_status"),
        nullable=False,
        server_default=TransactionStatus.PENDING.value,
        index=True,
    )
    reference = Column(String(100), nullable=False, unique=True)
    transfer_reference = Column(String(100), nullable=True, index=True)
    description = Column(String(255), nullable=True)
    created_at = Column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), index=True
    )
    updated_at = Column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )


class TransactionLogRow(Base):
    __tablename__ = "transaction_logs"

    id = Column(Integer, primary_key=True)
    transaction_id = Column(
        Integer,
        ForeignKey("transactions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    action = Column(String(100), nullable=False)
    status = Column(String(50), nullable=False)
    message = Column(Text, nullable=True)
    metadata_json = Column("metadata", JSONB, nullable=True)
    created_at = Column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), index=True
    )
