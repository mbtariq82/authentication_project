from sqlalchemy import Column, DateTime, Enum, ForeignKey, Integer, String
from sqlalchemy.orm import relationship, DeclarativeBase

from enums import Role, PlacementStatus, Batch

class Base(DeclarativeBase):
    pass

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
    hashed_password = Column(String(255), nullable=True)
    google_subject = Column(String, unique=True, index=True, nullable=True)
    refresh_tokens = relationship(
        "RefreshToken",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    consultant = relationship(
        "ConsultantRow",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan",
    )

class ConsultantRow(Base):
    __tablename__ = "consultants"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        unique=True,
        nullable=False,
    )
    batch = Column(
        Enum(Batch, name="batch"),
        nullable=True,
    )
    placement_status = Column(
        Enum(PlacementStatus, name="placement_status"),
        nullable=False,
        default=PlacementStatus.ONBOARDING,
    )
    client = Column(String(100), nullable=True)
    user = relationship(
        "UserRow",
        back_populates="consultant",
    )

class RefreshToken(Base):
    __tablename__ = "refresh_tokens"
    id = Column(Integer, primary_key=True, index=True)
    token = Column(String(512), unique=True, index=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    user = relationship("UserRow", back_populates="refresh_tokens")