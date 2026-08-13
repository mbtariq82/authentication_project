from sqlalchemy import Column, Enum, Integer, String
from sqlalchemy.orm import relationship

from enums import Role
from models.base import Base


class UserRow(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    role = Column(
        Enum(Role, name="role"),
        nullable=False,
        default=Role.USER,
    )
    hashed_password = Column("password_hash", String(255), nullable=True)
    google_subject = Column(String, unique=True, index=True, nullable=True)
    refresh_tokens = relationship(
        "RefreshToken",
        back_populates="user",
        cascade="all, delete-orphan",
    )
