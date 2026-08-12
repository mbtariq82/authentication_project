from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from models.base import Base


class RefreshToken(Base):
    __tablename__ = "refresh_tokens"

    token = Column(String(512), primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    user = relationship("UserRow", back_populates="refresh_tokens")
