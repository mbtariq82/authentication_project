from sqlalchemy import Column, ForeignKey, Integer, String, Numeric
from models.base import Base


class LoanRow(Base):
    __tablename__ = "loans"

    id = Column(Integer, primary_key=True, index=True)
    account_id = Column(Integer, ForeignKey("accounts.id"), nullable=True)
    document_id = Column(Integer, ForeignKey("documents.id"), nullable=True)
    loan_amount = Column(Numeric(12, 2), nullable=True)
    duration = Column(Integer, nullable=True)
    current_loan_status = Column(String(50), nullable=True)
    loan_type = Column(String(50), nullable=True)
    interest = Column(Integer, nullable=True)
    emi = Column(Numeric(12, 2), nullable=True)
