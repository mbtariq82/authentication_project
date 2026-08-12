from sqlalchemy import Column, ForeignKey, Integer, String

from models.base import Base


class LoanRow(Base):
    __tablename__ = "loans"

    id = Column(Integer, primary_key=True, index=True)
    account_number = Column(String(50), unique=True, nullable=True)
    document_id = Column(Integer, ForeignKey("documents.id"), nullable=True)
    loan_amount = Column(Integer, nullable=True)
    duration = Column(Integer, nullable=True)
    current_loan_status = Column(String(50), nullable=True)
    loan_type = Column(String(50), nullable=True)
    interest = Column(Integer, nullable=True)
    emi = Column(Integer, nullable=True)
