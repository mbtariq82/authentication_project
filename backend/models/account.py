from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    func,
)

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
    account_number = Column(String(50), unique=True, nullable=True)
    balance = Column(
        Numeric(18, 2),
        nullable=False,
        server_default="0.00",
    )
    account_status = Column(String(20), nullable=True)
    opened_at = Column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    closed_at = Column(DateTime(timezone=True), nullable=True)
