from sqlalchemy import Column, Integer, String

from models.base import Base


class DocumentRow(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    document_type = Column(String(50), nullable=True)
    document_url = Column(String(2048), nullable=True)
