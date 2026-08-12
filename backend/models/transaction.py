from sqlalchemy import Column, Integer

from models.base import Base


class TransactionRow(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
