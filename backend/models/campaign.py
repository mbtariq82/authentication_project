import enum

from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    DateTime,
    Enum,
    ForeignKey,
)
from sqlalchemy.sql import func

from models.base import Base


class CampaignStatus(str, enum.Enum):
    DRAFT = "DRAFT"
    PENDING_APPROVAL = "PENDING_APPROVAL"
    APPROVED = "APPROVED"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    REJECTED = "REJECTED"
    FAILED = "FAILED"


class CampaignType(str, enum.Enum):
    EMAIL = "EMAIL"
    INSTAGRAM = "INSTAGRAM"
    EMAIL_AND_INSTAGRAM = "EMAIL_AND_INSTAGRAM"


class CampaignRow(Base):
    __tablename__ = "campaigns"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    # -----------------------------
    # Campaign information
    # -----------------------------

    name = Column(
        String(255),
        nullable=False,
    )

    occasion = Column(
        String(100),
        nullable=True,
    )

    campaign_type = Column(
        Enum(CampaignType),
        nullable=False,
    )

    # -----------------------------
    # Audience
    # -----------------------------

    audience_description = Column(
        Text,
        nullable=True,
    )

    audience_query = Column(
        Text,
        nullable=True,
    )

    recipient_count = Column(
        Integer,
        nullable=True,
    )

    # -----------------------------
    # Email
    # -----------------------------

    email_subject = Column(
        String(255),
        nullable=True,
    )

    email_body = Column(
        Text,
        nullable=True,
    )

    # -----------------------------
    # Instagram
    # -----------------------------

    instagram_caption = Column(
        Text,
        nullable=True,
    )

    instagram_image_prompt = Column(
        Text,
        nullable=True,
    )

    instagram_image_url = Column(
        Text,
        nullable=True,
    )

    instagram_post_id = Column(
        String(255),
        nullable=True,
    )

    # -----------------------------
    # Approval
    # -----------------------------

    status = Column(
        Enum(CampaignStatus),
        nullable=False,
        default=CampaignStatus.DRAFT,
    )

    rejection_reason = Column(
        Text,
        nullable=True,
    )

    # -----------------------------
    # Admin information
    # -----------------------------

    created_by = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
    )

    approved_by = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=True,
    )

    # -----------------------------
    # Timestamps
    # -----------------------------

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    approved_at = Column(
        DateTime(timezone=True),
        nullable=True,
    )

    executed_at = Column(
        DateTime(timezone=True),
        nullable=True,
    )