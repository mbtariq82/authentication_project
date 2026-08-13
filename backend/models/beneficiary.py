from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, func

from models.base import Base


class BeneficiaryRow(Base):
    __tablename__ = "beneficiaries"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    name = Column(String(150), nullable=False)
    account_number = Column(String(50), nullable=False, index=True)
    sort_code = Column(String(20), nullable=False, index=True)
    bank_name = Column(String(150), nullable=False)
    reference = Column(String(255), nullable=True)
    is_active = Column(Boolean, nullable=False, server_default="true")
    created_at = Column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at = Column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )