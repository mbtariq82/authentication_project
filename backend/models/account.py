from sqlalchemy import (
    Column,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import relationship

from enums import AccountStatus, ApprovalStatus
from models.base import Base


class AccountRow(Base):
    __tablename__ = "accounts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    account_type_id = Column(
        Integer,
        ForeignKey("account_types.id", ondelete="RESTRICT"),
        nullable=False,
    )
    account_number = Column(String(20), unique=True, index=True, nullable=True)
    admin_approved = Column(
        Enum(ApprovalStatus, name="approval_status"),
        nullable=False,
        default=ApprovalStatus.PENDING,
    )
    status = Column(
        Enum(AccountStatus, name="account_status"),
        nullable=False,
        default=AccountStatus.ACTIVE,
    )
    approved_by = Column(
        Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    approved_at = Column(DateTime(timezone=True), nullable=True)
    rejection_reason = Column(Text, nullable=True)
    created_at = Column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    closed_at = Column(DateTime(timezone=True), nullable=True)

    account_type = relationship("AccountTypeRow", back_populates="accounts")
    balance = relationship(
        "BalanceRow",
        back_populates="account",
        uselist=False,
        cascade="all, delete-orphan",
    )

    __table_args__ = (
        UniqueConstraint(
            "user_id", "account_type_id", name="uq_accounts_user_type"
        ),
    )