from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, func

from models.base import Base


class CardRow(Base):
    __tablename__ = "cards"

    id = Column(Integer, primary_key=True, index=True)
    account_id = Column(Integer, ForeignKey("accounts.id"), nullable=True)
    card_number = Column(String(50), nullable=True)
    expiry_date = Column(DateTime(timezone=True), nullable=True)
    cvc = Column(String(10), nullable=True)
    status = Column(String(20), nullable=True)
    created_at = Column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
