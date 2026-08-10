from sqlalchemy import Boolean, Column, DateTime, Integer, Numeric, String, func
from sqlalchemy.orm import relationship

from models.base import Base

class AccountTypeRow(Base):
    __tablename__ = "account_types"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(20), unique=True, nullable=False)
    interest_rate = Column(Numeric(5, 2), nullable=False, server_default="0.00")
    minimum_balance = Column(
        Numeric(18, 2), nullable=False, server_default="0.00"
    )
    allows_overdraft = Column(Boolean, nullable=False, server_default="false")
    is_active = Column(Boolean, nullable=False, server_default="true")
    created_at = Column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    accounts = relationship("AccountRow", back_populates="account_type")