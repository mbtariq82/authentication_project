from sqlalchemy import (
    CheckConstraint,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    UniqueConstraint,
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
    balance = Column(
        Numeric(18, 2),
        nullable=False,
        server_default="0.00",
    )
    created_at = Column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
