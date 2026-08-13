from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    func,
)
from sqlalchemy.orm import relationship

from models.base import Base


class AccountRow(Base):
    __tablename__ = "accounts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False,
        unique=True,
    )
    document_id = Column(Integer, ForeignKey("documents.id"), nullable=True)

    sort_code = Column(String(20), nullable=True)
    branch = Column(String(100), nullable=True)
    account_type = Column(String(20), nullable=False, server_default="savings")  # savings, current
    account_number = Column(String(50), unique=True, nullable=True)

    balance = Column(
        Numeric(18, 2),
        nullable=False,
        server_default="0.00",
    )
    account_status = Column(
        String(20), nullable=False, server_default="pending"
    )  # approved, reject, closed, frozen, pending

    is_deleted = Column(Boolean, nullable=False, server_default="false")
    close_reason = Column(String(255), nullable=True)

    opened_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    closed_at = Column(DateTime(timezone=True), nullable=True)

    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    user = relationship("UserRow", back_populates="accounts")