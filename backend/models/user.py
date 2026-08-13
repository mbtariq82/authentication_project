from datetime import date, datetime

from sqlalchemy import (
    Boolean,
    Column,
    Date,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    String,
    func,
)
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

    dob = Column(Date, nullable=True)
    address = Column(String(255), nullable=True)
    photo_document_id = Column(Integer, ForeignKey("documents.id"), nullable=True)
    country = Column(String(100), nullable=True)
    mobile = Column(String(20), nullable=True)

    status = Column(String(20), nullable=False, server_default="pending")  # pending, approved, rejected
    rejection_reason = Column(String(255), nullable=True)
    is_deleted = Column(Boolean, nullable=False, server_default="false")

    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    refresh_tokens = relationship(
        "RefreshToken",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    accounts = relationship(
        "AccountRow",
        back_populates="user",
    )
    photo_document = relationship(
        "DocumentRow",
        foreign_keys=[photo_document_id],
    )