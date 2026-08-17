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
    google_subject = Column(String, unique=True, index=True, nullable=True)
    profile_image_key = Column(String(512), nullable=True)

    user_status = Column(
        String(20),
        nullable=False,
        server_default="PENDING",
    )

    dob = Column(Date, nullable=True)
    address_line = Column(String(255), nullable=True)

    city = Column(String(100), nullable=True)
    county = Column(String(100), nullable=True)
    postcode = Column(String(20), nullable=True)
    mobile = Column(String(20), nullable=True)

    rejection_reason = Column(String(255), nullable=True)
    is_deleted = Column(Boolean, nullable=False, server_default="false")

    refresh_tokens = relationship(
        "RefreshToken",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    accounts = relationship(
        "AccountRow",
        back_populates="user",
    )
